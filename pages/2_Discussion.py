"""Discussion page — configure and run an AI discussion."""
from __future__ import annotations

import streamlit as st

from agent_discussion.core.models import DiscussionParameters
from agent_discussion.ui.components import (
    KEY_API_KEY_VALID,
    KEY_CONFIG,
    KEY_CURRENT_DISCUSSION,
    KEY_DISCUSSION_SERVICE,
    KEY_PERSONA_SERVICE,
    KEY_RESUME_POINT,
    KEY_SELECTED_PERSONA_IDS,
    KEY_SHOW_TURN_LIMIT_MODAL,
    KEY_SHOW_TURN_LIMIT_WARNING,
    KEY_WORKFLOW_STATE,
    agent_color,
    render_message_card,
    render_validation_errors,
    render_validation_warnings,
)

st.set_page_config(page_title="Discussion", page_icon="💬")

# Guard: require valid API key
if not st.session_state.get(KEY_API_KEY_VALID):
    st.warning("Please complete setup first.")
    if st.button("Go to Setup"):
        st.switch_page("pages/1_Setup.py")
    st.stop()

svc = st.session_state[KEY_DISCUSSION_SERVICE]
persona_svc = st.session_state[KEY_PERSONA_SERVICE]
state = st.session_state.get(KEY_WORKFLOW_STATE, "configuring")
is_executing = state == "executing"

st.title("💬 Discussion")

# ──────────────────────────────────────────────────────────────
# Configuration Form (shown before/after execution)
# ──────────────────────────────────────────────────────────────
if state in ("configuring", "setup"):
    st.subheader("Topic")
    topic = st.text_area(
        "Enter discussion topic",
        max_chars=500,
        key="topic_input",
        value=st.session_state.get("topic", ""),
    )

    st.subheader("Personas")
    all_personas = persona_svc.get_all_personas()
    selected_ids: list = list(st.session_state.get(KEY_SELECTED_PERSONA_IDS, []))

    cols = st.columns(3)
    for i, persona in enumerate(all_personas):
        with cols[i % 3]:
            checked = persona.id in selected_ids
            new_checked = st.checkbox(
                f"**{persona.name}**\n\n{persona.description[:80]}…",
                value=checked,
                key=f"persona_{persona.id}",
            )
            if new_checked and persona.id not in selected_ids:
                selected_ids.append(persona.id)
            elif not new_checked and persona.id in selected_ids:
                selected_ids.remove(persona.id)
    st.session_state[KEY_SELECTED_PERSONA_IDS] = selected_ids

    with st.expander("➕ Create Custom Persona"):
        custom_name = st.text_input(
            "Name (max 100 chars)", max_chars=100, key="custom_persona_name"
        )
        custom_desc = st.text_area(
            "Description (max 500 chars)", max_chars=500, key="custom_persona_desc"
        )
        if st.button("Save Persona", key="save-custom-persona"):
            persona, result = persona_svc.create_custom_persona(custom_name, custom_desc)
            if result.valid:
                st.success(f"Persona '{persona.name}' created.")
                st.rerun()
            else:
                render_validation_errors(result.errors)

    custom_personas = [p for p in all_personas if p.type == "custom"]
    if custom_personas:
        with st.expander("✏️ Manage Custom Personas"):
            for cp in custom_personas:
                st.markdown(f"**{cp.name}**")
                edit_name = st.text_input(
                    "Name", value=cp.name, max_chars=100, key=f"edit_name_{cp.id}"
                )
                edit_desc = st.text_area(
                    "Description", value=cp.description, max_chars=500, key=f"edit_desc_{cp.id}"
                )
                col_save, col_del = st.columns([1, 1])
                with col_save:
                    if st.button("Save", key=f"edit_save_{cp.id}"):
                        _, result = persona_svc.update_custom_persona(cp.id, edit_name, edit_desc)
                        if result.valid:
                            st.success(f"'{edit_name}' updated.")
                            st.rerun()
                        else:
                            render_validation_errors(result.errors)
                with col_del:
                    if st.button("Delete", key=f"edit_del_{cp.id}", type="secondary"):
                        persona_svc.delete_custom_persona(cp.id)
                        if cp.id in selected_ids:
                            selected_ids.remove(cp.id)
                            st.session_state[KEY_SELECTED_PERSONA_IDS] = selected_ids
                        st.rerun()
                st.divider()

    st.subheader("Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        max_turns = st.number_input(
            "Max turns", min_value=1, max_value=20, value=3, key="max_turns"
        )
    with col2:
        style = st.selectbox(
            "Discussion style",
            ["formal", "casual", "debate"],
            key="discussion_style",
        )
    with col3:
        language = st.selectbox(
            "Language",
            ["en", "ja", "fr", "de", "es"],
            key="discussion_language",
        )

    st.subheader("Materials (optional)")
    uploaded = st.file_uploader(
        "Upload reference material",
        type=["txt", "md", "pdf", "docx"],
        key="materials_upload",
    )
    if uploaded and uploaded.size > 10 * 1024 * 1024:
        st.error("File exceeds 10 MB limit.")
        uploaded = None

    if st.button(
        "▶ Start Discussion",
        disabled=is_executing,
        key="start-discussion",
    ):
        params = DiscussionParameters(
            max_turns=int(max_turns),
            language=language,
            discussion_style=style,
        )
        mat_bytes = uploaded.read() if uploaded else None
        mat_name = uploaded.name if uploaded else None
        discussion, result = svc.setup_discussion(
            st.session_state.get("topic_input", ""),
            selected_ids,
            params,
            mat_bytes,
            mat_name,
        )
        if not result.valid:
            render_validation_errors(result.errors)
        else:
            render_validation_warnings(result.warnings)
            st.session_state[KEY_CURRENT_DISCUSSION] = discussion
            st.session_state[KEY_WORKFLOW_STATE] = "executing"
            st.rerun()

