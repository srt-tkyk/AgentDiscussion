"""Persona domain service — validation and lifecycle management."""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from agent_discussion.core.models import Persona, ValidationResult
from agent_discussion.personas.manager import PersonaManager

logger = logging.getLogger(__name__)


class PersonaService:
    """Business logic for persona selection and creation."""

    def __init__(self, manager: PersonaManager) -> None:
        self._manager = manager

    def get_all_personas(self) -> List[Persona]:
        """Return predefined personas followed by custom ones."""
        return self._manager.get_predefined_personas() + self._manager.get_custom_personas()

    def validate_selection(self, persona_ids: List[str]) -> ValidationResult:
        """Validate a list of selected persona IDs against business rules."""
        errors: List[str] = []
        warnings: List[str] = []

        if len(persona_ids) < 2:
            errors.append("Select at least 2 personas to start a discussion.")
        if len(persona_ids) > 6:
            errors.append("Maximum 6 personas allowed per discussion.")
        if len(persona_ids) != len(set(persona_ids)):
            errors.append(
                "Duplicate personas detected. Each persona can only be selected once."
            )

        if not errors:
            personas = [
                self._manager.get_persona_by_id(pid) for pid in persona_ids
            ]
            personas = [p for p in personas if p]
            # Soft rule: diversity check
            if len({p.description[:30] for p in personas}) == 1:
                warnings.append(
                    "Consider adding personas with different expertise for a richer discussion."
                )

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def create_custom_persona(
        self, name: str, description: str
    ) -> Tuple[Optional[Persona], ValidationResult]:
        """Validate and create a custom persona."""
        errors: List[str] = []
        if not name or not name.strip():
            errors.append("Persona name is required.")
        elif len(name) > 100:
            errors.append("Persona name must be 100 characters or fewer.")
        if not description or not description.strip():
            errors.append("Persona description is required.")
        elif len(description) > 500:
            errors.append("Persona description must be 500 characters or fewer.")

        if errors:
            return None, ValidationResult(valid=False, errors=errors)

        persona = self._manager.create_custom_persona(name.strip(), description.strip())
        return persona, ValidationResult(valid=True)

    def delete_custom_persona(self, persona_id: str) -> None:
        """Remove a custom persona."""
        self._manager.delete_custom_persona(persona_id)
