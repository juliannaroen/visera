# Visera

A full-stack application with Next.js frontend, FastAPI backend, and PostgreSQL database, all containerized with Docker.

## Project Structure

```
visera/
├── app/                   # Next.js frontend (App Router)
├── backend/               # FastAPI backend
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Frontend Dockerfile
└── backend/Dockerfile     # Backend Dockerfile
```

## Quick Start with Docker

1. **Start all services:**

   ```bash
   docker-compose up --build
   ```

2. **Access the services:**

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs
   - PostgreSQL: localhost:5432

3. **Stop all services:**

   ```bash
   docker-compose down
   ```

4. **Stop and remove volumes (clean database):**
   ```bash
   docker-compose down -v
   ```

## Development Setup (Without Docker)

### Frontend

```bash
pnpm install
pnpm dev
```

### Backend

**Prerequisites:** Install [pdm](https://pdm.fming.dev/)

```bash
cd backend
pdm install
pdm run dev
# Or: pdm run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database

Make sure PostgreSQL is running locally, then update the `DATABASE_URL` in `backend/.env`.

## Environment Variables

### Backend

The backend requires the following environment variables. Create a `.env` file in the `backend/` directory:

**Required Variables:**

```bash
# Authentication
AUTH_COOKIE_NAME=dev.sid                    # Session cookie name
AUTH_COOKIE_MAX_AGE=3600                    # Cookie max age in seconds
JWT_SECRET_KEY=your-secret-key-here          # Secret key for JWT tokens
JWT_EXPIRE_MINUTES=30                       # JWT token expiration time

# Database
DATABASE_URL=postgresql://visera_user:visera_password@postgres:5432/visera_db

# Email (for OTP verification)
SMTP_HOST=smtp.gmail.com                     # SMTP server host
SMTP_PORT=587                                # SMTP server port
SMTP_USER=your-email@gmail.com              # SMTP username
SMTP_PASSWORD=your-app-password              # SMTP password
SMTP_FROM_EMAIL=noreply@visera.com          # From email address

# Application
FRONTEND_URL=http://localhost:3000          # Frontend URL for CORS
ALLOWED_ORIGINS=http://localhost:3000        # Comma-separated allowed origins
ENVIRONMENT=development                      # Environment (development/production)
```

**For Docker Compose:**

The `DATABASE_URL` in docker-compose.yml will be automatically loaded. For other variables, you can either:

- Set them in `docker-compose.yml` under the `backend` service `environment` section
- Create a `.env` file in the project root (docker-compose will load it)

**For Google Cloud SQL:**

```bash
DATABASE_URL=postgresql://user:password@cloud-sql-ip:5432/database?sslmode=require
```

### Frontend

The frontend will connect to the backend at `http://localhost:8001` by default. No environment variables are required for the frontend.

## Features

- ✅ User authentication (sign up, login, logout)
- ✅ Email verification with OTP codes
- ✅ JWT-based session management with httpOnly cookies
- ✅ Protected routes and API endpoints
- ✅ User account management (view profile, delete account)
- ✅ GDPR-compliant soft deletion for account deletion
- ✅ Password hashing with bcrypt
- ✅ CORS configuration for cross-origin requests
