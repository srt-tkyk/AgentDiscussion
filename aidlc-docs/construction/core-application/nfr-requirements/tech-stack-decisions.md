# Tech Stack Decisions - Core Application

## Overview
Finalized technology choices for the Core Application unit.

---

## Core Stack

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| Language | Python | 3.9+ | Specified in requirements; broad compatibility |
| Web Framework | Streamlit | Latest stable | Specified in requirements; rapid UI development |
| AI Provider | Anthropic Claude | Latest SDK | Specified in requirements |
| Config Format | YAML | — | Specified in requirements |

---

## Dependencies

### Runtime Dependencies

| Package | Purpose | Notes |
|---|---|---|
| `streamlit` | Web UI framework | Core requirement |
| `anthropic` | Claude API client | Official SDK; enforces HTTPS |
| `pyyaml` | YAML config parsing | Read `config.yaml` |
| `pymupdf` (fitz) | PDF text extraction | Fast, no external binaries |
| `python-docx` | DOCX text extraction | Standard, well-maintained |

### Dev / Test Dependencies

| Package | Purpose |
|---|---|
| `pytest` | Unit and integration testing |
| `pytest-asyncio` | Async test support |

---

## File Storage

| Data | Format | Location |
|---|---|---|
| Discussions | JSON | `data/discussions/{id}.json` |
| Predefined personas | JSON | `data/personas/predefined.json` |
| Custom personas | JSON | `data/personas/custom/{id}.json` |
| Materials | Raw files | `data/materials/` |
| Config | YAML | `config.yaml` (root) |
| Logs | Text (rotating) | `logs/agent_discussion.log` |
| Export output | Markdown | `exports/{slug}_{date}.md` |

---

## Key Architectural Decisions

### Decision 1: API Key in config.yaml only
- **Choice**: `config.yaml` exclusively (no env var fallback)
- **Rationale**: Simplicity for a personal local tool
- **Security mitigation**: Auto-add `config.yaml` to `.gitignore`

### Decision 2: Startup API Key Validation
- **Choice**: Validate on startup with a lightweight API call
- **Rationale**: Fail fast; better UX than mid-discussion failure

### Decision 3: Resume on API Failure
- **Choice**: Force-save state on error, offer "Resume" button
- **Rationale**: Preserves discussion progress across API failures

### Decision 4: Partial UI Lock During Streaming
- **Choice**: Disable action buttons; keep scrolling enabled
- **Rationale**: Prevents conflicting actions while keeping content readable

### Decision 5: Rotating File Logging
- **Choice**: `RotatingFileHandler`, 1 MB max, 3 backups
- **Rationale**: Persistent debug trail without unbounded disk growth

---

## Python Version Compatibility Notes
- Minimum: Python 3.9
- Uses `dataclasses` (3.7+), `|` union type hints require 3.10+ — use `Optional[X]` / `Union[X, Y]` for 3.9 compatibility
- f-strings, `pathlib`, `asyncio` all available in 3.9+
