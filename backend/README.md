# Visera Backend

FastAPI backend for the Visera application.

## Directory Structure

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

## Database Migrations

This project uses Alembic for database migrations.

### Creating a Migration

After modifying models in `models/`, create a new migration:

```bash
docker exec visera-backend python -m alembic revision --autogenerate -m "Description of changes"
```

### Running Migrations

Migrations run automatically when the backend container starts. To run manually:

```bash
docker exec visera-backend python -m alembic upgrade head
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
