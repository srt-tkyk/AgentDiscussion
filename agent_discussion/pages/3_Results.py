"""Results page — review completed discussion and export meeting minutes."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from agent_discussion.ui.components import (
    KEY_API_KEY_VALID,
    KEY_CONFIG,
    KEY_CURRENT_DISCUSSION,
    KEY_DISCUSSION_SERVICE,
    KEY_RESUME_POINT,
    KEY_SELECTED_PERSONA_IDS,
    KEY_WORKFLOW_STATE,
    agent_color,
    render_message_card,
)

st.set_page_config(page_title="Results", page_icon="📋")
st.title("📋 Results")

if not st.session_state.get(KEY_API_KEY_VALID):
    st.warning("Please complete setup first.")
    st.stop()

discussion = st.session_state.get(KEY_CURRENT_DISCUSSION)
if not discussion:
    st.info("No discussion loaded. Go to History to load a previous discussion.")
    if st.button("Go to History", key="results-go-history"):
        st.switch_page("pages/4_History.py")
    st.stop()

# Resume banner
resume = st.session_state.get(KEY_RESUME_POINT, {})
if resume.get("is_resumable"):
    st.error(
        f"⚠️ Discussion paused at turn {resume['failed_turn']}: "
        f"{resume['error_message']}"
    )
    if st.button("▶ Resume Discussion", key="results-resume"):
        st.switch_page("pages/2_Discussion.py")

# Summary header
st.subheader(f"Topic: {discussion.topic}")
participants = ", ".join(p.name for p in discussion.personas)
turn_count = max((m.turn_number for m in discussion.messages), default=0)
st.caption(
    f"Participants: {participants}  ·  Turns: {turn_count}  ·  State: {discussion.state}"
)
st.divider()

# Transcript
for msg in discussion.messages:
    idx = next(
        (j for j, p in enumerate(discussion.personas) if p.id == msg.persona_id), 0
    )
    render_message_card(msg, agent_color(idx))

st.divider()

col1, col2 = st.columns(2)

with col1:
    can_export = discussion.state in ("completed", "exported")
    if st.button("📥 Export Meeting Minutes", disabled=not can_export, key="export"):
        try:
            config = st.session_state[KEY_CONFIG]
            exports_dir = Path(config.get("paths", "exports_dir", default="exports"))
            exports_dir.mkdir(exist_ok=True)

            slug = "".join(c if c.isalnum() else "_" for c in discussion.topic)[:40]
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = exports_dir / f"{slug}_{date_str}.md"

            lines = [
                "# Meeting Minutes\n",
                f"**Topic**: {discussion.topic}  ",
                f"**Date**: {discussion.created_at}  ",
                f"**Participants**: {participants}  ",
                f"**Turns**: {turn_count}\n",
                "---\n",
                "## Transcript\n",
            ]
            for msg in discussion.messages:
                lines.append(f"### Turn {msg.turn_number} — {msg.persona_name}\n{msg.content}\n")

            content = "\n".join(lines)
            filename.write_text(content, encoding="utf-8")

            discussion.state = "exported"
            st.session_state[KEY_DISCUSSION_SERVICE]._fm.save_discussion(discussion)

            st.success(f"Exported to `{filename}`")
            st.download_button(
                "⬇ Download",
                data=content,
                file_name=filename.name,
                mime="text/markdown",
                key="download-export",
            )
        except Exception as e:
            st.error(f"Export failed: {e}")

with col2:
    if st.button("➕ New Discussion", key="new-discussion"):
        for key in (
            KEY_CURRENT_DISCUSSION,
            KEY_SELECTED_PERSONA_IDS,
            KEY_RESUME_POINT,
        ):
            st.session_state.pop(key, None)
        st.session_state[KEY_WORKFLOW_STATE] = "configuring"
        st.switch_page("pages/2_Discussion.py")
