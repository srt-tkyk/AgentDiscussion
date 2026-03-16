# Business Logic Model - Core Application

## Overview
This document defines the core business workflows, processes, and logic for the Core Application unit.

---

## 1. Discussion Workflow State Machine

### States
```
setup → configuring → executing → completed → exported
```

| State | Description | Entry Condition | Exit Condition |
|---|---|---|---|
| `setup` | Initial application load, API key configuration | App start | API key valid, user navigates to discussion |
| `configuring` | User sets topic, selects personas, configures parameters | From `setup` | User starts discussion |
| `executing` | Discussion is actively running, agents responding | From `configuring` | Turn limit reached or user stops |
| `completed` | Discussion finished, results available | From `executing` | User exports or navigates away |
| `exported` | Meeting minutes generated and saved | From `completed` | User starts new discussion |

### State Transitions
```
setup        --[api_key_configured]--> configuring
configuring  --[start_discussion]---> executing
executing    --[turn_limit_reached]--> completed
executing    --[user_stops]---------> completed
completed    --[export_requested]---> exported
exported     --[new_discussion]-----> configuring
```

### State Persistence
- Current state stored in `st.session_state['workflow_state']`
- State transitions logged with timestamp
- Invalid transitions raise `WorkflowStateError`

---

## 2. Persona Selection and Validation Logic

### Validation Flow
```
User selects personas
        │
        ▼
Check count (2-6 personas)
        │
        ├── FAIL → Show error: "Select between 2 and 6 personas"
        │
        ▼
Check for duplicates
        │
        ├── FAIL → Show warning: "Duplicate persona detected"
        │
        ▼
Analyze role balance (recommendations only)
        │
        ├── WARN → "Consider adding a [role] for balanced discussion"
        │
        ▼
Validate persona data completeness
        │
        ▼
Return validation result (errors block, warnings allow override)
```

### Recommendation Rules
- If all personas share the same expertise area → recommend diversity
- If no "devil's advocate" or critical role → suggest adding one
- If more than 4 personas with similar communication styles → suggest variety
- Warnings are advisory; user can proceed despite warnings

---

## 3. Discussion Materials Processing

### AI-Powered Preprocessing Flow
```
File uploaded / path provided
        │
        ▼
Detect file type (txt, md, pdf, docx)
        │
        ▼
Extract raw text content
        │
        ▼
Send to AI for preprocessing:
  - Summarize key points
  - Extract main topics
  - Identify relevant context for personas
        │
        ▼
Store preprocessed context in session state
        │
        ▼
Inject into discussion prompt as context
```

### Supported File Types
- `.txt`, `.md` — direct text extraction
- `.pdf` — text extraction via library
- `.docx` — text extraction via library

### Preprocessing Output Structure
```python
{
    "original_filename": str,
    "raw_text": str,
    "summary": str,           # AI-generated summary
    "key_topics": list[str],  # Extracted topics
    "context_for_discussion": str  # Formatted context for prompt injection
}
```

---

## 4. Discussion Execution Workflow

### Turn-Based Execution Loop
```
Discussion started
        │
        ▼
For each turn (1 to max_turns):
    For each selected persona:
        │
        ▼
        Build prompt (topic + context + history + persona instructions)
                │
                ▼
        Send async request to AI Integration Service
                │
                ▼
        Receive streaming response
                │
                ▼
        Display streamed message in UI
                │
                ▼
        Append message to discussion history
                │
                ▼
        Auto-save discussion state
        │
        ▼
Check turn limit → show soft warning at configured threshold
        │
        ▼
Discussion completes → transition to `completed` state
```

### Soft Turn Limit Logic
- At `max_turns - 1`: display banner "Discussion approaching configured limit"
- At `max_turns`: display modal "Turn limit reached. Continue or finish?"
  - "Continue" → increment max_turns by configured extension amount
  - "Finish" → transition to `completed` state

---

## 5. Auto-Save Logic

### Trigger Conditions
- After every completed agent turn
- On state transition (executing → completed)
- On explicit user save action

### Save Process
```
Serialize discussion state to dict
        │
        ▼
Write to `{discussions_dir}/{discussion_id}.json`
        │
        ▼
On error → display non-blocking warning, continue execution
```

---

## 6. History Management Workflow

### Load Discussion List
```
Read all `.json` files from discussions directory
        │
        ▼
Parse metadata (id, topic, date, persona names, turn count)
        │
        ▼
Sort by creation date descending
        │
        ▼
Display in history page
```

### Load Previous Discussion
```
User selects discussion from list
        │
        ▼
Read full discussion JSON from file
        │
        ▼
Deserialize into Discussion domain entity
        │
        ▼
Populate session state
        │
        ▼
Navigate to completed discussion view
```

---

## 7. Export Workflow

### Export Initiation
```
User requests export (from completed state)
        │
        ▼
Collect discussion data from session state
        │
        ▼
Call Export Service with discussion data
        │
        ▼
Receive generated file path
        │
        ▼
Offer download link / display save location
        │
        ▼
Transition to `exported` state
```
