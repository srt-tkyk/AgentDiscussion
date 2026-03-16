# Frontend Components - Core Application

## Overview
Multi-page Streamlit application using `st.session_state` for all state management. Pages are organized by user journey.

---

## Page Structure

```
app/
├── main.py                  # Entry point, page routing
├── pages/
│   ├── 1_Setup.py           # Journey 1: Initial setup
│   ├── 2_Discussion.py      # Journey 2+3: Configure and run discussion
│   ├── 3_Results.py         # Journey 4: Review and export
│   └── 4_History.py         # Journey 5: View and load past discussions
```

---

## Session State Schema

All UI state lives in `st.session_state`. Keys and types:

```python
st.session_state = {
    # Workflow
    "workflow_state": str,              # setup | configuring | executing | completed | exported

    # Discussion setup
    "topic": str,
    "selected_persona_ids": list[str],
    "discussion_parameters": dict,      # DiscussionParameters as dict
    "materials_context": str | None,

    # Active discussion
    "current_discussion_id": str | None,
    "messages": list[dict],             # List of Message dicts
    "current_turn": int,

    # UI flags
    "show_turn_limit_warning": bool,
    "show_turn_limit_modal": bool,
    "validation_errors": list[str],
    "validation_warnings": list[str],
}
```

---

## Page: Setup (1_Setup.py)

### Purpose
API key configuration and application initialization.

### Components

#### ApiKeyForm
- **Input**: Text input (password type) for API key
- **Validation**: Non-empty check on submit
- **On submit**: Store in config, transition `workflow_state` → `configuring`
- **State keys**: reads/writes nothing in session_state (config-level)

---

## Page: Discussion (2_Discussion.py)

### Purpose
Topic input, persona selection, parameter configuration, materials upload, and discussion execution.

### Components

#### TopicInputForm
- **Input**: `st.text_area` for discussion topic (max 500 chars)
- **Validation**: Non-empty, length ≤ 500
- **State keys**: `st.session_state['topic']`
- **Error display**: Inline below input field

#### PersonaSelector
- **Display**: Grid of persona cards (name + description excerpt)
- **Interaction**: Click to select/deselect; selected cards highlighted
- **Validation**: Enforce 2–6 selection count; show hard errors and soft warnings
- **Custom persona button**: Opens `CustomPersonaForm` in sidebar/expander
- **State keys**: `st.session_state['selected_persona_ids']`

#### CustomPersonaForm
- **Inputs**: Name (text, max 100), Description (text_area, max 500)
- **Validation**: Both fields non-empty
- **On submit**: Call `PersonaService.create_custom_persona()`, refresh persona list
- **Error display**: Inline below each field

#### DiscussionParametersForm
- **Inputs**:
  - `max_turns`: `st.number_input` (1–20, default 3)
  - `language`: `st.selectbox` (supported languages)
  - `discussion_style`: `st.radio` (formal / casual / debate)
- **State keys**: `st.session_state['discussion_parameters']`

#### MaterialsUploader
- **Input**: `st.file_uploader` (accepts .txt, .md, .pdf, .docx, max 10 MB)
- **On upload**: Call `DiscussionService.process_materials()`, store result
- **State keys**: `st.session_state['materials_context']`
- **Error display**: `st.error()` for unsupported type or size exceeded

#### StartDiscussionButton
- **Condition**: Enabled only when topic non-empty and 2–6 personas selected
- **On click**: Validate all inputs → call `DiscussionService.setup_discussion()` → transition to `executing`

#### DiscussionDisplay
- **Purpose**: Real-time streaming display during `executing` state
- **Layout**: Vertical list of message cards
- **Message card structure**:
  - Persona name (bold, colored by persona index)
  - Turn number badge
  - Message content (streamed progressively via `st.write_stream` or manual placeholder update)
- **Streaming**: Each agent message streamed into a `st.empty()` placeholder; content appended as chunks arrive
- **State keys**: reads `st.session_state['messages']`

#### TurnLimitBanner
- **Condition**: `show_turn_limit_warning == True`
- **Display**: `st.warning("Discussion approaching its configured limit")`

#### TurnLimitModal
- **Condition**: `show_turn_limit_modal == True`
- **Display**: `st.dialog` or expander with two buttons:
  - "Continue Discussion" → extend turns, dismiss modal
  - "Finish Discussion" → transition to `completed`

---

## Page: Results (3_Results.py)

### Purpose
Display completed discussion and trigger export.

### Components

#### CompletedDiscussionView
- **Display**: Full message list (same card layout as DiscussionDisplay, non-streaming)
- **State keys**: reads `st.session_state['messages']`

#### ExportButton
- **Condition**: Visible when `workflow_state in ('completed', 'exported')`
- **On click**: Call `ExportService.export_discussion()` → show download link or file path
- **Error display**: `st.error()` on export failure with retry button

#### NewDiscussionButton
- **On click**: Clear relevant session state keys, transition to `configuring`

---

## Page: History (4_History.py)

### Purpose
Browse and reload past discussions.

### Components

#### DiscussionHistoryList
- **Display**: Table or card list of `DiscussionSummary` items (topic, date, personas, turn count)
- **Sort**: By `created_at` descending
- **Interaction**: Click row/card to load discussion

#### LoadDiscussionButton (per row)
- **On click**: Call `DiscussionService.load_discussion()` → populate session state → navigate to Results page

---

## Interaction Flows

### Start Discussion Flow
```
TopicInputForm (enter topic)
    → PersonaSelector (select 2-6 personas)
    → DiscussionParametersForm (configure)
    → MaterialsUploader (optional)
    → StartDiscussionButton (click)
    → DiscussionDisplay (streaming messages appear)
    → TurnLimitModal (at limit) → Continue or Finish
    → Results page (on completion)
```

### Load History Flow
```
History page → DiscussionHistoryList (browse)
    → LoadDiscussionButton (click)
    → Results page (completed discussion view)
```

---

## Form Validation Rules

| Component | Field | Rule | Display |
|---|---|---|---|
| TopicInputForm | topic | Non-empty, ≤500 chars | Inline `st.error()` |
| PersonaSelector | selection | 2–6 personas | Inline `st.error()` / `st.warning()` |
| CustomPersonaForm | name | Non-empty, ≤100 chars | Inline `st.error()` |
| CustomPersonaForm | description | Non-empty, ≤500 chars | Inline `st.error()` |
| DiscussionParametersForm | max_turns | 1–20 | `st.number_input` min/max enforced |
| MaterialsUploader | file | Supported type, ≤10 MB | `st.error()` |

---

## API Integration Points

| Component | Service/Method Called |
|---|---|
| ApiKeyForm | `ConfigurationManager.set_api_key()` |
| PersonaSelector | `PersonaService.get_all_personas()` |
| CustomPersonaForm | `PersonaService.create_custom_persona()` |
| MaterialsUploader | `DiscussionService.process_materials()` |
| StartDiscussionButton | `DiscussionService.setup_discussion()` |
| DiscussionDisplay | `DiscussionService.execute_discussion()` (async streaming) |
| ExportButton | `ExportService.export_discussion()` |
| DiscussionHistoryList | `DiscussionService.load_discussion_history()` |
| LoadDiscussionButton | `DiscussionService.load_discussion()` |
