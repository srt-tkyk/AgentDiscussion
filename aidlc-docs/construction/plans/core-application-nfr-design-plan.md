# Core Application NFR Design Plan

## Unit Context
**Unit**: Core Application (Monolith)
**NFR Requirements**: `aidlc-docs/construction/core-application/nfr-requirements/`

## Purpose
Translate NFR requirements into concrete design patterns and logical components.

---

## NFR DESIGN QUESTIONS

#### Question 1
For the "Resume Discussion" feature after an API failure, how should the resume point be stored?

A) In `st.session_state` only — resume is only possible within the same browser session
B) Persisted to the discussion JSON file — resume is possible even after app restart
C) Both — session state for immediate resume, JSON for cross-session resume
E) Other (please describe after [Answer]: tag below)

[Answer]: C

#### Question 2
For startup API key validation, what should the "lightweight validation call" be?

A) Call `client.models.list()` — lists available models, minimal cost
B) Send a minimal 1-token message to Claude — confirms full API access
C) Just check that the key is non-empty and matches the expected format (no actual API call)
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## NFR DESIGN CHECKLIST

### Phase 1: Resilience Patterns
- [x] Design resume-on-failure pattern (Q1)
- [x] Define error state representation in session state and JSON

### Phase 2: Security Patterns
- [x] Design config.yaml loading and validation pattern
- [x] Design .gitignore auto-generation logic
- [x] Design startup API key validation flow (Q2)

### Phase 3: Performance Patterns
- [x] Design streaming passthrough pattern (UI chunk rendering)
- [x] Define button disable/enable logic during streaming

### Phase 4: Maintainability Patterns
- [x] Design logging setup (RotatingFileHandler configuration)
- [x] Define log call placement conventions

### Phase 5: Artifact Generation
- [x] Generate nfr-design-patterns.md
- [x] Generate logical-components.md

---

## Completion Criteria
- [x] All NFR design questions answered
- [x] All NFR patterns documented
- [x] Logical components defined
- [ ] User explicitly approves NFR design
