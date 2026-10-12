"""MenuItem model.

The trust model is structural, not conventional:

- `price` is nullable. A missing price is NULL, never 0 or a guess.
- `allergens` is a JSONB object, not a list, so we can distinguish
  "no allergen info" (status unknown) from "confirmed contains peanuts".
  An empty list must NEVER imply allergen-free — see AllergenInfo in schemas.
- `availability` defaults to UNKNOWN.
- provenance / confidence / review_status record where data came from and
  whether a human has confirmed it.

Ingredients, dietary tags, customizations and allergens are JSONB blobs whose
shape is validated by Pydantic at the API boundary (see app/schemas). Keeping
them as JSONB for Milestone 1 avoids a sprawl of child tables before we know
the query patterns; they can be normalised into their own tables later if
search requires it.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AvailabilityStatus, ReviewStatus, VerificationStatus


def _pg_enum(py_enum: type, name: str) -> Enum:
    """Build a SQLAlchemy Enum that stores the member VALUE (lowercase) in PG.

    Without values_callable, SQLAlchemy sends the member NAME ("UNKNOWN"), which
    doesn't match the lowercase values the migration created ("unknown").
    """
    return Enum(
        py_enum,
        name=name,
        native_enum=True,
        values_callable=lambda e: [member.value for member in e],
    )

if TYPE_CHECKING:
    from app.models.restaurant import Restaurant


class MenuItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "menu_items"

    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    cuisine: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Nullable on purpose: a missing price is unknown, never assumed.
    price: Mapped["Decimal | None"] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    portion_size: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # JSONB payloads validated by Pydantic at the edge. Defaults chosen so an
    # absent value reads as "unknown", not as an empty/negative assertion.
    #   ingredients:    list[{name, source, confidence}]
    #   dietary_tags:   list[str]  (e.g. ["vegetarian"])
    #   allergens:      {status: confirmed|unverified|unknown, contains: [...], note}
    #   customizations: list[{name, options:[{name, price_delta}]}]
    ingredients: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    dietary_tags: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    allergens: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {"status": "unknown", "contains": [], "note": None},
        server_default='{"status": "unknown", "contains": [], "note": null}',
    )
    customizations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )

    availability: Mapped[AvailabilityStatus] = mapped_column(
        _pg_enum(AvailabilityStatus, "availability_status"),
        nullable=False,
        default=AvailabilityStatus.UNKNOWN,
        server_default=AvailabilityStatus.UNKNOWN.value,
    )

    # Provenance & trust
    menu_source: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source_file_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_verified_at: Mapped["datetime | None"] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_status: Mapped[VerificationStatus] = mapped_column(
        _pg_enum(VerificationStatus, "verification_status"),
        nullable=False,
        default=VerificationStatus.UNKNOWN,
        server_default=VerificationStatus.UNKNOWN.value,
    )
    review_status: Mapped[ReviewStatus] = mapped_column(
        _pg_enum(ReviewStatus, "review_status"),
        nullable=False,
        default=ReviewStatus.PENDING,
        server_default=ReviewStatus.PENDING.value,
    )
    # 0.0–1.0 overall record confidence. Nullable = not scored.
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    # Free-form provenance, e.g. {"extractor": "pymupdf", "page": 2, ...}
    provenance: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )

    restaurant: Mapped["Restaurant"] = relationship(back_populates="menu_items")

    __table_args__ = (
        CheckConstraint("price IS NULL OR price >= 0", name="ck_menu_items_price_nonneg"),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_menu_items_confidence_range",
        ),
        Index("ix_menu_items_restaurant_name", "restaurant_id", "name"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<MenuItem id={self.id} name={self.name!r} price={self.price}>"
