"""Discussion workflow orchestration."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Generator, List, Optional

from agent_discussion.core.models import (
    Discussion,
    DiscussionParameters,
    DiscussionSummary,
    Message,
    ValidationResult,
)

if TYPE_CHECKING:
    from agent_discussion.core.config import ConfigurationManager
    from agent_discussion.core.files import FileManager
    from agent_discussion.core.resume_manager import ResumeManager
    from agent_discussion.discussions.engine import DiscussionEngine
    from agent_discussion.personas.service import PersonaService

logger = logging.getLogger(__name__)

# Valid workflow state transitions
_VALID_TRANSITIONS: dict[str, list[str]] = {
    "setup": ["configuring"],
    "configuring": ["executing"],
    "executing": ["completed"],
    "completed": ["exported", "configuring"],
    "exported": ["configuring"],
}


class DiscussionService:
    """Manages the discussion lifecycle: setup, execution, history, and export."""

    def __init__(
        self,
        file_manager: "FileManager",
        persona_service: "PersonaService",
        resume_manager: "ResumeManager",
        engine: "DiscussionEngine",
    ) -> None:
        self._fm = file_manager
        self._personas = persona_service
        self._resume = resume_manager
        self._engine = engine

    # --- Setup ---

    def setup_discussion(
        self,
        topic: str,
        persona_ids: List[str],
        parameters: DiscussionParameters,
        materials_bytes: Optional[bytes] = None,
        materials_filename: Optional[str] = None,
    ) -> tuple:  # (Discussion | None, ValidationResult)
        """Validate inputs and create a new Discussion.

        Returns:
            Tuple of (Discussion or None, ValidationResult).
        """
        errors: List[str] = []

        if not topic or not topic.strip():
            errors.append("Discussion topic is required.")
        elif len(topic) > 500:
            errors.append("Topic must be between 1 and 500 characters.")

        persona_validation = self._personas.validate_selection(persona_ids)
        errors.extend(persona_validation.errors)

        if errors:
            return None, ValidationResult(
                valid=False, errors=errors, warnings=persona_validation.warnings
            )

        personas = [
            self._personas._manager.get_persona_by_id(pid) for pid in persona_ids
        ]
        personas = [p for p in personas if p]

        materials_context: Optional[str] = None
        if materials_bytes and materials_filename:
            try:
                raw_text = self._fm.extract_text(materials_bytes, materials_filename)
                # Cap context size; AI preprocessing is handled by DiscussionEngine prompts
                materials_context = raw_text[:8000]
            except Exception as e:
                logger.warning("Materials extraction failed: %s", e)

        now = datetime.now()
        discussion = Discussion(
            id=str(uuid.uuid4()),
            topic=topic.strip(),
            personas=personas,
            messages=[],
            parameters=parameters,
            state="configuring",
            created_at=now,
            updated_at=now,
            materials_context=materials_context,
        )
        self._fm.save_discussion(discussion)
        logger.info("Discussion %s created: %s", discussion.id, topic)
        return discussion, ValidationResult(valid=True, warnings=persona_validation.warnings)

    # --- Execution ---

    def execute_discussion(
        self,
        discussion: Discussion,
        on_chunk: Callable[[str, str], None],
        on_message_complete: Callable[[Message], None],
        should_stop: Callable[[], bool],
    ) -> Discussion:
        """Run the turn-based discussion loop.

        Args:
            discussion: The active Discussion object.
            on_chunk: Called with (persona_name, chunk) for each streaming chunk.
            on_message_complete: Called with the completed Message after each turn.
            should_stop: Returns True if the user has requested an early stop.
        """
        discussion.state = "executing"
        self._fm.save_discussion(discussion)

        start_turn = 1
        start_persona_idx = 0
        if discussion.resume_point:
            start_turn = discussion.resume_point["failed_turn"]
            start_persona_idx = discussion.resume_point["failed_persona_index"]
            self._resume.clear_resume_point(discussion)

        for turn in range(start_turn, discussion.parameters.max_turns + 1):
            for idx, persona in enumerate(discussion.personas):
                # Skip already-completed steps when resuming
                if turn == start_turn and idx < start_persona_idx:
                    continue

                if should_stop():
                    discussion.state = "completed"
                    discussion.updated_at = datetime.now()
                    self._fm.save_discussion(discussion)
                    logger.info("Discussion %s stopped by user at turn %d", discussion.id, turn)
                    return discussion

                try:
                    context = self._build_context(discussion)
                    full_content = ""
                    for chunk in self._engine.stream_response(persona, context):
                        on_chunk(persona.name, chunk)
                        full_content += chunk

                    msg = Message(
                        id=str(uuid.uuid4()),
                        persona_id=persona.id,
                        persona_name=persona.name,
                        content=full_content,
                        turn_number=turn,
                        timestamp=datetime.now(),
                    )
                    discussion.messages.append(msg)
                    discussion.updated_at = datetime.now()
                    self._fm.save_discussion(discussion)
                    on_message_complete(msg)

                except Exception as e:
                    logger.error(
                        "API failure at turn %d, persona %s: %s",
                        turn,
                        persona.id,
                        e,
                    )
                    self._resume.set_resume_point(
                        discussion, turn=turn, persona_index=idx, error=str(e)
                    )
                    raise

        discussion.state = "completed"
        discussion.updated_at = datetime.now()
        self._fm.save_discussion(discussion)
        logger.info("Discussion %s completed (%d turns)", discussion.id, discussion.parameters.max_turns)
        return discussion

    # --- History ---

    def load_discussion_history(self) -> List[DiscussionSummary]:
        """Return a list of past discussion summaries."""
        return self._fm.list_discussions()

    def load_discussion(self, discussion_id: str) -> Optional[Discussion]:
        """Load a full discussion by ID."""
        return self._fm.load_discussion(discussion_id)

    # --- Helpers ---

    def _build_context(self, discussion: Discussion) -> dict:
        return {
            "topic": discussion.topic,
            "style": discussion.parameters.discussion_style,
            "language": discussion.parameters.language,
            "materials": discussion.materials_context,
            "history": [
                {
                    "persona": m.persona_name,
                    "content": m.content,
                    "turn": m.turn_number,
                }
                for m in discussion.messages
            ],
        }
