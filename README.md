# Visera

A full-stack application with Next.js frontend, FastAPI backend, and PostgreSQL database, all containerized with Docker.

## Project Structure

```
visera/
├── app/                    # Next.js frontend (App Router)
├── backend/                # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   └── pyproject.toml     # Python dependencies (pdm)
├── docker-compose.yml      # Docker Compose configuration
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

### Backend (.env in backend/ directory)

```
DATABASE_URL=postgresql://visera_user:visera_password@postgres:5432/visera_db
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend

The frontend will connect to the backend at `http://localhost:8001` by default.

## Next Steps

- [ ] Add authentication endpoints (sign in, sign up)
- [ ] Connect frontend sign-in form to backend API
- [ ] Add password hashing and JWT tokens
- [ ] Add more database models as needed
