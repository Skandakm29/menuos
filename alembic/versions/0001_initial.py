"""initial: restaurants and menu_items

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-12
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Each enum is referenced by exactly one column below, so we let the CREATE
# TABLE emit the CREATE TYPE (checkfirst via create_type default). We create
# them explicitly up front anyway with checkfirst=True for an unambiguous
# ordering, then pass create_type=False on the columns so the type isn't
# created twice.
availability_status = postgresql.ENUM(
    "available", "unavailable", "unknown", name="availability_status"
)
verification_status = postgresql.ENUM(
    "confirmed", "unverified", "unknown", name="verification_status"
)
review_status = postgresql.ENUM(
    "pending", "in_review", "approved", "rejected", name="review_status"
)

# Column-bound references that must NOT re-create the type.
availability_col = postgresql.ENUM(
    "available", "unavailable", "unknown",
    name="availability_status", create_type=False,
)
verification_col = postgresql.ENUM(
    "confirmed", "unverified", "unknown",
    name="verification_status", create_type=False,
)
review_col = postgresql.ENUM(
    "pending", "in_review", "approved", "rejected",
    name="review_status", create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    # gen_random_uuid() lives in pgcrypto on older PGs; harmless if already there.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    availability_status.create(bind, checkfirst=True)
    verification_status.create(bind, checkfirst=True)
    review_status.create(bind, checkfirst=True)

    op.create_table(
        "restaurants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("cuisine", sa.String(length=100), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("contact_phone", sa.String(length=32), nullable=True),
        sa.Column("contact_email", sa.String(length=320), nullable=True),
        sa.Column("owner_email", sa.String(length=320), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_restaurants_city", "restaurants", ["city"])
    op.create_index("ix_restaurants_cuisine", "restaurants", ["cuisine"])
    op.create_index("ix_restaurants_owner_email", "restaurants", ["owner_email"])

    op.create_table(
        "menu_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("restaurant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("cuisine", sa.String(length=120), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("portion_size", sa.String(length=120), nullable=True),
        sa.Column(
            "ingredients",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "dietary_tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "allergens",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='{"status": "unknown", "contains": [], "note": null}',
        ),
        sa.Column(
            "customizations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "availability",
            availability_col,
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("menu_source", sa.String(length=300), nullable=True),
        sa.Column("source_file_ref", sa.String(length=500), nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "verification_status",
            verification_col,
            nullable=False,
            server_default="unknown",
        ),
        sa.Column(
            "review_status",
            review_col,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column(
            "provenance",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint("price IS NULL OR price >= 0", name="ck_menu_items_price_nonneg"),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_menu_items_confidence_range",
        ),
    )
    op.create_index("ix_menu_items_restaurant_id", "menu_items", ["restaurant_id"])
    op.create_index("ix_menu_items_category", "menu_items", ["category"])
    op.create_index(
        "ix_menu_items_restaurant_name", "menu_items", ["restaurant_id", "name"]
    )


def downgrade() -> None:
    op.drop_index("ix_menu_items_restaurant_name", table_name="menu_items")
    op.drop_index("ix_menu_items_category", table_name="menu_items")
    op.drop_index("ix_menu_items_restaurant_id", table_name="menu_items")
    op.drop_table("menu_items")

    op.drop_index("ix_restaurants_owner_email", table_name="restaurants")
    op.drop_index("ix_restaurants_cuisine", table_name="restaurants")
    op.drop_index("ix_restaurants_city", table_name="restaurants")
    op.drop_table("restaurants")

    bind = op.get_bind()
    review_status.drop(bind, checkfirst=True)
    verification_status.drop(bind, checkfirst=True)
    availability_status.drop(bind, checkfirst=True)
