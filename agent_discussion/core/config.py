"""Configuration management."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from agent_discussion.core.exceptions import ConfigError

logger = logging.getLogger(__name__)


def ensure_gitignore() -> None:
    """Auto-add config.yaml to .gitignore if not already present."""
    gitignore = Path(".gitignore")
    entry = "config.yaml\n"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if "config.yaml" not in content:
            with gitignore.open("a", encoding="utf-8") as f:
                f.write(entry)
            logger.info("Added config.yaml to .gitignore")
    else:
        gitignore.write_text(entry, encoding="utf-8")
        logger.info("Created .gitignore with config.yaml entry")


class ConfigurationManager:
    """Loads and validates application configuration from config.yaml."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        self._path = Path(config_path)
        self._data: dict = {}

    def load(self) -> None:
        """Load and validate config. Raises ConfigError on failure."""
        if not self._path.exists():
            raise ConfigError(
                f"{self._path} not found. "
                "Copy config.yaml.example to config.yaml and set your API key."
            )
        try:
            with self._path.open(encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse {self._path}: {e}") from e

        self._validate()
        logger.info("Configuration loaded from %s", self._path)

    def _validate(self) -> None:
        api_key = self._data.get("anthropic", {}).get("api_key", "")
        if not api_key or api_key == "YOUR_ANTHROPIC_API_KEY_HERE":
            raise ConfigError(
                "anthropic.api_key is missing or not set in config.yaml"
            )

    def get_api_key(self) -> str:
        """Return the Anthropic API key."""
        return self._data["anthropic"]["api_key"]

    def get(self, *keys: str, default: Any = None) -> Any:
        """Traverse nested keys and return the value, or default if not found."""
        node = self._data
        for k in keys:
            if not isinstance(node, dict):
                return default
            node = node.get(k, default)
        return node
