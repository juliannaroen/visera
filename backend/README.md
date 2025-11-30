# Visera Backend

FastAPI backend for the Visera application.

## Project Structure

The backend follows a feature-based architecture with clear separation of concerns:

```
backend/
├── main.py                # FastAPI app setup, CORS, router registration
├── api/                   # API layer
│   ├── deps.py            # Shared dependencies (get_current_user, etc.)
│   └── v1/                # API version 1
│       ├── auth.py        # Authentication routes (/auth/*)
│       └── users.py       # User routes (/users/*)
├── core/                  # Core utilities and configuration
│   ├── config.py          # Application configuration (CORS, etc.)
│   ├── database.py        # Database setup and session management
│   └── security.py        # JWT and password hashing utilities
├── models/                # SQLAlchemy database models
│   └── user.py            # User model
├── schemas/               # Pydantic schemas for request/response validation
│   ├── auth.py            # Authentication schemas (LoginRequest, LoginResponse)
│   └── user.py            # User schemas (UserCreate, UserResponse)
└── services/              # Business logic layer
    ├── auth_service.py    # Authentication business logic
    └── user_service.py    # User business logic
```

### Architecture Overview

- **API Layer** (`api/`): FastAPI routers that handle HTTP requests/responses
- **Services Layer** (`services/`): Business logic separated from HTTP concerns
- **Models** (`models/`): SQLAlchemy ORM models representing database tables
- **Schemas** (`schemas/`): Pydantic models for request validation and response serialization
- **Core** (`core/`): Shared utilities, configuration, and infrastructure code

This structure makes it easy to:

- Add new features (create new routers, services, models, schemas)
- Test business logic independently of HTTP layer
- Maintain clear separation of concerns
- Scale as the application grows

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

## Testing

This project uses pytest for testing with a comprehensive test structure.

### Test Structure

```
tests/
├── unit/              # Unit tests (no database)
│   └── models/       # Model tests
├── integration/       # Integration tests (with database)
├── fixtures/          # Test data factories
└── utils/             # Test utilities
```

### Running Tests

#### Local Development (Recommended for fast iteration)

**Option 1: From project root (recommended)**

```bash
# Run all tests
pnpm test:backend

# Run with coverage
pnpm test:backend:cov

# Run specific test file (pass arguments)
pnpm test:backend -- tests/unit/models/test_user.py
```

**Option 2: From backend directory**

```bash
cd backend

# Run all tests
pdm run test

# Run with coverage report
pdm run test-cov

# Run specific test file
pdm run pytest tests/unit/models/test_user.py

# Run with verbose output
pdm run pytest -v
```

#### Docker (Matches production environment)

```bash
# Make sure backend container is running
docker-compose up -d backend

# Run tests in the container (using system Python since PDM_NO_VENV=1)
docker exec visera-backend python -m pytest tests/

# Run with coverage
docker exec visera-backend python -m pytest --cov=. --cov-report=term tests/

# Or use pdm (if test dependencies are installed)
docker exec visera-backend pdm run test
```

**Note**: The Dockerfile installs test dependencies, but uses `PDM_NO_VENV=1` (system Python). Use `python -m pytest` directly for more reliable execution in Docker.

### Test Dependencies

Test dependencies are installed as an optional dependency group:

```bash
# Install test dependencies (if not already installed)
pdm install -G test
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test API endpoints with database
- **Fixtures**: Use `tests/fixtures/factories.py` for test data
- **Database**: Tests use in-memory SQLite (fast, isolated)

Example test structure:

```python
# tests/unit/models/test_user.py
def test_user_creation(test_session):
    user = User(email="test@example.com", ...)
    test_session.add(user)
    test_session.commit()
    assert user.id is not None
```

## GCP Cloud Run Configuration

This application is deployed to Google Cloud Platform (GCP) Cloud Run. All environment variables and secrets are managed in GCP, not in the deployment workflow.

### Setting Environment Variables in GCP Cloud Run

1. **Go to Cloud Run Console:**

   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Go to **Cloud Run** → Select your service (`visera-backend`)

2. **Edit Service:**

   - Click **"Edit & Deploy New Revision"**
   - Go to the **"Variables & Secrets"** tab

3. **Add Environment Variables:**

   - Click **"Add Variable"**
   - Enter the variable name and value
   - For non-sensitive values (like `ENVIRONMENT`, `PORT`, `SMTP_HOST`), enter directly

4. **Add Secrets (Recommended for Sensitive Data):**
   - Click **"Reference a secret"**
   - Select **"Create a new secret"** or choose existing secret
   - Enter secret name (e.g., `jwt-secret-key`)
   - Enter secret value
   - Choose version (use `latest` for automatic updates)
   - Set environment variable name (e.g., `JWT_SECRET_KEY`)

### Managing Secrets in GCP Secret Manager

#### Creating a Secret

**Option 1: Via Cloud Console**

1. Go to **Secret Manager** in GCP Console
2. Click **"Create Secret"**
3. Enter secret name (e.g., `jwt-secret-key`)
4. Enter secret value
5. Click **"Create Secret"**

**Option 2: Via gcloud CLI**

```bash
# Create a secret
echo -n "your-secret-value" | gcloud secrets create jwt-secret-key \
  --data-file=- \
  --replication-policy="automatic"

# Or create from a file
gcloud secrets create database-url \
  --data-file=path/to/database-url.txt \
  --replication-policy="automatic"
```

#### Reading a Secret

**Via gcloud CLI:**

```bash
# Read secret value
gcloud secrets versions access latest --secret="jwt-secret-key"

# List all secrets
gcloud secrets list

# View secret metadata
gcloud secrets describe jwt-secret-key
```

**Via Cloud Console:**

1. Go to **Secret Manager**
2. Click on the secret name
3. Click **"View Secret Value"** (requires appropriate permissions)

#### Updating a Secret

**Via gcloud CLI:**

```bash
# Create a new version of the secret
echo -n "new-secret-value" | gcloud secrets versions add jwt-secret-key \
  --data-file=-

# The latest version will be automatically used by Cloud Run
```

**Via Cloud Console:**

1. Go to **Secret Manager** → Select secret
2. Click **"Add New Version"**
3. Enter new value
4. Cloud Run will use the latest version automatically

#### Granting Access to Secrets

Cloud Run service account needs Secret Manager Secret Accessor role:

```bash
# Get your service account email
SERVICE_ACCOUNT="visera-backend@PROJECT_ID.iam.gserviceaccount.com"

# Grant access
gcloud secrets add-iam-policy-binding jwt-secret-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

Or via Cloud Console:

1. Go to **Secret Manager** → Select secret
2. Click **"Permissions"** tab
3. Click **"Grant Access"**
4. Add service account with **Secret Manager Secret Accessor** role

### Verifying Configuration

After setting environment variables and secrets:

1. **Check in Cloud Run:**

   - Go to your service → **"Revisions"** tab
   - Click on latest revision
   - View **"Environment Variables"** section

2. **Check via gcloud CLI:**

```bash
gcloud run services describe visera-backend \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

3. **Test in Application:**
   - Check application logs for any missing variable errors
   - The application will raise clear errors if required variables are missing

## Database Migrations

This project uses Alembic for database migrations.

### Creating a Migration

After modifying models in `models/`, create a new migration:

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
