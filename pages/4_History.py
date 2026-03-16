"""History page — browse and reload past discussions."""
import streamlit as st

from agent_discussion.ui.components import (
    KEY_API_KEY_VALID,
    KEY_CURRENT_DISCUSSION,
    KEY_DISCUSSION_SERVICE,
    KEY_RESUME_POINT,
    KEY_WORKFLOW_STATE,
)

st.set_page_config(page_title="History", page_icon="🗂️")
st.title("🗂️ History")

if not st.session_state.get(KEY_API_KEY_VALID):
    st.warning("Please complete setup first.")
    st.stop()

svc = st.session_state[KEY_DISCUSSION_SERVICE]
summaries = svc.load_discussion_history()

if not summaries:
    st.info("No past discussions found.")
    st.stop()

for summary in summaries:
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{summary.topic}**")
            date_str = (
                summary.created_at.strftime("%Y-%m-%d %H:%M")
                if summary.created_at
                else "unknown"
            )
            st.caption(
                f"Participants: {', '.join(summary.persona_names)}  ·  "
                f"Turns: {summary.turn_count}  ·  "
                f"State: {summary.state}  ·  "
                f"Date: {date_str}"
            )
        with col2:
            if st.button("Load", key=f"load-{summary.id}"):
                loaded = svc.load_discussion(summary.id)
                if loaded:
                    st.session_state[KEY_CURRENT_DISCUSSION] = loaded
                    st.session_state[KEY_WORKFLOW_STATE] = loaded.state
                    # Restore resume point to session state if present
                    if loaded.resume_point:
                        st.session_state[KEY_RESUME_POINT] = loaded.resume_point
                    else:
                        st.session_state.pop(KEY_RESUME_POINT, None)
                    st.switch_page("pages/3_Results.py")
                else:
                    st.error("Failed to load discussion.")
        st.divider()
