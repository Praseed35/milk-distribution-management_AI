# Milk Distribution Management System

> **DEPRECATED — SUPERSEDED.** This is an early design snapshot (mentions a repository layer and `common/`/`utils/` dirs that were never implemented). The canonical, up-to-date project memory is **`PROJECT_CONTEXT.md`**. Keep this file only as historical reference.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- JWT Authentication
- Pydantic v2

## Architecture (Actual)

app/
    common/
    constants/
    core/
    exceptions/
    models/
    repositories/
    routers/
    schemas/
    services/
    utils/
    database.py
    dependencies.py
    main.py

## Coding Rules

- Business logic belongs in services.
- Routers only validate requests and call services.
- No SQL inside routers.
- No duplicated logic.
- Use dependency injection.
- Every new table requires:
  - SQLAlchemy model
  - Alembic migration
  - Pydantic schemas
  - Service
  - Router
- Use async endpoints where appropriate.
- Follow REST conventions.
- Write reusable code.
- Prefer composition over duplication.

## Current Modules (As of July 2026)

### Implemented ✅
- Authentication
- Users
- Customers
- Routes
- Milk Types
- Employees
- Subscriptions

### In Progress 🔄
- Token Books
- Cash Sales
- Milk Allocation
- Reconciliation

### Planned ❌
- Daily Delivery
- Token Ledger
- Payments
- Reports
- Analytics
- Frontend