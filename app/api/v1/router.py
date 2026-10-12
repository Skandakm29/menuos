"""Aggregates all v1 routers. Milestone 2 adds restaurants/menu-items here."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()
api_router.include_router(health.router)
