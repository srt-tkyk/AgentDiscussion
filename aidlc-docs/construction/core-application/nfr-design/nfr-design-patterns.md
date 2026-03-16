# NFR Design Patterns - Core Application

## Overview
Design patterns implementing the NFR requirements for the Core Application unit.

---

## 1. Resilience Pattern: Resume on API Failure

### Pattern: Checkpoint-and-Resume
Store the resume point in both session state (immediate resume) and the discussion JSON (cross-session resume).

**Session State Keys (added to schema)**:
```python
st.session_state['resume_point'] = {
    "failed_turn": int,        # Turn number that failed
    "failed_persona_index": int,  # Index in personas list that failed
    "error_message": str,      # Human-readable error
    "is_resumable": bool,      # True when in error-paused state
}
```

**JSON Persistence (added to Discussion entity)**:
```python
@dataclass
class Discussion:
    ...
    resume_point: dict | None  # None when not in error state
```

**Flow**:
```
API error during turn N, persona P
        │
        ▼
Force-save discussion JSON with resume_point = {failed_turn: N, failed_persona_index: P}
        │
        ▼
Set st.session_state['resume_point'] with same data
        │
        ▼
Set workflow_state = 'executing' (stays executing, paused)
        │
        ▼
Display error banner + "Resume Discussion" button
        │
        ▼
User clicks Resume
        │
        ▼
Retry from (turn N, persona P) — skip already-completed messages
        │
        ▼
On success: clear resume_point in both session state and JSON
```

**Cross-session resume**: When loading a discussion from history, if `resume_point` is present and `state == 'executing'`, offer "Resume" option on the Results page.

---

## 2. Security Pattern: Config Loading and Validation

### Pattern: Fail-Fast Config Loader
```
App startup
    │
    ▼
ConfigurationManager.load()
    ├── config.yaml exists? → parse YAML
    │       ├── parse error → raise ConfigError with clear message
    │       └── success → validate required fields
    └── config.yaml missing → raise ConfigError("config.yaml not found. Copy config.yaml.example.")
            │
            ▼
    Validate anthropic.api_key present and non-empty
            ├── missing/empty → raise ConfigError("anthropic.api_key is required in config.yaml")
            └── present → proceed to API validation
```

### Pattern: .gitignore Auto-Generation
Runs once at startup before config loading:
```python
def ensure_gitignore():
    gitignore = Path(".gitignore")
    entry = "config.yaml\n"
    if gitignore.exists():
        if "config.yaml" not in gitignore.read_text():
            gitignore.open("a").write(entry)
    else:
        gitignore.write_text(entry)
```

### Pattern: Startup API Key Validation
```
ConfigurationManager loaded successfully
        │
        ▼
Call client.models.list() with configured API key
        ├── Success → set session_state['api_key_valid'] = True, proceed to app
        └── AuthenticationError → display Setup page error:
                "Invalid API key. Please check config.yaml."
                Block navigation to Discussion page.
        └── ConnectionError → display Setup page warning:
                "Could not reach Anthropic API. Check your internet connection."
                Block navigation to Discussion page.
```

---

## 3. Performance Pattern: Streaming Passthrough

### Pattern: Direct Chunk Rendering
No buffering — render each chunk from the API stream immediately into a Streamlit placeholder.

```
DiscussionEngine yields chunk from anthropic streaming response
        │
        ▼
DiscussionService receives chunk via async callback
        │
        ▼
StreamlitUI appends chunk to st.empty() placeholder
        │
        ▼
Streamlit re-renders the placeholder (no full page rerun)
        │
        ▼
After stream complete: append full message to session_state['messages']
```

### Pattern: Button State Management
```python
# During executing state
is_executing = st.session_state['workflow_state'] == 'executing'

start_button.disabled = is_executing
export_button.disabled = is_executing
new_discussion_button.disabled = is_executing
# Scrolling: not blocked (Streamlit default behavior)
```

---

## 4. Maintainability Pattern: Logging Setup

### Pattern: Module-Level Logger with Rotating File Handler
```python
# core/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(level: str = "INFO"):
    Path("logs").mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        "logs/agent_discussion.log",
        maxBytes=1_000_000,  # 1 MB
        backupCount=3,
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    logging.basicConfig(level=getattr(logging, level), handlers=[handler])
```

**Logger usage convention** — each module gets its own named logger:
```python
# In any module
import logging
logger = logging.getLogger(__name__)

# Usage
logger.info("Discussion started: %s", discussion_id)
logger.error("API failure on turn %d: %s", turn, error)
```

**Log placement rules**:
| Event | Level |
|---|---|
| Workflow state transition | INFO |
| Discussion start / end | INFO |
| API request sent | DEBUG |
| API response received | DEBUG |
| API failure | ERROR |
| File I/O error | ERROR |
| Config validation warning | WARNING |
| Input validation failure | WARNING |
