# NFR Requirements - Core Application

## Overview
Non-functional requirements for the Core Application unit (personal single-user Streamlit tool).

---

## NFR-PERF-1: Streaming Response Time
- **Requirement**: No strict latency target — stream messages as fast as the API delivers them
- **Rationale**: Personal tool; user prefers natural API speed over artificial constraints
- **Implementation note**: Do not add artificial delays; pipe API stream chunks directly to UI

## NFR-PERF-2: UI Responsiveness During Streaming
- **Requirement**: Partial interactivity — scrolling must remain functional; action controls (start, stop, export) may be disabled during active streaming
- **Implementation note**: Disable Start/Export buttons while `workflow_state == 'executing'`; do not block Streamlit's rendering loop

---

## NFR-REL-1: API Failure Handling
- **Requirement**: On API failure mid-discussion, auto-save current progress and present a "Resume" option to retry from the failed turn
- **Behavior**:
  1. API error occurs during a turn
  2. Force-save discussion state immediately
  3. Display error message with "Resume Discussion" button
  4. On resume, retry the failed agent's turn from where it stopped
- **Rationale**: Preserves work done so far; avoids restarting long discussions from scratch

## NFR-REL-2: API Key Validation
- **Requirement**: Validate API key at application startup; block discussion start if key is invalid or missing
- **Behavior**:
  - On startup: attempt a lightweight API validation call
  - If invalid: display error on Setup page, prevent navigation to Discussion page
  - If valid: proceed normally

---

## NFR-SEC-1: API Key Storage
- **Requirement**: API key read exclusively from `config.yaml`; no environment variable fallback
- **Key path in config**: `anthropic.api_key`

## NFR-SEC-2: .gitignore Management
- **Requirement**: Automatically generate/update `.gitignore` to include `config.yaml` on first run
- **Behavior**: Append `config.yaml` if not already present; create `.gitignore` if absent

## NFR-SEC-3: Input Validation
- **Requirement**: Validate all user inputs before processing (rules defined in business-rules.md)

## NFR-SEC-4: Secure API Communication
- **Requirement**: All API calls use HTTPS via the official `anthropic` Python SDK

---

## NFR-MAINT-1: Logging
- **Requirement**: Python standard `logging` module writing to a rotating log file
- **Log file**: `logs/agent_discussion.log`
- **Log levels**: ERROR (failures), WARNING (validation/config), INFO (state transitions), DEBUG (API details, off by default)
- **Rotation**: `RotatingFileHandler`, max 1 MB, keep 3 backups

## NFR-MAINT-2: Code Structure
- Feature-based directory structure per unit-of-work.md
- Dependency injection for all service/component wiring
- No circular imports

## NFR-MAINT-3: Dependencies
- All dependencies pinned in `requirements.txt`
- No unused dependencies

---

## NFR-USAB-1: Interface Simplicity
- No technical knowledge required to operate
- Clear visual distinction between agents (color-coded by persona index)
- Immediate feedback on all user actions
