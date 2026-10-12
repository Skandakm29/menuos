"""Minimal structured-ish logging setup.

Kept deliberately simple for Milestone 1. Swap for structlog / JSON logs
when there's a real operational need.
"""
from __future__ import annotations

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
