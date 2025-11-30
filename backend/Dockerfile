FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install pdm
RUN pip install --no-cache-dir pdm

# Configure pdm to not use virtual environment (install to system)
ENV PDM_NO_VENV=1
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml pdm.lock* ./

# Install dependencies using pdm (including test dependencies for testing in container)
# Also install with pip as backup to ensure all dependencies are available
RUN pdm install --no-self -G test && \
    python -m pip install --no-cache-dir uvicorn[standard] fastapi sqlalchemy psycopg2-binary python-dotenv pydantic pydantic-settings alembic passlib[bcrypt] email-validator bcrypt==4.2.0 pyjwt==2.9.0 "python-jose[cryptography]==3.3.0" pytest pytest-asyncio pytest-cov httpx faker

# Copy application code
COPY . .

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Run the application
# Cloud Run sets PORT environment variable, default to 8080 for local development
CMD sh -c "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"

