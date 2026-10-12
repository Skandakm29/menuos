"""Pytest fixtures.

Runs the suite against a real Postgres test database (TEST_DATABASE_URL),
applying Alembic migrations once per session so tests exercise the same schema
production will use — not a create_all() approximation.

Skips the whole suite with a clear message if the test DB is unreachable, so a
missing Postgres is an obvious "start the DB" rather than a wall of errors.
"""
from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _test_db_url() -> str:
    settings = get_settings()
    if settings.test_database_url:
        return settings.test_database_url
    # Fall back to main DB name + "_test".
    return settings.sqlalchemy_url.rsplit("/", 1)[0] + "/menuos_test"


TEST_DB_URL = _test_db_url()


def _db_reachable(url: str) -> bool:
    try:
        eng = create_engine(url)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def _migrated_db() -> Generator[None, None, None]:
    if not _db_reachable(TEST_DB_URL):
        pytest.skip(
            f"Test database not reachable at {TEST_DB_URL!r}. "
            "Start Postgres (docker compose up -d) and create menuos_test."
        )

    cfg = Config("alembic.ini")
    cfg.set_main_option("script_location", "alembic")
    # env.py reads ALEMBIC_DATABASE_URL first.
    os.environ["ALEMBIC_DATABASE_URL"] = TEST_DB_URL

    command.downgrade(cfg, "base")  # clean slate if a prior run left tables
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(TEST_DB_URL, future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient with get_db overridden to use the test session."""
    from app.db.session import get_db
    from app.main import app

    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
