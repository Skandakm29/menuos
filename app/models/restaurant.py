"""Restaurant (tenant) model.

Designed so multi-tenant auth can be layered on later: each restaurant is the
tenant boundary, and `owner_email` is a placeholder for the eventual link to
an auth/users table. No auth is enforced yet (Milestone 1).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem


class Restaurant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "restaurants"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    cuisine: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # ISO 4217 currency code (e.g. "INR"). Default to INR for the Bengaluru launch.
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)

    # Placeholder tenancy hook. Becomes a FK to a users/accounts table in the
    # auth milestone. Nullable for now so Milestone 1 can create restaurants freely.
    owner_email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)

    menu_items: Mapped[list["MenuItem"]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Restaurant id={self.id} name={self.name!r}>"
