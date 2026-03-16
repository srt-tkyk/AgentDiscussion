"""Shared UI helper functions and constants."""
from __future__ import annotations

from typing import List

import streamlit as st

from agent_discussion.core.models import Message

# Session state key constants (avoid magic strings)
KEY_WORKFLOW_STATE = "workflow_state"
KEY_CURRENT_DISCUSSION = "current_discussion"
KEY_SELECTED_PERSONA_IDS = "selected_persona_ids"
KEY_RESUME_POINT = "resume_point"
KEY_API_KEY_VALID = "api_key_valid"
KEY_API_VALIDATION_RESULT = "api_validation_result"
KEY_CONFIG = "config"
KEY_CONFIG_ERROR = "config_error"
KEY_INITIALIZED = "initialized"
KEY_DISCUSSION_SERVICE = "discussion_service"
KEY_PERSONA_SERVICE = "persona_service"
KEY_FILE_MANAGER = "file_manager"
KEY_RESUME_MANAGER = "resume_manager"
KEY_SHOW_TURN_LIMIT_WARNING = "show_turn_limit_warning"
KEY_SHOW_TURN_LIMIT_MODAL = "show_turn_limit_modal"

_AGENT_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def agent_color(index: int) -> str:
    """Return a distinct hex color for an agent at the given index."""
    return _AGENT_COLORS[index % len(_AGENT_COLORS)]


def render_message_card(message: Message, color: str) -> None:
    """Render a persona message as a colored card."""
    st.markdown(
        f'<div style="border-left: 4px solid {color}; padding: 8px 12px; margin: 4px 0;">'
        f'<strong style="color:{color}">{message.persona_name}</strong> '
        f'<span style="font-size:0.8em; color:#888;">Turn {message.turn_number}</span><br>'
        f'{message.content}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_validation_errors(errors: List[str]) -> None:
    """Display each validation error as a Streamlit error message."""
    for e in errors:
        st.error(e)


def render_validation_warnings(warnings: List[str]) -> None:
    """Display each validation warning as a Streamlit warning message."""
    for w in warnings:
        st.warning(w)
