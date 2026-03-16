"""Application logging configuration."""
import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_dir: str = "logs", level: str = "INFO") -> None:
    """Configure RotatingFileHandler. Call once at app startup."""
    Path(log_dir).mkdir(exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/agent_discussion.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not root.handlers:
        root.addHandler(handler)
