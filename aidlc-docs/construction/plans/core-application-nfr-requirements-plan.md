# Core Application NFR Requirements Plan

## Unit Context
**Unit**: Core Application (Monolith)
**Type**: Personal single-user Streamlit web application
**Tech Stack (from requirements)**: Python 3.9+, Streamlit, Claude API (Anthropic), YAML config

## Purpose
Confirm and detail non-functional requirements and finalize tech stack decisions for the Core Application unit.

---

## NFR REQUIREMENTS QUESTIONS

### Performance Questions

#### Question 1
What is the acceptable response time for the UI to begin displaying a streamed agent message after the AI request is sent?

A) Under 1 second (as specified in requirements NFR-3)
B) Under 2 seconds
C) Under 3 seconds
D) No strict requirement — just "as fast as possible"
E) Other (please describe after [Answer]: tag below)

[Answer]: D

#### Question 2
Should the application remain responsive (e.g., allow scrolling, viewing history) while a discussion is actively streaming?

A) Yes — UI must remain interactive during streaming
B) No — blocking the UI during streaming is acceptable for simplicity
C) Partial — some controls can be disabled but scrolling must work
E) Other (please describe after [Answer]: tag below)

[Answer]: C

### Reliability Questions

#### Question 3
When an API call fails mid-discussion, what should happen?

A) Stop the discussion and show an error with a retry button (as per requirements FR-8)
B) Automatically retry up to 3 times before showing error
C) Skip the failed agent's turn and continue with the next agent
D) Save progress and allow user to resume from the failed turn
E) Other (please describe after [Answer]: tag below)

[Answer]: D

#### Question 4
Should the application validate the API key on startup before allowing a discussion to begin?

A) Yes — validate on startup and block discussion if invalid
B) Yes — validate only when user attempts to start a discussion
C) No — only surface errors when an actual API call fails
E) Other (please describe after [Answer]: tag below)

[Answer]: A

### Security Questions

#### Question 5
Where should the API key be read from at runtime?

A) Environment variable only
B) config.yaml file only
C) Either environment variable or config.yaml (env var takes precedence)
D) Both must be present (config.yaml for defaults, env var for override)
E) Other (please describe after [Answer]: tag below)

[Answer]: B

#### Question 6
Should config.yaml be automatically added to .gitignore during setup?

A) Yes — generate a .gitignore entry automatically
B) No — document it in README but leave .gitignore to the user
C) Provide a .gitignore template but don't auto-modify
E) Other (please describe after [Answer]: tag below)

[Answer]: A

### Tech Stack Questions

#### Question 7
Which Python version should be the minimum target?

A) Python 3.9 (as specified in requirements)
B) Python 3.10
C) Python 3.11
D) Python 3.12
E) Other (please describe after [Answer]: tag below)

[Answer]: A

#### Question 8
For PDF text extraction (materials upload), which library is preferred?

A) PyMuPDF (fitz) — fast, no external dependencies
B) pdfplumber — good table/layout support
C) pypdf — lightweight, pure Python
D) No preference — choose the simplest option
E) Other (please describe after [Answer]: tag below)

[Answer]: A

#### Question 9
For DOCX text extraction, which library is preferred?

A) python-docx — standard, well-maintained
B) docx2txt — simpler, text-only extraction
C) No preference — choose the simplest option
E) Other (please describe after [Answer]: tag below)

[Answer]: A

### Maintainability Questions

#### Question 10
What logging approach should be used for error and debug logging?

A) Python standard `logging` module writing to a log file
B) Python standard `logging` module writing to stdout only
C) Simple `print()` statements for debugging (no formal logging)
D) No logging required for this personal tool
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## NFR REQUIREMENTS CHECKLIST

### Phase 1: Performance Assessment
- [x] Define streaming response time requirements (Q1)
- [x] Define UI responsiveness during streaming (Q2)
- [x] Document performance benchmarks

### Phase 2: Reliability Assessment
- [x] Define API failure handling strategy (Q3)
- [x] Define API key validation approach (Q4)
- [x] Document reliability requirements

### Phase 3: Security Assessment
- [x] Define API key storage and access (Q5)
- [x] Define .gitignore strategy (Q6)
- [x] Document security requirements

### Phase 4: Tech Stack Finalization
- [x] Confirm Python version (Q7)
- [x] Select PDF extraction library (Q8)
- [x] Select DOCX extraction library (Q9)
- [x] Confirm full dependency list

### Phase 5: Maintainability Assessment
- [x] Define logging approach (Q10)
- [x] Document maintainability requirements

### Phase 6: Artifact Generation
- [x] Generate nfr-requirements.md
- [x] Generate tech-stack-decisions.md

---

## Completion Criteria
- [x] All NFR questions answered and ambiguities resolved
- [x] Performance, reliability, security requirements documented
- [x] Tech stack fully decided
- [ ] User explicitly approves NFR requirements
