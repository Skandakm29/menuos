"""Import every model here so Alembic's autogenerate sees full metadata.

`from app.models import *` is not used; Alembic imports this module (via
alembic/env.py) and that import side-effect registers the tables on Base.
"""
from app.models.enums import (  # noqa: F401
    AvailabilityStatus,
    ReviewStatus,
    VerificationStatus,
)
from app.models.menu_item import MenuItem  # noqa: F401
from app.models.restaurant import Restaurant  # noqa: F401

__all__ = [
    "Restaurant",
    "MenuItem",
    "AvailabilityStatus",
    "ReviewStatus",
    "VerificationStatus",
]
