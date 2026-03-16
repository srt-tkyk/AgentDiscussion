"""Setup page — API key status display."""
import streamlit as st

from agent_discussion.ui.components import (
    KEY_API_KEY_VALID,
    KEY_API_VALIDATION_RESULT,
    KEY_CONFIG_ERROR,
)

st.set_page_config(page_title="Setup", page_icon="⚙️")
st.title("⚙️ Setup")

if st.session_state.get(KEY_CONFIG_ERROR):
    st.error(st.session_state[KEY_CONFIG_ERROR])
    st.info("Edit `config.yaml` and set `anthropic.api_key`, then restart the app.")
    st.stop()

valid = st.session_state.get(KEY_API_KEY_VALID, False)
validation_result = st.session_state.get(KEY_API_VALIDATION_RESULT)

if valid:
    st.success("✅ API key is valid. You're ready to start a discussion.")
    if st.button("Go to Discussion →", key="setup-go"):
        st.switch_page("pages/2_Discussion.py")
else:
    error_msg = (
        validation_result.error_message
        if validation_result
        else "API key could not be validated."
    )
    st.error(f"❌ {error_msg}")
    st.info("Edit `config.yaml` and set `anthropic.api_key`, then restart the app.")
