"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        description="AI-readable restaurant menu infrastructure.",
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {
            "name": settings.project_name,
            "version": __version__,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    logger.info("%s v%s started (env=%s)", settings.project_name, __version__, settings.env)
    return app


app = create_app()
