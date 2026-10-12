"""Controlled vocabularies used across models and schemas.

These three distinctions are the heart of the product's trust model:

- AvailabilityStatus: never silently assume a dish is available.
- VerificationStatus: confirmed vs imported-unverified vs unknown.
- ReviewStatus: has a human at the restaurant looked at this yet.

Plain `str, Enum` so the same members are shared by SQLAlchemy and Pydantic.
"""
from __future__ import annotations

from enum import Enum


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"  # default — absence of info is not "available"


class VerificationStatus(str, Enum):
    """Applies to a field or record: how much do we trust this value?"""

    CONFIRMED = "confirmed"      # a human at the restaurant confirmed it
    UNVERIFIED = "unverified"    # imported/extracted, not yet confirmed
    UNKNOWN = "unknown"          # we have no information


class ReviewStatus(str, Enum):
    """Workflow state of a record awaiting restaurant review."""

    PENDING = "pending"        # created by ingestion, not yet reviewed
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
