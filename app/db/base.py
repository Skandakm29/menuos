"""Declarative base and shared column mixins.

Alembic imports `Base` (and, through `app.models`, every model) from here so
that autogenerate sees the full metadata.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class UUIDPrimaryKeyMixin:
    """Server-generated UUID primary key.

    Uses Postgres `gen_random_uuid()` (pgcrypto / built into PG13+ via
    `pgcrypto`; on PG13+ `gen_random_uuid` is available without the extension).
    Kept as a mixin so every entity gets stable, non-enumerable IDs.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )


class TimestampMixin:
    """created_at / updated_at maintained by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
