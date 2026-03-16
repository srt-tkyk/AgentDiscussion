"""Claude API integration — streaming discussion responses."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generator

import anthropic

if TYPE_CHECKING:
    from agent_discussion.core.models import Discussion, Persona

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
_MAX_TOKENS = 1024


class DiscussionEngine:
    """Generates streaming responses from Claude for each persona turn."""

    def __init__(self, api_key: str, model: str = _DEFAULT_MODEL) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def stream_response(
        self, persona: "Persona", context: dict
    ) -> Generator[str, None, None]:
        """Yield text chunks for a persona's turn in the discussion.

        Args:
            persona: The persona whose response is being generated.
            context: Dict with keys: topic, style, language, materials, history.
        """
        system_prompt = self._build_system_prompt(persona, context)
        user_message = self._build_user_message(context)

        logger.debug(
            "Streaming response for persona %s (turn context: %d messages)",
            persona.name,
            len(context.get("history", [])),
        )

        with self._client.messages.stream(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _build_system_prompt(self, persona: "Persona", context: dict) -> str:
        parts = [
            f"You are {persona.name}. {persona.description}",
            f"Engage in a {context['style']} discussion in {context['language']}.",
            "Stay in character. Contribute meaningfully to the conversation.",
        ]
        if context.get("materials"):
            parts.append(f"\nReference material:\n{context['materials']}")
        return "\n".join(parts)

    def _build_user_message(self, context: dict) -> str:
        history = context.get("history", [])
        if history:
            history_text = "\n".join(
                f"{entry['persona']}: {entry['content']}" for entry in history
            )
            return (
                f"Topic: {context['topic']}\n\n"
                f"Discussion so far:\n{history_text}\n\n"
                "Your response:"
            )
        return f"Topic: {context['topic']}\n\nStart the discussion with your opening statement:"
