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

# Install dependencies using pdm
RUN pdm install --prod --no-self && \
    # Ensure uvicorn is available in PATH
    python -m pip install --no-cache-dir uvicorn[standard] fastapi sqlalchemy psycopg2-binary python-dotenv pydantic pydantic-settings alembic passlib[bcrypt] email-validator bcrypt==4.2.0

# Copy application code
COPY . .

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8001

# Run the application
# Cloud Run sets PORT environment variable, default to 8001 for local development
# Use sh -c to properly expand the environment variable
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"

