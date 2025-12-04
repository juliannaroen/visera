# Visera

A full-stack application with Next.js frontend, FastAPI backend, and PostgreSQL database, all containerized with Docker.

https://visera.app

## Project Structure

```
visera/
├── app/                   # Next.js frontend (App Router)
├── backend/               # FastAPI backend
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Frontend Dockerfile
└── backend/Dockerfile     # Backend Dockerfile
```

## Features

- ✅ User authentication (sign up, login, logout)
- ✅ Email verification with OTP codes
- ✅ JWT-based session management with httpOnly cookies
- ✅ Protected routes and API endpoints
- ✅ User account management (view profile, delete account)
- ✅ GDPR-compliant soft deletion for account deletion
- ✅ Password hashing with bcrypt
- ✅ CORS configuration for cross-origin requests

## Running app with Docker

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

### Running Tests

```bash
# Run all tests
pnpm test:backend

# Run with coverage
pnpm test:backend:cov

# Run specific test file (pass arguments)
pnpm test:backend -- tests/unit/models/test_user.py
```

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
- [ ] Implement email change functionality with verification
- [ ] Add two-factor authentication (2FA) support
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
- [ ] Send emails asynchronously via a message queue
- [ ] Implement caching layer (Redis) for frequently accessed data
- [ ] Add database connection pooling optimization
- [ ] Implement API response pagination for list endpoints
- [ ] Add CDN for static assets
- [ ] Optimize frontend bundle size and code splitting
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
- [ ] Add database seeding scripts for development
- [ ] Improve error messages and debugging information
- [ ] Add development tools (React DevTools, Redux DevTools if needed)

### Infrastructure & DevOps

- [ ] Set up automated database backups
- [ ] Add staging environment configuration
- [ ] Set up monitoring dashboards (Grafana, DataDog, etc.)
- [ ] Implement automated rollback procedures
- [ ] Set up automated security scanning in CI/CD
- [ ] Add database migration rollback testing
- [ ] Implement feature flags for gradual rollouts

### Features & Functionality

- [ ] Add user dashboard with analytics/metrics
- [ ] Add file upload functionality with validation
- [ ] Implement search functionality
- [ ] Add data export functionality (GDPR compliance)
- [ ] Create admin panel for user management
- [ ] Add user preferences and settings management
