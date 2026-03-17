"""Application entry point."""
import streamlit as st

from agent_discussion.core.api_validator import ApiValidator
from agent_discussion.core.config import ConfigurationManager, ensure_gitignore
from agent_discussion.core.exceptions import ConfigError
from agent_discussion.core.files import FileManager
from agent_discussion.core.logging_config import setup_logging
from agent_discussion.core.resume_manager import ResumeManager
from agent_discussion.discussions.engine import DiscussionEngine
from agent_discussion.discussions.service import DiscussionService
from agent_discussion.personas.manager import PersonaManager
from agent_discussion.personas.service import PersonaService
from agent_discussion.ui.components import (
    KEY_API_KEY_VALID,
    KEY_API_VALIDATION_RESULT,
    KEY_CONFIG,
    KEY_CONFIG_ERROR,
    KEY_DISCUSSION_SERVICE,
    KEY_FILE_MANAGER,
    KEY_INITIALIZED,
    KEY_PERSONA_SERVICE,
    KEY_RESUME_MANAGER,
    KEY_WORKFLOW_STATE,
)


def _init() -> None:
    """Initialize all services into session_state once per session."""
    if st.session_state.get(KEY_INITIALIZED):
        return

    # 1. Logging (load config partially to get log level, fall back to INFO)
    try:
        _pre_config = ConfigurationManager()
        _pre_config.load()
        log_level = _pre_config.get("app", "log_level", default="INFO")
    except ConfigError:
        log_level = "INFO"
    setup_logging(level=log_level)

    # 2. Auto-generate .gitignore entry for config.yaml
    ensure_gitignore()

    # 3. Load full config
    config = ConfigurationManager()
    try:
        config.load()
    except ConfigError as e:
        st.session_state[KEY_CONFIG_ERROR] = str(e)
        st.session_state[KEY_API_KEY_VALID] = False
        st.session_state[KEY_INITIALIZED] = True
        return

    st.session_state[KEY_CONFIG] = config

    # 4. Validate API key against live API
    result = ApiValidator().validate(config.get_api_key())
    st.session_state[KEY_API_KEY_VALID] = result.valid
    st.session_state[KEY_API_VALIDATION_RESULT] = result

    # 5. Wire services (Dependency Injection)
    fm = FileManager(config)
    pm = PersonaManager(fm)
    ps = PersonaService(pm)
    rm = ResumeManager(fm)
    engine = DiscussionEngine(
        api_key=config.get_api_key(),
        model=config.get("anthropic", "model", default="claude-3-5-sonnet-20241022"),
        max_tokens=config.get("anthropic", "max_tokens", default=4096),
        max_response_chars=config.get("anthropic", "max_response_chars", default=500),
    )
    ds = DiscussionService(fm, ps, rm, engine)

    st.session_state[KEY_FILE_MANAGER] = fm
    st.session_state[KEY_PERSONA_SERVICE] = ps
    st.session_state[KEY_DISCUSSION_SERVICE] = ds
    st.session_state[KEY_RESUME_MANAGER] = rm

    if KEY_WORKFLOW_STATE not in st.session_state:
        st.session_state[KEY_WORKFLOW_STATE] = "configuring"

    st.session_state[KEY_INITIALIZED] = True


_init()
st.switch_page("pages/1_Setup.py")
