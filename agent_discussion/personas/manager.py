"""Persona CRUD operations."""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import List, Optional

from agent_discussion.core.files import FileManager
from agent_discussion.core.models import Persona

logger = logging.getLogger(__name__)


def _slugify(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class PersonaManager:
    """Handles CRUD operations for personas via FileManager."""

    def __init__(self, file_manager: FileManager) -> None:
        self._fm = file_manager

    def get_predefined_personas(self) -> List[Persona]:
        """Return built-in personas."""
        return self._fm.load_predefined_personas()

    def get_custom_personas(self) -> List[Persona]:
        """Return user-created custom personas."""
        return self._fm.load_custom_personas()

    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Look up a persona by its ID across predefined and custom lists."""
        all_personas = self.get_predefined_personas() + self.get_custom_personas()
        return next((p for p in all_personas if p.id == persona_id), None)

    def create_custom_persona(self, name: str, description: str) -> Persona:
        """Create and persist a new custom persona with a unique slug ID."""
        base_slug = _slugify(name)
        existing_ids = {p.id for p in self.get_custom_personas()}
        slug = base_slug
        counter = 2
        while slug in existing_ids:
            slug = f"{base_slug}-{counter}"
            counter += 1
        persona = Persona(
            id=slug,
            name=name,
            description=description,
            type="custom",
            created_at=datetime.now(),
        )
        self._fm.save_custom_persona(persona)
        logger.info("Created custom persona: %s", slug)
        return persona

    def delete_custom_persona(self, persona_id: str) -> None:
        """Remove a custom persona by ID."""
        self._fm.delete_custom_persona(persona_id)
        logger.info("Deleted custom persona: %s", persona_id)
