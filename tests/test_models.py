"""Schema-level guarantees for the trust model.

These assert the DB enforces the invariants the product depends on, so a later
refactor can't quietly weaken them.
"""
from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MenuItem, Restaurant
from app.models.enums import AvailabilityStatus, ReviewStatus, VerificationStatus


def _restaurant(db: Session) -> Restaurant:
    r = Restaurant(name="Test Darshini", city="Bengaluru", cuisine="South Indian")
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_defaults_express_unknown_not_assumptions(db_session: Session) -> None:
    r = _restaurant(db_session)
    item = MenuItem(restaurant_id=r.id, name="Masala Dosa")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    # A brand-new item asserts nothing it wasn't told.
    assert item.price is None
    assert item.availability == AvailabilityStatus.UNKNOWN
    assert item.verification_status == VerificationStatus.UNKNOWN
    assert item.review_status == ReviewStatus.PENDING
    assert item.ingredients == []
    # Empty allergen list must NOT read as allergen-free.
    assert item.allergens == {"status": "unknown", "contains": [], "note": None}
    assert item.confidence is None


def test_negative_price_rejected(db_session: Session) -> None:
    r = _restaurant(db_session)
    db_session.add(MenuItem(restaurant_id=r.id, name="Bad", price=-5))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_confidence_out_of_range_rejected(db_session: Session) -> None:
    r = _restaurant(db_session)
    db_session.add(MenuItem(restaurant_id=r.id, name="Bad", confidence=1.5))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_cascade_delete(db_session: Session) -> None:
    r = _restaurant(db_session)
    db_session.add(MenuItem(restaurant_id=r.id, name="Idli"))
    db_session.commit()

    db_session.delete(r)
    db_session.commit()

    assert db_session.query(MenuItem).filter_by(restaurant_id=r.id).count() == 0
