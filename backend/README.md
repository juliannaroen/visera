# Visera Backend

FastAPI backend for the Visera application.

## Prerequisites

Install [pdm](https://pdm.fming.dev/):

```bash
# macOS/Linux
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -

# Or via pip
pip install pdm
```

## Setup

1. Install dependencies:

```bash
pdm install
```

2. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

3. Run the development server:

```bash
pdm run dev
# Or: pdm run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

## Adding Dependencies

```bash
# Add a new dependency
pdm add package-name

# Add a dev dependency
pdm add -dG dev package-name
```

## Database Migrations

This project uses Alembic for database migrations.

### Creating a Migration

After modifying models in `models.py`, create a new migration:

```bash
# In Docker
docker exec visera-backend python -m alembic revision --autogenerate -m "Description of changes"

# Locally (if running without Docker)
pdm run alembic revision --autogenerate -m "Description of changes"
```

### Running Migrations

Migrations run automatically when the backend container starts. To run manually:

```bash
# In Docker
docker exec visera-backend python -m alembic upgrade head

# Locally
pdm run alembic upgrade head
```

### Migration Commands

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to base (removes all tables)
alembic downgrade base
```
