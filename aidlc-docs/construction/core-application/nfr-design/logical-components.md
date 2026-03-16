# Logical Components - Core Application

## Overview
Logical components added or modified to implement NFR design patterns. These are technology-agnostic design elements that will be realized in code generation.

---

## New Logical Components

### 1. ConfigurationManager (enhanced)
**Existing component** — extended with NFR responsibilities.

**Added responsibilities**:
- `.gitignore` auto-generation on startup (`ensure_gitignore()`)
- Fail-fast YAML loading with clear error messages
- API key presence validation (format only)
- Expose `api_key_valid: bool` state after startup validation

**Startup sequence**:
```
ensure_gitignore() → load_config() → validate_config() → validate_api_key_with_api()
```

---

### 2. ApiValidator
**New logical component** — single-responsibility: validate API key against live API.

**Responsibility**: Call `client.models.list()` and return success/failure with error type.

**Interface**:
```python
class ApiValidator:
    def validate(self, api_key: str) -> ApiValidationResult:
        ...

@dataclass
class ApiValidationResult:
    valid: bool
    error_type: str | None   # "auth" | "connection" | None
    error_message: str | None
```

**Used by**: `ConfigurationManager` during startup sequence.

---

### 3. LoggingConfig
**New logical component** — sets up application-wide logging.

**Responsibility**: Configure `RotatingFileHandler` once at app entry point.

**Interface**:
```python
def setup_logging(level: str = "INFO") -> None: ...
```

**Called once** in `main.py` before any other initialization.

---

### 4. ResumeManager
**New logical component** — manages error-pause and resume state.

**Responsibility**: Encapsulate all resume-point logic (set, clear, detect, restore).

**Interface**:
```python
class ResumeManager:
    def set_resume_point(self, turn: int, persona_index: int, error: str) -> None: ...
    def clear_resume_point(self) -> None: ...
    def has_resume_point(self) -> bool: ...
    def get_resume_point(self) -> dict | None: ...
```

**Stores to**: both `st.session_state['resume_point']` and the discussion JSON via `FileManager`.

**Used by**: `DiscussionService` on API failure and on successful resume completion.

---

## Modified Logical Components

### DiscussionService (modified)
**Added responsibilities**:
- On API error: call `ResumeManager.set_resume_point()`, then force-save via `FileManager`
- On resume: call `ResumeManager.get_resume_point()`, skip already-completed messages, retry from checkpoint
- On successful resume completion: call `ResumeManager.clear_resume_point()`

### Discussion (domain entity, modified)
**Added field**: `resume_point: dict | None` — persisted in JSON, `None` when not in error state.

### StreamlitUI (modified)
**Added responsibilities**:
- Render "Resume Discussion" button when `ResumeManager.has_resume_point()` is True
- Disable action buttons (`start`, `export`, `new_discussion`) when `workflow_state == 'executing'`
- Render streaming chunks into `st.empty()` placeholder without full page rerun

---

## Component Interaction for NFR Flows

### Startup Flow
```
main.py
  → setup_logging()                    [LoggingConfig]
  → ensure_gitignore()                 [ConfigurationManager]
  → load_config()                      [ConfigurationManager]
  → validate_api_key_with_api()        [ConfigurationManager → ApiValidator]
  → render Setup page (valid/invalid)  [StreamlitUI]
```

### API Failure Flow
```
DiscussionService.execute_discussion()
  → API error raised
  → ResumeManager.set_resume_point(turn, persona_index, error)
  → FileManager.save_discussion(discussion)   [includes resume_point]
  → StreamlitUI renders error + Resume button
```

### Resume Flow
```
User clicks "Resume"
  → DiscussionService.resume_discussion()
  → ResumeManager.get_resume_point()
  → Skip messages already in discussion.messages
  → Retry from checkpoint
  → On success: ResumeManager.clear_resume_point()
  → FileManager.save_discussion(discussion)   [resume_point = None]
```