# ──────────────────────────────────────────────────────────────
# Streaming Execution Display
# ──────────────────────────────────────────────────────────────
if state == "executing":
    discussion = st.session_state.get(KEY_CURRENT_DISCUSSION)
    if not discussion:
        st.error("No active discussion found.")
        st.stop()

    st.info(f"**Topic**: {discussion.topic}")

    # Render already-completed messages
    for msg in discussion.messages:
        idx = next(
            (j for j, p in enumerate(discussion.personas) if p.id == msg.persona_id),
            0,
        )
        render_message_card(msg, agent_color(idx))

    # Soft turn-limit warning banner
    if st.session_state.get(KEY_SHOW_TURN_LIMIT_WARNING):
        st.warning("⚠️ Discussion is approaching its configured turn limit.")

    # Turn-limit modal
    if st.session_state.get(KEY_SHOW_TURN_LIMIT_MODAL):
        st.warning("**Turn limit reached.** Continue or finish?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Continue Discussion", key="continue-discussion"):
                discussion.parameters.max_turns += discussion.parameters.extended_turns
                st.session_state[KEY_SHOW_TURN_LIMIT_MODAL] = False
                st.rerun()
        with c2:
            if st.button("Finish Discussion", key="finish-discussion"):
                discussion.state = "completed"
                st.session_state[KEY_WORKFLOW_STATE] = "completed"
                st.session_state[KEY_SHOW_TURN_LIMIT_MODAL] = False
                st.switch_page("pages/3_Results.py")
        st.stop()

    # Resume point banner
    resume = st.session_state.get(KEY_RESUME_POINT, {})
    if resume.get("is_resumable"):
        st.error(
            f"⚠️ Discussion paused at turn {resume['failed_turn']}: "
            f"{resume['error_message']}"
        )
        if st.button("▶ Resume Discussion", key="resume-discussion"):
            st.rerun()
        st.stop()

    # Build AI engine
    config = st.session_state[KEY_CONFIG]

    stop_flag = {"stop": False}
    if st.button("⏹ Stop Discussion", key="stop-discussion"):
        stop_flag["stop"] = True

    placeholder = st.empty()
    streaming_buf: dict = {"content": "", "persona": ""}

    def on_chunk(persona_name: str, chunk: str) -> None:
        streaming_buf["content"] += chunk
        streaming_buf["persona"] = persona_name
        placeholder.markdown(f"**{persona_name}**: {streaming_buf['content']}▌")

    def on_message_complete(msg) -> None:
        streaming_buf["content"] = ""
        placeholder.empty()
        idx = next(
            (j for j, p in enumerate(discussion.personas) if p.id == msg.persona_id),
            0,
        )
        render_message_card(msg, agent_color(idx))

    try:
        svc.execute_discussion(
            discussion,
            on_chunk=on_chunk,
            on_message_complete=on_message_complete,
            should_stop=lambda: stop_flag["stop"],
        )
        st.session_state[KEY_WORKFLOW_STATE] = "completed"
        st.session_state[KEY_CURRENT_DISCUSSION] = discussion
        st.switch_page("pages/3_Results.py")
    except Exception as e:
        err_msg = (
            st.session_state.get(KEY_RESUME_POINT, {}).get("error_message") or str(e)
        )
        st.error(f"Discussion paused due to an error: {err_msg}")
        if st.button("▶ Resume Discussion", key="resume-after-error"):
            st.rerun()
