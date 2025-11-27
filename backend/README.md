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
