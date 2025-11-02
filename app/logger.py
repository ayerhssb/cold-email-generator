"""Global logger for the project.

Usage:
    from app.logger import logger
    logger.info("message")

Or to get a namespaced logger:
    from app.logger import get_logger
    log = get_logger(__name__)
    log.debug("debug")
"""
from __future__ import annotations

import logging
import sys
from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _make_logger() -> Logger:
    name = "cold-email-generator"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times if module reloaded
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Timed rotating file handler (daily, keep 30 days)
    file_path = LOG_DIR / "app.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(file_path), when="midnight", interval=1, backupCount=30, utc=True
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional: include warnings from third-party libs at INFO or higher
    logging.captureWarnings(True)

    return logger


logger: Logger = _make_logger()


def get_logger(name: str | None = None) -> Logger:
    """Return the global logger or a child logger for the provided name.

    If name is provided, a child logger is returned so logs are namespaced but
    still go to the configured handlers.
    """
    if name:
        return logger.getChild(name)
    return logger


__all__ = ["logger", "get_logger"]
