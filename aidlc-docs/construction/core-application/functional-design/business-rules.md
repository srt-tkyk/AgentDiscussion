# Business Rules - Core Application

## Overview
All validation rules, constraints, and business policies for the Core Application unit.

---

## 1. Topic Validation Rules

| Rule | Constraint | Error Message |
|---|---|---|
| Non-empty | Topic must not be blank | "Discussion topic is required" |
| Length | 1–500 characters | "Topic must be between 1 and 500 characters" |
| Encoding | Valid UTF-8 string | "Topic contains invalid characters" |

**Enforcement point**: `DiscussionService.setup_discussion()` before creating a Discussion entity.

---

## 2. Persona Selection Rules

### Hard Rules (block progression)
| Rule | Constraint | Error Message |
|---|---|---|
| Minimum count | At least 2 personas selected | "Select at least 2 personas to start a discussion" |
| Maximum count | No more than 6 personas | "Maximum 6 personas allowed per discussion" |
| No duplicates | Each persona ID unique in selection | "Persona '{name}' is already selected" |
| Data completeness | Each persona must have name and description | "Persona data is incomplete" |

### Soft Rules (warnings, user can override)
| Rule | Condition | Warning Message |
|---|---|---|
| Role diversity | All personas share same expertise area | "Consider adding personas with different expertise for a richer discussion" |
| Discussion balance | No persona with critical/questioning role | "Consider adding a critical thinker for balanced discussion" |

---

## 3. Discussion Parameters Rules

| Parameter | Default | Valid Range | Rule |
|---|---|---|---|
| `max_turns` | 3 | 1–20 | Must be positive integer |
| `language` | "en" | Supported language codes | Must be in supported list |
| `discussion_style` | "formal" | formal, casual, debate | Must be one of allowed values |
| `extended_turns` | 1 | 1–5 | Applied when user extends past limit |

---

## 4. Turn Limit Rules

| Condition | Action |
|---|---|
| `current_turn == max_turns - 1` | Display non-blocking banner: "Discussion approaching its limit" |
| `current_turn == max_turns` | Display modal: "Turn limit reached. Continue or finish?" |
| User selects "Continue" | `max_turns += extended_turns`, dismiss modal, continue execution |
| User selects "Finish" | Transition to `completed` state |

---

## 5. File Operations Rules

### Discussion Persistence
| Rule | Description |
|---|---|
| Auto-save trigger | After every completed agent message |
| Save format | JSON, UTF-8 encoded |
| File naming | `{discussion_id}.json` (UUID-based) |
| Error handling | Log error, display non-blocking warning, do not interrupt discussion |
| Overwrite | Always overwrite existing file (no versioning) |

### Custom Persona Persistence
| Rule | Description |
|---|---|
| Save trigger | On explicit user save action |
| File naming | `{persona_id}.json` where `persona_id` is URL-safe slug of name |
| Duplicate ID | Append numeric suffix: `{slug}-2`, `{slug}-3`, etc. |
| Delete | Remove file; if persona is in active discussion, block deletion with error |

### Materials Loading
| Rule | Description |
|---|---|
| Supported types | `.txt`, `.md`, `.pdf`, `.docx` |
| Max file size | 10 MB |
| Encoding | Attempt UTF-8, fallback to latin-1 |
| Error on unsupported type | "File type not supported. Use .txt, .md, .pdf, or .docx" |
| Error on size exceeded | "File exceeds 10 MB limit" |

---

## 6. Configuration Rules

| Rule | Description |
|---|---|
| API key required | Application cannot start discussion without valid API key |
| API key storage | Read from environment variable or config file; never hardcoded |
| Config file missing | Use defaults; do not raise error |
| Invalid config value | Use default for that field; log warning |

---

## 7. State Transition Rules

| From State | Allowed Transitions | Blocked Transitions |
|---|---|---|
| `setup` | → `configuring` | → `executing`, `completed`, `exported` |
| `configuring` | → `executing` | → `exported` |
| `executing` | → `completed` | → `setup`, `exported` |
| `completed` | → `exported`, → `configuring` (new discussion) | → `executing` |
| `exported` | → `configuring` (new discussion) | → `executing`, `completed` |

Invalid transition raises `WorkflowStateError` with message: "Cannot transition from '{current}' to '{target}'".

---

## 8. Export Rules

| Rule | Description |
|---|---|
| Export requires completed state | Export only available when `state == 'completed'` or `'exported'` |
| Minimum content | Discussion must have at least 1 message to export |
| File naming | `{discussion_topic_slug}_{date}.md` |
