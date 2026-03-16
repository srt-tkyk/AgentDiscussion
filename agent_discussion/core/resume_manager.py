"""Resume point management for API failure recovery."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import streamlit as st

if TYPE_CHECKING:
    from agent_discussion.core.files import FileManager
    from agent_discussion.core.models import Discussion

logger = logging.getLogger(__name__)

_SESSION_KEY = "resume_point"


class ResumeManager:
    """Manages checkpoint state for resuming a discussion after API failure."""

    def __init__(self, file_manager: "FileManager") -> None:
        self._fm = file_manager

    def set_resume_point(
        self,
        discussion: "Discussion",
        turn: int,
        persona_index: int,
        error: str,
    ) -> None:
        """Persist a resume checkpoint to session state and discussion JSON."""
        point = {
            "failed_turn": turn,
            "failed_persona_index": persona_index,
            "error_message": error,
            "is_resumable": True,
        }
        st.session_state[_SESSION_KEY] = point
        discussion.resume_point = point
        self._fm.save_discussion(discussion)
        logger.error(
            "Resume point set at turn %d, persona index %d: %s",
            turn,
            persona_index,
            error,
        )

    def clear_resume_point(self, discussion: "Discussion") -> None:
        """Remove the resume checkpoint after a successful resume."""
        st.session_state.pop(_SESSION_KEY, None)
        discussion.resume_point = None
        self._fm.save_discussion(discussion)
        logger.info("Resume point cleared for discussion %s", discussion.id)

    def has_resume_point(self) -> bool:
        """Return True if an active resume point exists in session state."""
        return bool(st.session_state.get(_SESSION_KEY, {}).get("is_resumable"))

    def get_resume_point(self) -> Optional[dict]:
        """Return the current resume point dict, or None."""
        return st.session_state.get(_SESSION_KEY)
