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

## TODO: Improvements

This section outlines potential improvements and enhancements for the application.

### Testing & Quality

- [ ] Add frontend testing infrastructure (Jest, React Testing Library, Playwright)
- [ ] Add E2E tests for critical user flows (signup, login, email verification)
- [ ] Increase backend test coverage (currently has good coverage, but can expand edge cases)
- [ ] Add visual regression testing
- [ ] Set up pre-commit hooks with linting and formatting checks

### Security

- [ ] Implement rate limiting on authentication endpoints (login, signup, OTP verification)
- [ ] Implement security headers middleware (HSTS, X-Frame-Options, CSP, etc.)
- [ ] Add password strength meter and enhanced password validation
- [ ] Add account lockout after multiple failed login attempts
- [ ] Add input sanitization for XSS prevention
- [ ] Regular security dependency audits (Dependabot, Snyk)

### Authentication & User Management

- [ ] Add password reset functionality (forgot password flow)
- [ ] Add resend OTP email functionality
- [ ] Implement email change functionality with verification
- [ ] Add two-factor authentication (2FA) support
- [ ] Implement "Remember me" functionality with longer-lived tokens
- [ ] Add social authentication (OAuth with Google, GitHub, etc.)
- [ ] Implement session management (view active sessions, revoke sessions)

### Logging & Monitoring

- [ ] Replace print statements with structured logging (Python logging module or structlog)
- [ ] Add centralized logging solution (e.g., Cloud Logging, ELK stack)
- [ ] Implement error tracking and monitoring (Sentry, Rollbar, etc.)
- [ ] Add application performance monitoring (APM)
- [ ] Create health check endpoints with detailed status (database, email service, etc.)
- [ ] Add request/response logging middleware with correlation IDs
- [ ] Implement audit logging for sensitive operations (account deletion, password changes, etc.)

### Performance & Scalability

- [ ] Add database query optimization and indexing analysis
- [ ] Implement caching layer (Redis) for frequently accessed data
- [ ] Add database connection pooling optimization
- [ ] Implement API response pagination for list endpoints
- [ ] Add CDN for static assets
- [ ] Optimize frontend bundle size and code splitting
- [ ] Implement lazy loading for images and components
- [ ] Add database read replicas for read-heavy operations

### User Experience

- [ ] Add loading states and skeleton screens for better UX
- [ ] Implement toast notifications for user feedback
- [ ] Add form validation with real-time feedback
- [ ] Implement dark mode support
- [ ] Add accessibility improvements (ARIA labels, keyboard navigation, screen reader support)
- [ ] Improve mobile responsiveness and touch interactions
- [ ] Add internationalization (i18n) support for multiple languages
- [ ] Implement progressive web app (PWA) features
- [ ] Add offline support and service workers

### Developer Experience

- [ ] Add API documentation improvements (OpenAPI/Swagger enhancements)
- [ ] Create development environment setup script
- [ ] Add database seeding scripts for development
- [ ] Improve error messages and debugging information
- [ ] Add development tools (React DevTools, Redux DevTools if needed)
- [ ] Create comprehensive API examples and Postman collection
- [ ] Add environment variable validation on startup
- [ ] Improve Docker development workflow (hot reload, faster builds)

### Infrastructure & DevOps

- [ ] Set up automated database backups
- [ ] Implement blue-green deployment strategy
- [ ] Add staging environment configuration
- [ ] Set up monitoring dashboards (Grafana, DataDog, etc.)
- [ ] Implement automated rollback procedures
- [ ] Add infrastructure as code (Terraform, Pulumi)
- [ ] Set up automated security scanning in CI/CD
- [ ] Add database migration rollback testing
- [ ] Implement feature flags for gradual rollouts

### Features & Functionality

- [ ] Add user dashboard with analytics/metrics
- [ ] Implement notification system (in-app and email)
- [ ] Add file upload functionality with validation
- [ ] Implement search functionality
- [ ] Add data export functionality (GDPR compliance)
- [ ] Create admin panel for user management
- [ ] Add user preferences and settings management
- [ ] Implement activity feed or audit log viewer
