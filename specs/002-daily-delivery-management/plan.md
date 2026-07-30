# Implementation Plan: Daily Delivery Management

**Branch**: `002-daily-delivery-management` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-daily-delivery-management/spec.md`

## Summary

Implement daily delivery management for milk distribution operations, covering the complete lifecycle from delivery list generation through route reconciliation and closure. The feature includes token sheet registration, unplanned deliveries, session editing with token returns, and comprehensive warning systems for edge cases.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: FastAPI 0.138.x, SQLAlchemy 2.0.x, Pydantic v2 2.13.x

**Storage**: PostgreSQL

**Testing**: pytest

**Target Platform**: Linux server (web service)

**Project Type**: web-service (REST API)

**Performance Goals**: 
- Delivery list generation: <5 seconds for 50-customer route
- Token registration: <3 seconds
- Reconciliation: instant calculation

**Constraints**: 
- Must follow existing layered architecture
- Must use soft deletes for all entities
- Must implement optimistic locking for concurrent edits

**Scale/Scope**:
- 50+ customers per route
- Multiple routes per day
- Morning and evening shifts
- Unlimited active token books per customer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Plan places code in correct layers (routers, services, models, schemas)
- [x] **RBAC**: Role-based access controls defined for all endpoints (OWNER, CHECKER, DELIVERY_PARTNER)
- [x] **Schema-Driven Contracts**: Dedicated Create/Update/Response Pydantic schemas specified
- [x] **Soft Deletes**: All entities use `is_active` flag
- [x] **Tech Stack**: Uses established stack (FastAPI, SQLAlchemy 2.0, PostgreSQL, Pydantic v2)
- [x] **Testing**: Test coverage planned for all endpoints
- [x] **Security**: Credentials externalized, JWT authentication required
- [x] **Migrations**: Alembic migrations planned for new tables

## Project Structure

### Documentation (this feature)

```text
specs/002-daily-delivery-management/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── sessions.md      # Delivery session API contracts
│   ├── deliveries.md    # Daily delivery API contracts
│   └── reconciliation.md # Reconciliation API contracts
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models/
│   ├── delivery_session.py      # NEW
│   ├── daily_delivery.py        # NEW
│   ├── session_edit.py          # NEW
│   └── token_sheet_warning.py   # NEW
├── schemas/
│   ├── delivery_session.py      # NEW
│   ├── daily_delivery.py        # NEW
│   └── delivery_edit.py         # NEW
├── services/
│   ├── delivery_service.py      # NEW
│   ├── delivery_registration.py # NEW
│   ├── delivery_reconciliation.py # NEW
│   └── delivery_edit_service.py # NEW
├── routers/
│   ├── deliveries.py            # NEW
│   └── delivery_edit.py         # NEW
├── exceptions/
│   ├── delivery.py              # NEW
│   └── delivery_edit.py         # NEW
└── constants/
    └── statuses.py              # UPDATE - add new statuses

alembic/versions/
└── XXXX_create_delivery_tables.py  # NEW
```

**Structure Decision**: Follow existing layered architecture pattern. New delivery domain files are added in each layer following the naming convention (e.g., `delivery_session.py` across models, schemas, services, routers).

## Complexity Tracking

No constitution violations requiring justification. This feature follows all established patterns.
