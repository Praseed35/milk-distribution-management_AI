# Deployment & Environment

## Purpose

This document defines how the Milk Distribution Management System should be configured, deployed, and managed across different environments.

The goal is to ensure every deployment is reproducible, secure, and consistent.

Every AI assistant must follow these guidelines when adding configuration, environment variables, startup logic, or deployment scripts.

---

# Supported Environments

The project supports multiple environments.

```
Development

↓

Testing

↓

Staging

↓

Production
```

Each environment should use independent configuration.

Never share databases between environments.

---

# Environment Variables

Configuration must come from environment variables.

Never hardcode configuration values.

Typical variables

```
DATABASE_URL

SECRET_KEY

ACCESS_TOKEN_EXPIRE_MINUTES

REFRESH_TOKEN_EXPIRE_MINUTES

ALGORITHM

APP_ENV

DEBUG

LOG_LEVEL

CORS_ORIGINS
```

Sensitive values should never be committed to Git.

---

# .env File

Local development should use

```
.env
```

Example

```env
APP_ENV=development

DATABASE_URL=postgresql://postgres:password@localhost:5432/milk_erp

SECRET_KEY=replace_with_secure_key

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_MINUTES=10080

DEBUG=True

LOG_LEVEL=INFO
```

Production should use environment variables provided by the deployment platform instead of a `.env` file.

---

# Configuration Management

All configuration should be centralized.

```
app/

core/

config.py
```

Configuration should be loaded once during application startup.

Never read environment variables throughout the codebase.

---

# Database Configuration

Use PostgreSQL for all environments.

The application should connect using

```
DATABASE_URL
```

The SQLAlchemy engine should be initialized in a single location.

Never create multiple engines.

---

# Alembic

Schema changes must always be handled through Alembic.

Workflow

```
Modify Models

↓

Generate Migration

↓

Review Migration

↓

Run Migration

↓

Verify Schema
```

Never modify production schemas manually.

---

# Application Startup

Application startup should

- Load configuration
- Initialize database
- Register routers
- Register middleware
- Register exception handlers
- Initialize logging

Startup should not execute business logic.

---

# Application Shutdown

Shutdown should

- Close database resources
- Release external connections
- Flush logs if required

Shutdown should not modify business data.

---

# Logging

Logging should be configurable.

Typical levels

```
DEBUG

INFO

WARNING

ERROR

CRITICAL
```

Production should avoid DEBUG logging.

Sensitive information must never be logged.

---

# Secrets

Secrets include

- JWT secret
- Database password
- API keys
- Third-party credentials

Rules

- Never commit secrets to Git.
- Never expose secrets in logs.
- Rotate secrets periodically.
- Store secrets using the deployment platform's secret manager.

---

# CORS

CORS origins should be configurable.

Development

```
http://localhost:3000

http://localhost:5173
```

Production should allow only trusted domains.

Avoid using

```
*
```

in production.

---

# Static Files

If future modules support uploads

```
documents

images

reports
```

Store uploaded files outside the application code directory.

Never trust client-provided file names.

---

# Health Check

Expose a lightweight endpoint.

Example

```
GET /health
```

Checks may include

- Application status
- Database connectivity

The endpoint should not expose sensitive information.

---

# Production Settings

Production should

- Disable debug mode
- Use HTTPS
- Restrict CORS
- Use strong secrets
- Enable structured logging
- Use connection pooling
- Apply database migrations before serving traffic

---

# Docker (Future)

If Docker is introduced

Recommended services

```
FastAPI

↓

PostgreSQL

↓

Redis (optional)

↓

Nginx (optional)
```

Each service should have a single responsibility.

---

# Backup Strategy

Production databases should be backed up regularly.

Backups should be

- Automated
- Tested
- Securely stored

Recovery procedures should be documented.

---

# Deployment Checklist

Before deployment

✔ Run automated tests

✔ Apply Alembic migrations

✔ Verify environment variables

✔ Verify secrets

✔ Check logging configuration

✔ Validate database connectivity

✔ Confirm API health

After deployment

✔ Verify application startup

✔ Verify authentication

✔ Verify database access

✔ Verify critical business workflows

---

# AI Checklist

Before introducing configuration

✔ Use environment variables

✔ Reuse centralized configuration

✔ Avoid hardcoded values

✔ Keep environments isolated

✔ Preserve startup consistency

Never

- Commit secrets.
- Hardcode credentials.
- Create multiple database engines.
- Modify production schemas manually.
- Enable debug mode in production.

---

# Golden Rule

Deployment should be predictable, repeatable, and secure.

Any developer should be able to deploy the application using the documented configuration without modifying the application code.