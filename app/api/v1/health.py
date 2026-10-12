"""Health endpoint.

Liveness is trivial; readiness checks the DB with a cheap `SELECT 1`. We return
200 with database="unavailable" rather than 503 for Milestone 1 so the route is
easy to probe during setup; tighten to 503-on-DB-down when wiring real
orchestration health checks.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - exercised only when DB down
        logger.warning("Health check DB probe failed: %s", exc)
        db_status = "unavailable"

    return HealthResponse(status="ok", version=__version__, database=db_status)
