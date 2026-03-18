"""API key validation against Anthropic."""
from __future__ import annotations

import logging

import anthropic

from agent_discussion.core.models import ApiValidationResult

logger = logging.getLogger(__name__)


class ApiValidator:
    """Validates an Anthropic API key by calling models.list()."""

    def validate(self, api_key: str) -> ApiValidationResult:
        """Return ApiValidationResult indicating whether the key is valid."""
        try:
            client = anthropic.Anthropic(api_key=api_key, timeout=10.0)
            client.models.list()
            logger.info("API key validated successfully")
            return ApiValidationResult(valid=True)
        except anthropic.AuthenticationError as e:
            logger.error("API key authentication failed: %s", e)
            return ApiValidationResult(
                valid=False,
                error_type="auth",
                error_message="Invalid API key. Please check config.yaml.",
            )
        except Exception as e:
            logger.error("API validation connection error: %s", e)
            return ApiValidationResult(
                valid=False,
                error_type="connection",
                error_message=(
                    "Could not reach Anthropic API. Check your internet connection."
                ),
            )
