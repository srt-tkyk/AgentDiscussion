"""Centralized file operations — all disk I/O goes through FileManager."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from agent_discussion.core.models import (
    Discussion,
    DiscussionParameters,
    DiscussionSummary,
    Message,
    Persona,
)

logger = logging.getLogger(__name__)

_DT_FMT = "%Y-%m-%dT%H:%M:%S"


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    return datetime.strptime(s, _DT_FMT) if s else None


def _fmt_dt(dt: Optional[datetime]) -> Optional[str]:
    return dt.strftime(_DT_FMT) if dt else None


class FileManager:
    """Handles all file I/O for discussions, personas, and exports."""

    def __init__(self, config) -> None:
        self._discussions = Path(
            config.get("paths", "discussions_dir", default="data/discussions")
        )
        self._personas = Path(
            config.get("paths", "personas_dir", default="data/personas")
        )
        self._exports = Path(
            config.get("paths", "exports_dir", default="exports")
        )
        for d in (self._discussions, self._personas / "custom", self._exports):
            d.mkdir(parents=True, exist_ok=True)

    # --- Discussions ---

    def save_discussion(self, discussion: Discussion) -> None:
        """Persist discussion to JSON. Non-blocking on error."""
        path = self._discussions / f"{discussion.id}.json"
        try:
            path.write_text(
                json.dumps(
                    self._discussion_to_dict(discussion),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            logger.debug("Saved discussion %s", discussion.id)
        except OSError as e:
            logger.error("Failed to save discussion %s: %s", discussion.id, e)

    def load_discussion(self, discussion_id: str) -> Optional[Discussion]:
        """Load a discussion from JSON by ID."""
        path = self._discussions / f"{discussion_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._dict_to_discussion(data)
        except Exception as e:
            logger.error("Failed to load discussion %s: %s", discussion_id, e)
            return None

    def list_discussions(self) -> List[DiscussionSummary]:
        """Return lightweight summaries sorted by modification time (newest first)."""
        summaries: List[DiscussionSummary] = []
        for p in sorted(
            self._discussions.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        ):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                summaries.append(
                    DiscussionSummary(
                        id=data["id"],
                        topic=data["topic"],
                        persona_names=[pe["name"] for pe in data.get("personas", [])],
                        turn_count=max(
                            (m["turn_number"] for m in data.get("messages", [])),
                            default=0,
                        ),
                        state=data.get("state", "completed"),
                        created_at=_parse_dt(data.get("created_at")),
                        updated_at=_parse_dt(data.get("updated_at")),
                    )
                )
            except Exception as e:
                logger.warning("Skipping malformed discussion file %s: %s", p.name, e)
        return summaries

    # --- Personas ---

    def save_custom_persona(self, persona: Persona) -> None:
        """Persist a custom persona to its own JSON file."""
        path = self._personas / "custom" / f"{persona.id}.json"
        path.write_text(
            json.dumps(
                {
                    "id": persona.id,
                    "name": persona.name,
                    "description": persona.description,
                    "type": "custom",
                    "created_at": _fmt_dt(persona.created_at),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def load_custom_personas(self) -> List[Persona]:
        """Load all custom persona files."""
        personas: List[Persona] = []
        for p in (self._personas / "custom").glob("*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                personas.append(
                    Persona(
                        id=d["id"],
                        name=d["name"],
                        description=d["description"],
                        type="custom",
                        created_at=_parse_dt(d.get("created_at")),
                    )
                )
            except Exception as e:
                logger.warning("Skipping malformed persona file %s: %s", p.name, e)
        return personas

    def delete_custom_persona(self, persona_id: str) -> None:
        """Remove a custom persona file."""
        path = self._personas / "custom" / f"{persona_id}.json"
        if path.exists():
            path.unlink()

    def load_predefined_personas(self) -> List[Persona]:
        """Load built-in personas from predefined.json."""
        path = self._personas / "predefined.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return [
                Persona(
                    id=d["id"],
                    name=d["name"],
                    description=d["description"],
                    type="predefined",
                )
                for d in data
            ]
        except Exception as e:
            logger.error("Failed to load predefined personas: %s", e)
            return []

    # --- Materials ---

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """Extract plain text from an uploaded file."""
        suffix = Path(filename).suffix.lower()
        try:
            if suffix in (".txt", ".md"):
                return file_bytes.decode("utf-8", errors="replace")
            elif suffix == ".pdf":
                import fitz  # type: ignore  # noqa: PLC0415

                doc = fitz.open(stream=file_bytes, filetype="pdf")
                return "\n".join(page.get_text() for page in doc)
            elif suffix == ".docx":
                import io  # noqa: PLC0415
                from docx import Document  # type: ignore  # noqa: PLC0415

                doc = Document(io.BytesIO(file_bytes))
                return "\n".join(p.text for p in doc.paragraphs)
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
        except Exception as e:
            logger.error("Text extraction failed for %s: %s", filename, e)
            raise

    # --- Serialization helpers ---

    def _discussion_to_dict(self, d: Discussion) -> dict:
        return {
            "id": d.id,
            "topic": d.topic,
            "state": d.state,
            "materials_context": d.materials_context,
            "resume_point": d.resume_point,
            "created_at": _fmt_dt(d.created_at),
            "updated_at": _fmt_dt(d.updated_at),
            "parameters": {
                "max_turns": d.parameters.max_turns,
                "language": d.parameters.language,
                "discussion_style": d.parameters.discussion_style,
                "extended_turns": d.parameters.extended_turns,
            },
            "personas": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "type": p.type,
                }
                for p in d.personas
            ],
            "messages": [
                {
                    "id": m.id,
                    "persona_id": m.persona_id,
                    "persona_name": m.persona_name,
                    "content": m.content,
                    "turn_number": m.turn_number,
                    "timestamp": _fmt_dt(m.timestamp),
                }
                for m in d.messages
            ],
        }

    def _dict_to_discussion(self, data: dict) -> Discussion:
        params = data.get("parameters", {})
        return Discussion(
            id=data["id"],
            topic=data["topic"],
            state=data.get("state", "completed"),
            materials_context=data.get("materials_context"),
            resume_point=data.get("resume_point"),
            created_at=_parse_dt(data.get("created_at")),
            updated_at=_parse_dt(data.get("updated_at")),
            parameters=DiscussionParameters(
                max_turns=params.get("max_turns", 3),
                language=params.get("language", "en"),
                discussion_style=params.get("discussion_style", "formal"),
                extended_turns=params.get("extended_turns", 1),
            ),
            personas=[
                Persona(
                    id=p["id"],
                    name=p["name"],
                    description=p["description"],
                    type=p["type"],
                )
                for p in data.get("personas", [])
            ],
            messages=[
                Message(
                    id=m["id"],
                    persona_id=m["persona_id"],
                    persona_name=m["persona_name"],
                    content=m["content"],
                    turn_number=m["turn_number"],
                    timestamp=_parse_dt(m.get("timestamp")),
                )
                for m in data.get("messages", [])
            ],
        )
