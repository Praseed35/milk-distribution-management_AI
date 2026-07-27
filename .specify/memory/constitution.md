<!-- Sync Impact Report
Version change: 0.0.0 → 1.0.0
Modified principles: N/A (initial creation)
Added sections: Core Principles (5), Technology Stack, Architecture Standards, Security Requirements, Development Workflow, Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
Follow-up TODOs: None
-->

# Milk Management AI Constitution

## Core Principles

### I. Layered Architecture (NON-NEGOTIABLE)

Every feature MUST follow the established layered architecture:

- **Routers** (`app/routers/`) handle HTTP concerns only — request parsing, response formatting, status codes. Routers MUST NOT contain business logic.
- **Services** (`app/services/`) contain all business logic and orchestration. Services MUST NOT import request/response objects directly.
- **Models** (`app/models/`) define SQLAlchemy ORM entities and table schemas. Models MUST NOT contain business logic.
- **Schemas** (`app/schemas/`) define Pydantic v2 request/response contracts. Schemas MUST NOT contain database operations.
- **Core** (`app/core/`) holds cross-cutting concerns: authentication, configuration, security, roles.

New domains MUST be added as new files in each layer following the existing naming convention (e.g., `customer.py` across models, schemas, services, routers).

### II. Role-Based Access Control (NON-NEGOTIABLE)

All endpoints MUST be protected by authentication and authorized by role. The system uses four roles defined in `app/core/roles.py`:

- **OWNER** — full system access, can manage users, employees, routes, customers, and all operational data.
- **ADMIN** — operational access to manage customers, subscriptions, routes, and delivery exceptions.
- **CHECKER** — read-only access to verify data quality and confirm deliveries.
- **DELIVERY_PARTNER** — limited access to delivery-related operations and route data.

Endpoints MUST use the `get_current_user` dependency from `app/core/auth.py` and MUST check `user.role` against the required permission. Never expose unprotected endpoints.

### III. Test-First Development

All new features MUST include tests. Tests MUST be written before or alongside implementation:

- Each router MUST have a corresponding test file in `tests/test_<domain>.py`.
- Tests MUST cover: successful operations, authentication failures (401), authorization failures (403), validation errors (422), and not-found cases (404).
- Use `conftest.py` fixtures for database sessions and test clients.
- Run `pytest` before committing to ensure no regressions.

### IV. Data Integrity and Soft Deletes

All entity records MUST use soft deletion (`is_active` flag) rather than hard deletes. This preserves referential integrity and audit trails:

- DELETE endpoints MUST set `is_active = False`, never remove rows.
- List endpoints MUST filter by `is_active = True` by default.
- Foreign key relationships MUST use `ON DELETE SET NULL` or `ON DELETE RESTRICT` — never `CASCADE` deletes without explicit approval.

### V. Schema-Driven API Contracts

Pydantic schemas in `app/schemas/` ARE the API contract:

- Every endpoint MUST have dedicated `Create`, `Update`, and `Response` schemas.
- Schemas MUST use Pydantic v2 features (`model_config`, `ConfigDict`, `Field` validators).
- Response schemas MUST exclude sensitive fields (e.g., password hashes).
- Use `orm_mode = True` (via `from_attributes = True`) for ORM model binding.

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI | 0.138.x |
| ORM | SQLAlchemy | 2.0.x |
| Database | PostgreSQL | — |
| Migrations | Alembic | — |
| Auth | JWT (python-jose) | — |
| Password Hashing | bcrypt (passlib) | — |
| Validation | Pydantic v2 | 2.13.x |
| Testing | pytest | — |

All new code MUST use the established stack. Introducing new libraries requires explicit approval and justification.

## Architecture Standards

- **Database Sessions**: Use `get_db()` dependency from `app/dependencies.py`. Never create sessions directly.
- **Configuration**: Secrets and config values MUST go through environment variables or `app/core/config.py`. Never hardcode credentials.
- **Error Handling**: Use HTTPException with appropriate status codes. Custom exceptions in `app/exceptions/` for domain-specific errors.
- **Migrations**: All schema changes MUST go through Alembic. Never modify the database directly. Run `alembic revision --autogenerate -m "description"` then review before `alembic upgrade head`.

## Security Requirements

- JWT tokens MUST expire (currently 30 minutes). Refresh mechanisms MUST be implemented before extending token lifetime.
- Passwords MUST be hashed with bcrypt before storage. Raw passwords MUST NEVER be logged or returned in responses.
- The `SECRET_KEY` in `app/core/config.py` MUST be loaded from environment variables in production — never committed to source control.
- All database credentials MUST be externalized via environment variables or `.env` files (which are gitignored).

## Development Workflow

1. **Branch** from `main` for each feature.
2. **Specify** the feature using `/speckit.specify` before coding.
3. **Plan** the implementation using `/speckit.plan`.
4. **Break down** into tasks using `/speckit.tasks`.
5. **Implement** following the layered architecture and test-first principle.
6. **Test** with `pytest` — all tests MUST pass before merge.
7. **Migrate** with Alembic if schema changes are needed.
8. **Review** — verify constitution compliance before merge.

## Governance

This constitution supersedes all other development practices for the Milk Management AI project. All pull requests and code reviews MUST verify compliance with the principles above.

Amendments to this constitution MUST:
1. Be documented with rationale.
2. Increment the version number (MAJOR for principle removals/redefinitions, MINOR for new principles, PATCH for clarifications).
3. Propagate changes to dependent templates (plan, spec, tasks).

Complexity beyond the established patterns MUST be justified in the implementation plan's Complexity Tracking section.

**Version**: 1.0.0 | **Ratified**: 2026-07-27 | **Last Amended**: 2026-07-27
