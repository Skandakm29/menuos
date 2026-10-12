# MenuOS

AI-readable restaurant menu infrastructure. B2B: restaurants supply menus; we
turn them into validated, structured, searchable data that authorized AI agents
and apps consume through an API.

**Milestone 1 (this commit):** FastAPI + PostgreSQL + SQLAlchemy 2.x + Alembic
foundation, with the restaurant/menu-item data model, a health endpoint, and
tests. No auth and no CRUD endpoints yet — those are Milestone 2.

## Requirements

- Python 3.11+
- PostgreSQL 14+ (16 recommended). A Docker compose file is included.

## Setup

```bash
cd menuos
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # adjust if your Postgres differs

# Start Postgres (creates both menuos and menuos_test):
docker compose up -d

# Apply migrations:
alembic upgrade head

# Run the API:
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/            → service info
- http://127.0.0.1:8000/docs        → interactive OpenAPI docs
- http://127.0.0.1:8000/api/v1/health → health + DB probe

## Tests

```bash
pytest
```

Tests run against `TEST_DATABASE_URL` (default `menuos_test`), applying the real
Alembic migrations. If Postgres isn't running, the suite **skips** with a clear
message rather than failing confusingly.

## Project layout

```
app/
  main.py              FastAPI app factory
  core/                config, logging
  db/                  engine/session, declarative base + mixins
  models/              SQLAlchemy models (restaurant, menu_item, enums)
  schemas/             Pydantic schemas
  api/v1/              routers (health now; CRUD in M2)
alembic/               migrations (0001_initial)
tests/                 pytest + API/schema tests
```

## Design notes

- **PostgreSQL-first.** The trust model uses JSONB and native enums; SQLite is
  not used, even in tests, to avoid schema drift.
- **Absence ≠ assertion.** `price` is nullable; `availability`,
  `verification_status` default to `unknown`; an empty allergen list never means
  allergen-free (allergens carry an explicit `status`).
- **Migrations, not create_all.** Alembic is the schema source of truth.

## Not production-ready

No auth, tenant isolation, rate limiting, upload handling, or hardened health
semantics yet. The dev server running is not a production signal.
# menuos
