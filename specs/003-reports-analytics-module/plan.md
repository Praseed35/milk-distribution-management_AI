# Implementation Plan: Reports and Analytics Module

**Branch**: `003-reports-analytics-module` | **Date**: 2026-07-30 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-reports-analytics-module/spec.md`

## Summary

Add 6 report types (route delivery, revenue, collection efficiency, customer consumption, token book utilization, operational dashboard) as read-only API endpoints with JSON + CSV export, pagination, role-based access, and optional caching. No new database tables — all reports are computed from existing tables via SQL aggregation queries in a new `app/services/reports/` service module.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI 0.138.x, SQLAlchemy 2.0.x, Pydantic v2

**Storage**: PostgreSQL (existing) — no new tables needed. Reports are computed from existing `delivery_sessions`, `daily_deliveries`, `customer_payments`, `customer_bills`, `customer_bill_items`, `token_book_issues`, `token_book_payments`, `token_identities`, `subscriptions`, `customers`, `routes`, `milk_types` tables.

**Testing**: pytest with TestClient (existing conftest.py patterns)

**Target Platform**: Linux/Windows server (same as existing)

**Project Type**: Web service (FastAPI backend)

**Performance Goals**: Route delivery report for 6 months of data returns within 5 seconds. Operational dashboard loads within 3 seconds.

**Constraints**: All reports must respect soft deletes (`is_active`). Reports must reflect latest state (edited deliveries, reopened sessions). No new database tables.

**Scale/Scope**: Expected volume ~50 routes, ~2000 customers, ~500 sessions/month, ~15K deliveries/month.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Reports follow the existing pattern — new `app/routers/reports.py`, `app/schemas/reports.py`, `app/services/reports/*.py`. No business logic in routers.
- [x] **RBAC**: Role-based access defined for each report endpoint (OWNER=all, ADMIN=operational only, CHECKER=read-only status, DELIVERY_PARTNER=own route).
- [x] **Schema-Driven Contracts**: Dedicated ReportRequest filter schemas and ReportResponse schemas using Pydantic v2 `ConfigDict(from_attributes=True)`.
- [x] **Soft Deletes**: All report queries filter `is_active == True` for customers, routes, milk types by default.
- [x] **Tech Stack**: Uses established FastAPI + SQLAlchemy 2.0 + PostgreSQL + Pydantic v2 stack.
- [x] **Testing**: New test file `tests/test_reports.py` following existing conftest fixture patterns.
- [x] **Security**: All endpoints use `get_current_user` dependency. Revenue reports restricted to OWNER.
- [x] **Migrations**: No schema changes needed — reports use existing tables only.

## Project Structure

### Documentation (this feature)

```text
specs/003-reports-analytics-module/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Interface contracts
│   └── report-endpoints.md
├── checklists/
│   └── requirements.md
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
app/
├── routers/
│   ├── reports.py               # NEW - report endpoints
│   └── ... (existing)
├── schemas/
│   ├── reports.py               # NEW - report request/response schemas
│   └── ... (existing)
├── services/
│   ├── reports/                 # NEW - report service package
│   │   ├── __init__.py
│   │   ├── route_delivery.py    # FR-001: Route-wise delivery reports
│   │   ├── revenue.py           # FR-002: Revenue reports
│   │   ├── collection.py        # FR-003: Collection efficiency reports
│   │   ├── consumption.py       # FR-004: Customer consumption reports
│   │   ├── token_utilization.py # FR-005: Token book utilization reports
│   │   └── dashboard.py         # FR-006: Operational dashboard
│   └── ... (existing)
└── core/
    └── (existing - no changes)

tests/
├── test_reports.py             # NEW - all report tests
├── conftest.py                 # Extended with report fixtures
└── ... (existing)
```

**Structure Decision**: New `reports` module across layers (routers, schemas, services). Reports are read-only aggregations. Service logic split into focused files per report type for maintainability.

## Complexity Tracking

No constitution violations. All patterns follow existing conventions.
