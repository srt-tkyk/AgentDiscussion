"""Shared domain models for Agent Discussion."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Persona:
    """An AI agent persona participating in a discussion."""

    id: str                        # unique slug
    name: str                      # max 100 chars
    description: str               # max 500 chars
    type: str                      # "predefined" | "custom"
    created_at: Optional[datetime] = None


@dataclass
class Message:
    """A single message produced by a persona during a discussion."""

    id: str
    persona_id: str
    persona_name: str              # denormalized for display
    content: str
    turn_number: int               # >= 1
    timestamp: datetime


@dataclass
class DiscussionParameters:
    """Configuration parameters for a discussion session."""

    max_turns: int = 3             # range 1-20
    language: str = "en"
    discussion_style: str = "formal"  # "formal" | "casual" | "debate"
    extended_turns: int = 1        # turns added when continuing


@dataclass
class Discussion:
    """Main aggregate representing an entire discussion session."""

    id: str                        # UUID
    topic: str                     # max 500 chars
    personas: List[Persona]        # 2-6 participants
    messages: List[Message]        # linear order
    parameters: DiscussionParameters
    state: str                     # setup|configuring|executing|completed|exported
    created_at: datetime
    updated_at: datetime
    materials_context: Optional[str] = None   # preprocessed reference text
    resume_point: Optional[dict] = None       # set on API failure


@dataclass
class DiscussionSummary:
    """Lightweight model for the history list."""

    id: str
    topic: str
    persona_names: List[str]
    turn_count: int
    state: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


@dataclass
class ApiValidationResult:
    """Result of API key validation."""

    valid: bool
    error_type: Optional[str] = None    # "auth" | "connection" | None
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Generic validation result with errors and warnings."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
