# Domain Entities - Core Application

## Overview
Rich domain model with core entities and their relationships.

---

## Entity Definitions

### Persona
Simple model representing a discussion participant.

```python
@dataclass
class Persona:
    id: str                    # Unique identifier (slug)
    name: str                  # Display name
    description: str           # Role/background description
    type: str                  # "predefined" | "custom"
    created_at: datetime       # Creation timestamp (custom personas)
```

**Constraints**:
- `id` must be unique across all personas
- `name` max 100 characters, non-empty
- `description` max 500 characters, non-empty

---

### Message
A single agent response in the discussion.

```python
@dataclass
class Message:
    id: str                    # Unique message identifier
    persona_id: str            # FK → Persona.id
    persona_name: str          # Denormalized for display
    content: str               # Message text
    turn_number: int           # Which turn this belongs to
    timestamp: datetime        # When message was generated
```

---

### Discussion
Top-level entity representing a complete discussion session.

```python
@dataclass
class Discussion:
    id: str                    # Unique identifier (UUID)
    topic: str                 # Discussion topic
    personas: list[Persona]    # Selected participants
    messages: list[Message]    # Ordered list of messages (linear model)
    parameters: DiscussionParameters
    materials_context: str | None  # Preprocessed materials content
    state: str                 # workflow state
    created_at: datetime
    updated_at: datetime
```

---

### DiscussionParameters
Configuration for a discussion session.

```python
@dataclass
class DiscussionParameters:
    max_turns: int             # Configured turn limit (default: 3)
    language: str              # Response language (default: "en")
    discussion_style: str      # "formal" | "casual" | "debate"
    extended_turns: int        # How many turns to add when extending (default: 1)
```

---

### DiscussionSummary
Lightweight metadata for history list display.

```python
@dataclass
class DiscussionSummary:
    id: str
    topic: str
    persona_names: list[str]
    turn_count: int
    state: str
    created_at: datetime
    updated_at: datetime
```

---

## Entity Relationships

```
Discussion 1 ──── * Persona        (selected participants)
Discussion 1 ──── * Message        (ordered conversation)
Discussion 1 ──── 1 DiscussionParameters
Message    * ──── 1 Persona        (author, via persona_id)
```

---

## Data Integrity Rules

| Rule | Description |
|---|---|
| Persona uniqueness | No duplicate persona IDs within a Discussion |
| Persona count | 2–6 personas per Discussion |
| Message ordering | Messages ordered by (turn_number, persona order in Discussion.personas) |
| Topic non-empty | Discussion.topic must be non-empty string, max 500 chars |
| Turn number | Message.turn_number >= 1 |

---

## Persistence Format

Discussions are persisted as JSON files:

```
{discussions_dir}/
    {discussion_id}.json    # Full Discussion entity
```

Personas are persisted as JSON:

```
{personas_dir}/
    predefined.json         # List of built-in Persona objects
    custom/
        {persona_id}.json   # Individual custom Persona objects
```
