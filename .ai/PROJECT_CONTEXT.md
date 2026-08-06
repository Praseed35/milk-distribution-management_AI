# PROJECT_CONTEXT.md - Milk Management ERP Backend

> Primary project memory for AI assistants. Read this first.

---

## Project Overview

A **Milk Distribution ERP backend** built with FastAPI + PostgreSQL. Manages the full lifecycle of a milk distribution business: master data (customers, routes, milk types, employees), subscriptions, delivery exceptions, token book management, **daily delivery sessions**, **reconciliation**, **payment management**, **reports & analytics**, and **AI business intelligence** (forecast, anomalies, churn risk, LLM narrative, conversational chat). Serves a **React + TypeScript frontend** (`frontend/`, Phases 1–7 + AI Insights page complete) via a REST API under `/api/v1`.

**Business Domain**: Milk distribution cooperatives/dairies that deliver milk to customers on daily routes using subscription-based ordering. Customers receive physical "token books" (prepaid booklets) to collect milk. Delivery partners load milk, deliver to customers, collect tokens/cash, return leftover milk, and the session is reconciled.

---

## Current Implementation Status (Actual)

| Metric | Value |
|--------|-------|
| SQLAlchemy Models | **17 classes / 16 files** (10 original + DeliverySession, DailyDelivery, SessionEdit, TokenSheetWarning + CustomerBill, CustomerBillItem, CustomerPayment — CustomerBillItem lives in customer_bill.py) |
| Alembic Migrations | **13** (9 original + payment tables + report indexes + `delivery_exceptions.shift`) |
| API Routers | **14** (auth, users, routes, customers, milk_types, employees, subscriptions, delivery_exceptions, token_books, **deliveries**, **delivery_edit**, **payments**, **reports**, **ai**) |
| Service Modules | **19 service files + 8 reports files** (auth, user, route, customer, milk_type, employee, subscription, delivery_exception, token_book, delivery_service, delivery_registration, delivery_reconciliation, delivery_edit_service, payment + AI: forecast, anomaly, churn, insights, chat + reports: route_delivery, revenue, collection, consumption, token_utilization, dashboard, common, cache) |
| Schema Modules | **16** (original + delivery + payments + reports + ai) |
| Exception Modules | **13 + base** (incl. payment + ai) |
| Test Files | **14** (delivery + delivery_edit + payments + reports + ai) |
| Total API Endpoints | **~90** (39 original + 26 delivery + 14 payments + 6 reports + 5 AI) |
| Frontend | **Phases 1–7 + AI Insights complete** — Phase 1 (Setup/Auth/Layout) + Phase 2 (Master Data CRUD) [Sprint 9]; Phase 3 (Subscriptions & Exceptions) + Phase 4 (Token Books) [Sprint 10]; Phase 5 (Delivery Management) [specs/007]; Phase 6 (Payment Management) [specs/008]; Phase 7 (Reports Pages) [specs/009, commit 4489d6a]; AI Insights (`/reports/ai`) [specs/010]. Phase 8 (Polish) pending |

---

## Technology Stack

| Component | Technology | Version/Details |
|-----------|-----------|-----------------|
| Framework | FastAPI | Latest |
| ORM | SQLAlchemy 2.0 | `declarative_base()` style (legacy pattern) |
| Database | PostgreSQL | localhost:5432 |
| DB Name | `milk_managemen_ai` | (note: typo is intentional in code) |
| Migrations | Alembic | **13** migration files in `alembic/versions/` |
| Auth | JWT (python-jose) | HS256, 30min expiry |
| Password Hashing | bcrypt (passlib) | CryptContext with auto-deprecation |
| Validation | Pydantic v2 | `model_config = ConfigDict(from_attributes=True)` |
| Testing | pytest + TestClient | **14 test files, 466 tests passing** |
| Test DB | Same PostgreSQL DB | Transaction rollback isolation per test |

---

## Architecture

### Layered Architecture (No Repository Layer)

```
Router (HTTP) -> Service (Business Logic) -> SQLAlchemy ORM (Data Access)
     |                    |                          |
  schemas/           exceptions/                  models/
```

**Key Pattern**: Services are **module-level functions** (not classes). They accept `db: Session` as first argument. No repository abstraction layer exists - services query SQLAlchemy models directly.

### Application Entry Point

- `app/main.py`: Creates `FastAPI()` instance, adds **CORS middleware** (allow `http://localhost:5173`), creates an `api_v1 = APIRouter(prefix="/api/v1")` umbrella router that includes all **13 routers**, defines `GET /api/v1/health`, AND re-includes all routers at root level for backward compatibility (deprecated)
- **CORS configured** for `http://localhost:5173` (Vite dev server)
- **API prefix added**: all routes are available at `/api/v1/...` (primary) AND root level (legacy/deprecated)
- **No global exception handlers** at the app level yet
- Delivery routers: `deliveries` (prefix `/deliveries/sessions`) and `delivery_edit` (prefix `/deliveries`)

### File Structure (Actual)

```
app/
├── main.py                 # FastAPI app, CORS, /api/v1 umbrella + legacy root routers, health endpoint
├── database.py             # Engine, SessionLocal, Base (declarative_base)
├── dependencies.py         # get_db() generator, OAuth2PasswordBearer(tokenUrl="auth/login")
├── __init__.py
├── core/                   # Security, auth, config, roles
│   ├── config.py           # SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
│   ├── security.py         # hash_password, verify_password, create_access_token, decode_access_token
│   ├── auth.py             # get_current_user() dependency (decodes JWT, fetches User)
│   └── roles.py            # require_role(allowed_roles) dependency factory
├── constants/              # Enum definitions (roles, shifts, statuses)
│   ├── roles.py            # UserRole enum (OWNER, CHECKER, DELIVERY_PARTNER)
│   ├── shifts.py           # Shift enum (MORNING, EVENING)
│   └── statuses.py         # ~12 enums (SessionStatus, DeliveryStatus, DeliverySource, WarningCode, ReconciliationStatus, etc.)
├── models/                 # 16 model files (17 model classes) SQLAlchemy ORM
│   ├── __init__.py         # Imports all models (required for Alembic autogenerate)
│   ├── user.py, route.py, customer.py, milk_type.py, employee.py
│   ├── subscription.py, delivery_exception.py
│   ├── token_identity.py, token_book_issue.py, token_book_payment.py
│   ├── delivery_session.py, daily_delivery.py, session_edit.py, token_sheet_warning.py
│   ├── customer_bill.py    # CustomerBill + CustomerBillItem
│   └── customer_payment.py
├── schemas/                # 15 Pydantic schema modules
│   ├── __init__.py
│   ├── auth.py, user.py, route.py, customer.py, milk_type.py, employee.py
│   ├── subscription.py, delivery_exception.py
│   ├── token_identity.py, token_book.py
│   ├── delivery_session.py, daily_delivery.py, delivery_edit.py
│   ├── payment.py
│   └── reports.py
├── routers/                # 13 FastAPI APIRouters
│   ├── __init__.py
│   ├── auth.py (/auth), users.py (/users), routes.py (/routes)
│   ├── customers.py (/customers), milk_types.py (/milk-types)
│   ├── employees.py (/employees), subscriptions.py (/subscriptions)
│   ├── delivery_exceptions.py (/delivery-exceptions)
│   ├── token_books.py (/token-books)
│   ├── deliveries.py (/deliveries/sessions) -- 16 endpoints (incl. POST /{id}/complete)
│   ├── delivery_edit.py (/deliveries) -- 10 endpoints (edit/reopen now OWNER-only server-side)
│   ├── payments.py (/payments) -- 14 endpoints
│   ├── reports.py (/reports) -- 6 endpoints
│   └── ai.py (/ai) -- 5 endpoints (forecast, anomalies, churn-risk, insights, chat)
├── services/               # 19 business logic modules + reports + ai packages (module-level functions)
│   ├── auth_service.py, user_service.py, route_service.py
│   ├── customer_service.py, milk_type_service.py, employee_service.py
│   ├── subscription_service.py, delivery_exception_service.py
│   ├── token_book_service.py
│   ├── delivery_service.py        # Session lifecycle (create, start, close, generate delivery list)
│   ├── delivery_registration.py    # Token sheet validation, register token/cash/unplanned
│   ├── delivery_reconciliation.py  # Reconciliation calculation, submit, validate, summary
│   ├── delivery_edit_service.py    # Session reopen, undo delivery, edit delivery, edit history
│   ├── payment_service.py          # Bill generation, payments, outstanding
│   ├── ai/                         # 5 AI service modules + LLM client + payload builder + cache
│   │   ├── __init__.py
│   │   ├── client.py               # Mock/disabled-aware LLM client (NVIDIA-compatible), AI_LLM_DISABLED
│   │   ├── llm_payload.py          # Prompt/context builders for insights + chat
│   │   ├── cache.py                # AI report TTL cache (300s, per-user keys)
│   │   ├── forecast.py, anomaly.py, churn.py, insights.py, chat.py
│   └── reports/                    # 6 report + 1 common + 1 cache
│       ├── __init__.py
│       ├── route_delivery.py, revenue.py, collection.py
│       ├── consumption.py, token_utilization.py, dashboard.py
│       ├── common.py (date range, CSV export, role-scoped routes), cache.py (in-memory TTL cache)
├── exceptions/             # 13 custom exception modules + base
│   ├── base.py, user.py, route.py, customer.py, milk_type.py
│   ├── employee.py, subscription.py, delivery_exception.py, token_book.py
│   ├── delivery.py, delivery_edit.py, payment.py
│   └── ai.py (AIRateLimitError, AIUnavailableError)
├── common/                 # Empty (only __init__.py)
└── utils/                  # Empty (only __init__.py)

scripts/
├── seed.py                 # Idempotent database seeder (5 users, 5 routes, 7 milk types, 15 customers, 5 employees, 5 subscriptions)
├── seed_history.py         # Seeds 30 days of sessions/deliveries/bills/payments so AI pages + reports have history
├── test_subscriptions.py   # Manual test script
└── e2e_backend.py          # Playwright E2E backend: resets isolated milk_management_e2e DB, serves API on :8001

tests/
├── conftest.py             # Test fixtures with DB isolation
├── test_auth.py
├── test_users.py
├── test_routes.py
├── test_customers.py
├── test_milk_types.py
├── test_employees.py
├── test_subscriptions.py
├── test_delivery_exceptions.py
├── test_token_books.py
├── test_daily_delivery.py     # 81 delivery tests (session, registration, reconciliation, edit)
├── test_delivery_edit.py      # 8 OWNER-RBAC tests (edit_delivery, reopen_session)
├── test_payments.py           # 33 payment management tests
├── test_reports.py            # 24 reports tests (6 stories + RBAC + CSV + auth)
└── test_ai.py                 # 87 AI tests (forecast, anomalies, churn, insights, chat, edge cases)
# 14 test files, 466 tests total (plus 13 server-dependent scripts/test_subscriptions.py integration tests)

alembic/
├── env.py                  # Imports Base.metadata, app.models for autogenerate
└── versions/               # 13 migration files (chronological)
    ├── cd5183b67dae_initial_schema.py          # users, routes
    ├── de893ed2ffb7_add_customers_table.py     # customers
    ├── 4085a4134c96_add_milk_types_and_employees_tables.py
    ├── b3c4d5e6f7a8_add_employee_fields.py     # employee_code, role, route_id, user_id, timestamps
    ├── 2a032b2352b4_add_subscriptions_table.py
    ├── 3f8a1b2c4d5e_create_delivery_exceptions_table.py
    ├── 4e5f6a7b8c9d_create_token_books_tables.py  # token_identities, token_book_issues, token_book_payments
    ├── 5a6b7c8d9e0f_create_delivery_tables.py     # delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings
    ├── 1154a3a25414_remove_is_active_in_update_customer_.py  # EMPTY migration (no upgrade/downgrade logic)
    ├── aeecd8f99d6d_merge_token_books_and_delivery_heads.py  # Merge heads
    ├── 6a0f9777a5cb_add_payment_management_tables.py         # customer_bills, customer_bill_items, customer_payments
    ├── 119aa199d5d7_add_report_indexes.py                    # report indexes
    └── a1b2c3d4e5f6_add_shift_to_delivery_exceptions.py      # add nullable shift column (MORNING/EVENING) to delivery_exceptions
```

---

## Role Hierarchy

```
OWNER > CHECKER > DELIVERY_PARTNER > EMPLOYEE
```

- **OWNER**: Full system access, can manage employees and credentials, access owner-dashboard
- **CHECKER**: Can verify/check deliveries
- **DELIVERY_PARTNER**: Assigned to routes for delivery
- **EMPLOYEE**: Basic access

RBAC is enforced via `require_role()` on payment/report endpoints (OWNER only for revenue/financial data, ADMIN for operational, DELIVERY_PARTNER scoped to own route). Most basic CRUD endpoints remain unprotected.

---

## Database Schema (17 Tables)

All tables use `is_active` boolean for soft-delete (never physically delete records). Most tables have `created_at` and `updated_at` timestamp columns (except `users` and `session_edits`).

### Payment Tables

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `customer_bills` | id, customer_id (FK), bill_period_start, bill_period_end, total_amount, paid_amount, balance_amount, bill_status, is_active, created_at, updated_at | Belongs to Customer; has many CustomerBillItems |
| `customer_bill_items` | id, customer_bill_id (FK), milk_type_id (FK), quantity, rate_per_unit, amount | Belongs to CustomerBill and MilkType |
| `customer_payments` | id, customer_bill_id (FK), payment_mode, amount, payment_date, remarks, is_active, created_at, updated_at | Belongs to CustomerBill |

### Core Master Data Tables

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `users` | id, username (unique), password_hash, role, is_active | Referenced by employees (user_id), token_book_payments (collected_by) |
| `routes` | id, route_code (unique), route_name (unique), description, is_active, created_at, updated_at | Has many customers, employees, delivery_sessions |
| `customers` | id, customer_code (unique), customer_name, primary_phone (unique), alternate_phone, address, route_id (FK->routes), remarks, is_active, created_at, updated_at | Belongs to Route; has many Subscriptions, TokenIdentities, DailyDeliveries, TokenBookIssues |
| `milk_types` | id, milk_name (unique), volume_ml, description, is_active, created_at, updated_at | Has many DailyDeliveries, TokenBookIssues |
| `employees` | id, employee_code (unique), name, phone (unique), address, role, route_id (FK nullable), user_id (FK nullable), is_active, created_at, updated_at | Belongs to Route (optional), optionally linked to User; has many DeliverySessions (as delivery_partner). Has @property username |

### Subscription Tables

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `subscriptions` | id, customer_id (FK), milk_type_id (FK), morning_quantity, evening_quantity, status, start_date, end_date, remarks, is_active, created_at, updated_at | Belongs to Customer and MilkType, has many DeliveryExceptions |
| `delivery_exceptions` | id, subscription_id (FK), exception_type, shift (nullable: MORNING/EVENING — null = whole day), start_date, end_date, reason, status, is_active, created_at, updated_at | Belongs to Subscription |

### Token Book Tables

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `token_identities` | id, customer_id (FK), milk_type_id (FK), token_number, is_active, created_at, updated_at | Unique constraint on (customer_id, milk_type_id, token_number). Has many BookIssues |
| `token_book_issues` | id, token_identity_id (FK), customer_id (FK), milk_type_id (FK), issue_number, book_number, total_sheets, issue_date, completion_date, current_sheet, status, remarks, is_active, created_at, updated_at | Belongs to TokenIdentity/Customer/MilkType; has many Payments, Deliveries, Warnings |
| `token_book_payments` | id, token_book_issue_id (FK), payment_mode, payment_status, book_price (Numeric), amount_paid (Numeric), balance_amount (Numeric), payment_date, collected_by (FK->users nullable), remarks, is_active, created_at, updated_at | Belongs to TokenBookIssue, optionally references User (collector) |

### Delivery Management Tables

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `delivery_sessions` | id, route_id (FK), delivery_date, shift, delivery_partner_id (FK->employees), status, total_milk_loaded, total_token_registered, total_cash_sales, total_returned_milk, reconciliation_status, reopened_by (FK->users), reopened_at, reopen_count, version, is_active, created_at, updated_at | Unique constraint on (route_id, delivery_date, shift). Has many DailyDeliveries, SessionEdits |
| `daily_deliveries` | id, session_id (FK), customer_id (FK), milk_type_id (FK), planned_quantity, delivered_quantity, delivery_status, delivery_source, token_sheet_number, token_book_issue_id (FK), added_by (FK->users), added_reason, cash_amount, is_edited, last_edited_by (FK->users), last_edited_at, shift, delivery_date, remarks, version, is_active, created_at, updated_at | Belongs to Session/Customer/MilkType/TokenBookIssue; has many SessionEdits, TokenSheetWarnings |
| `session_edits` | id, session_id (FK), delivery_id (FK nullable), edited_by (FK->users), edit_type, old_value (JSONB), new_value (JSONB), reason (Text), created_at | No is_active (immutable audit log). Belongs to Session/Delivery |
| `token_sheet_warnings` | id, delivery_id (FK), warning_code, warning_message, sheet_number, expected_sheet, book_issue_id (FK nullable), metadata (JSONB), acknowledged_by (FK->users), acknowledged_at, created_at | Belongs to Delivery/TokenBookIssue |

### Entity Relationship Diagram (Text) - Complete

```
User ───────────────────────────────────────────────────────┐
  │                                                         │
  ├──< Employee (user_id)                                  │
  ├──< TokenBookPayment (collected_by)                     │
  ├──< DeliverySession (reopened_by)                       │
  ├──< DailyDelivery (added_by, last_edited_by)            │
  └──< SessionEdit (edited_by)                             │
                                                            │
Route ──────────────────────────────────────────────────────┤
  │                                                         │
  ├──< Customer (route_id)                                  │
  │     │                                                   │
  │     ├──< Subscription (customer_id)                     │
  │     │     │                                             │
  │     │     ├──< DeliveryException (subscription_id)      │
  │     │     └──> MilkType (milk_type_id)                  │
  │     │                                                   │
  │     ├──< TokenIdentity (customer_id)                    │
  │     │     └──> MilkType (milk_type_id)                  │
  │     │                                                   │
  │     ├──< TokenBookIssue (customer_id)                   │
  │     │     └──> MilkType (milk_type_id)                  │
  │     │                                                   │
  │     ├──< DailyDelivery (customer_id)                    │
  │     │     └──> MilkType (milk_type_id)                  │
  │     │                                                   │
  │     ├──< CustomerBill (customer_id)                     │
  │     │     │                                             │
  │     │     ├──< CustomerBillItem (customer_bill_id)      │
  │     │     │     └──> MilkType (milk_type_id)            │
  │     │     └──< CustomerPayment (customer_bill_id)       │
  │     │                                                   │
  │     └──< CustomerPayment (customer_id)                  │
  │                                                         │
  ├──< Employee (route_id)                                  │
  ├──< DeliverySession (route_id)                           │
  │     │                                                   │
  │     ├──< DailyDelivery (session_id)                     │
  │     │     │                                             │
  │     │     ├──< TokenSheetWarning (delivery_id)          │
  │     │     │     └──> TokenBookIssue (book_issue_id)     │
  │     │     └──< SessionEdit (delivery_id)                │
  │     │                                                   │
  │     └──< SessionEdit (session_id)                       │
  │                                                         │
  └──< DeliverySession (delivery_partner_id -> employees)   │
                                                            │
TokenIdentity ───< TokenBookIssue (token_identity_id)       │
                      │                                     │
                      ├──< TokenBookPayment                 │
                      │     (token_book_issue_id)           │
                      │                                     │
                      ├──< DailyDelivery                    │
                      │     (token_book_issue_id)           │
                      │                                     │
                      └──< TokenSheetWarning                │
                            (book_issue_id)                 │
```

## API Endpoints Summary

### Authentication (`/auth`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/auth/login` | Login, returns JWT token | No |
| GET | `/auth/me` | Current user profile (id, username, role) | Yes (any role) |
| PUT | `/auth/change-password` | Change password (validates current, confirms new) | Yes (any role) |
| GET | `/auth/owner-dashboard` | Owner-only dashboard endpoint | OWNER |

### Users (`/users`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/users/` | List all users | No |
| POST | `/users/` | Create new user | No |

### Routes (`/routes`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/routes/` | List active routes | No |
| GET | `/routes/{id}` | Get route by ID (active only) | No |
| POST | `/routes/` | Create route (validates unique code & name) | No |
| PUT | `/routes/{id}` | Update route (validates unique code & name) | No |
| DELETE | `/routes/{id}` | Soft-delete route (sets is_active=False) | No |

### Customers (`/customers`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/customers/` | List active customers | No |
| GET | `/customers/{id}` | Get customer by ID (active only) | No |
| POST | `/customers/` | Create customer (auto-generates code CXXXXX) | No |
| PUT | `/customers/{id}` | Update customer | No |
| DELETE | `/customers/{id}` | Soft-delete customer | No |

### Milk Types (`/milk-types`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/milk-types/` | List active milk types | No |
| GET | `/milk-types/{id}` | Get milk type by ID (active only) | No |
| POST | `/milk-types/` | Create milk type (validates unique name) | No |
| PUT | `/milk-types/{id}` | Update milk type | No |
| DELETE | `/milk-types/{id}` | Soft-delete milk type | No |

### Employees (`/employees`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/employees/` | List active employees | No |
| GET | `/employees/{id}` | Get employee by ID (active only) | No |
| POST | `/employees/` | Create employee (optional user creation with credentials) | OWNER |
| PUT | `/employees/{id}` | Update employee details | No |
| PUT | `/employees/{id}/credentials` | Update linked user credentials (username/password) | OWNER |
| DELETE | `/employees/{id}` | Soft-delete employee | No |

### Subscriptions (`/subscriptions`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/subscriptions/` | List active (flat joined response with customer_code, route_name, milk_type_name) | No |
| GET | `/subscriptions/{id}` | Get detail (nested customer + milk_type objects) | No |
| GET | `/subscriptions/customer/{id}` | Get subscriptions by customer ID | No |
| POST | `/subscriptions/` | Create subscription (validates customer, milk_type, quantities, duplicate) | No |
| PUT | `/subscriptions/{id}` | Update quantities/status/remarks | No |
| DELETE | `/subscriptions/{id}` | Deactivate (sets is_active=False, status=INACTIVE) | No |

### Delivery Exceptions (`/delivery-exceptions`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/delivery-exceptions/` | List active (flat joined with customer, route) | No |
| GET | `/delivery-exceptions/{id}` | Get detail (nested subscription with customer) | No |
| GET | `/delivery-exceptions/subscription/{id}` | Get exceptions by subscription ID | No |
| POST | `/delivery-exceptions/` | Create exception (validates subscription, dates, overlap) | No |
| PUT | `/delivery-exceptions/{id}` | Update exception | No |
| DELETE | `/delivery-exceptions/{id}` | Cancel (sets is_active=False, status=CANCELLED) | No |

### Token Books (`/token-books`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| **Identities** | | | |
| POST | `/token-books/identities/` | Create token identity (validates customer, milk_type, unique constraint) | No |
| GET | `/token-books/identities/` | List all (flat joined with customer, milk_type) | No |
| GET | `/token-books/identities/{id}` | Get detail (nested customer + milk_type) | No |
| GET | `/token-books/identities/customer/{id}` | Get identities by customer ID | No |
| PUT | `/token-books/identities/{id}` | Update token_number | No |
| DELETE | `/token-books/identities/{id}` | Soft-delete identity | No |
| **Book Issues** | | | |
| POST | `/token-books/issues/` | Issue new book (validates active book doesn't exist, unique issue number) | No |
| GET | `/token-books/issues/` | List all (flat joined with customer, milk_type) | No |
| GET | `/token-books/issues/{id}` | Get detail (full nested hierarchy) | No |
| GET | `/token-books/issues/identity/{id}` | Get issues by identity ID | No |
| PUT | `/token-books/issues/{id}` | Update status/sheet/completion_date | No |
| DELETE | `/token-books/issues/{id}` | Soft-delete issue | No |
| **Payments** | | | |
| POST | `/token-books/payments/` | Record payment (auto-calculates balance and status) | No |
| GET | `/token-books/payments/` | List all (flat joined with customer) | No |
| GET | `/token-books/payments/{id}` | Get detail (full nested hierarchy: payment > issue > identity > customer + milk_type) | No |
| GET | `/token-books/payments/issue/{id}` | Get payments by issue ID | No |
| PUT | `/token-books/payments/{id}` | Update payment (recalculates balance and auto-status) | No |
| DELETE | `/token-books/payments/{id}` | Soft-delete payment | No |

### Delivery Sessions (`/deliveries/sessions`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| **Session Lifecycle** | | | |
| POST | `/deliveries/sessions/` | Create delivery session (route + date + shift + partner) | N/A |
| GET | `/deliveries/sessions/` | List sessions (filterable: route_id, delivery_date, shift, status; paginated) | N/A |
| GET | `/deliveries/sessions/{id}` | Get session detail with deliveries list | N/A |
| POST | `/deliveries/sessions/{id}/start` | Start session (record dispatch) - sets PLANNED->STARTED | N/A |
| POST | `/deliveries/sessions/{id}/dispatch` | Record milk dispatch (total_milk_loaded) | N/A |
| POST | `/deliveries/sessions/{id}/complete` | Mark session COMPLETED (STARTED->COMPLETED) — added in Phase 5 | N/A |
| POST | `/deliveries/sessions/{id}/close` | Close session (COMPLETED->CLOSED, requires balanced reconciliation) | N/A |
| **Checklist & Report** | | | |
| GET | `/deliveries/sessions/{id}/checklist` | Get delivery checklist (customers, routes, quantities) | N/A |
| GET | `/deliveries/sessions/{id}/report` | Get session report with summary and milk summary | N/A |
| **Reconciliation** | | | |
| GET | `/deliveries/sessions/{id}/reconciliation` | Get reconciliation (loaded vs token vs cash vs returned) | N/A |
| GET | `/deliveries/sessions/{id}/reconciliation/summary` | Get session summary | N/A |
| GET | `/deliveries/sessions/{id}/reconciliation/customers` | Get customer delivery statuses | N/A |
| POST | `/deliveries/sessions/{id}/reconciliation/validate` | Validate reconciliation (check if can close) | N/A |
| POST | `/deliveries/sessions/{id}/reconciliation/submit` | Submit reconciliation (cash, returns, tokens) | N/A |
| POST | `/deliveries/sessions/{id}/reconciliation/cash-sales` | Add cash sale during reconciliation | N/A |
| DELETE | `/deliveries/sessions/{id}/reconciliation/cash-sales/{cs_id}` | Remove cash sale | N/A |

### Delivery Operations (`/deliveries`)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| **Delivery CRUD** | | | |
| PUT | `/deliveries/{id}` | Update delivery status/quantity/sheet (with optimistic locking) | N/A |
| POST | `/deliveries/unplanned` | Register an unplanned delivery (token/cash/pending) | N/A |
| POST | `/deliveries/validate-token` | Validate a token sheet before registration | N/A |
| GET | `/deliveries/customer/{id}/token-status` | Get customer's token book status | N/A |
| **Token Registration** | | | |
| POST | `/deliveries/{id}/register-token` | Register a token sheet for a delivery | N/A |
| **Editing & History** | | | |
| PUT | `/deliveries/{id}/edit` | Edit delivery in a reopened session (owner only) | OWNER |
| GET | `/deliveries/{id}/warnings` | Get warnings for a delivery | N/A |
| GET | `/deliveries/session/{id}` | Get all deliveries for a session (filterable by status) | N/A |
| POST | `/deliveries/session/{id}/reopen` | Reopen a closed session (owner only) | OWNER |
| GET | `/deliveries/session/{id}/edit-history` | Get full edit history for a session | N/A |

### AI Insights (`/ai`) — Sprint 14 (specs/010)
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/ai/forecast` | Statistical demand forecast (weekday-seasonal moving average, horizon 1-30) | OWNER/ADMIN |
| GET | `/ai/anomalies` | Anomaly detection (z-score: high returns, cash shortfall, mismatch, low sales, consumption drop) | OWNER/ADMIN |
| GET | `/ai/churn-risk` | Churn-risk score per customer (0-100, LOW/MEDIUM/HIGH) | OWNER/ADMIN |
| GET | `/ai/insights` | LLM narrative + stats (degrades to `stats_only` when disabled/unavailable) | OWNER |
| POST | `/ai/chat` | Conversational Q&A over business data (per-user rate limit, 429/503 handled) | OWNER |

All AI results cached 300s per user (`?refresh=true` bypasses); chat never cached. Volumes in litres.

**Total: ~90 API endpoints across 14 routers**

---

## Business Workflows

### Customer Management
1. Routes are created first (geographic delivery areas)
2. Customers are registered and assigned to a route
3. Auto-generated customer codes: `C{NNNNN}` (C00001, C00002, ...)
4. Phone number uniqueness enforced; primary and alternate must differ

### Subscription Lifecycle
1. Customer selects a milk type and sets morning/evening quantities
2. At least one quantity must be > 0
3. Only one active subscription per customer-milk_type pair allowed
4. Subscriptions can be updated (quantities, status) or deactivated
5. Deactivation sets status="INACTIVE" and is_active=False

### Delivery Exceptions
1. Temporarily modify a subscription's delivery (vacation, no_milk, holiday)
2. Date overlap detection prevents conflicting exceptions for the same subscription
3. End date must be >= start date
4. `shift` is optional (MORNING/EVENING); when set, the exception applies only to that shift — otherwise it applies to the whole day (used by session checklist generation)
5. Can be cancelled (sets status=CANCELLED)

### Token Book System
1. **Token Identity**: Unique token number assigned to customer + milk_type combination
2. **Book Issue**: Physical book issued against an identity; only ONE active book per identity at a time
3. **Payment**: Tracks book price, amount paid, auto-calculated balance (PAID/PARTIAL/PENDING)
4. Book lifecycle: WAITING -> ACTIVE -> COMPLETED

### Employee Management
1. Employees can be assigned to routes
2. Optional user account creation during employee registration
3. Credentials (username/password) managed separately via dedicated endpoint
4. OWNER-only access for employee creation and credential management

### Delivery Session Lifecycle
1. **Create**: A delivery session is created for a route + date + shift + delivery partner
2. **Dispatch/Start**: Milk quantity loaded is recorded; session status becomes STARTED
3. **Generate Delivery List**: Active subscriptions for the route generate DailyDelivery records (Phase 5 rewrite joins through `Customer.route_id`; planned_quantity = `morning_quantity`/`evening_quantity` per shift, zero-quantity subscriptions skipped, exceptions excluded by date+shift)
4. **Deliver**: Delivery partner delivers milk, records status per customer:
   - DELIVERED (token sheet collected)
   - PENDING_TOKEN (delivered but token pending)
   - CASH_SALE (cash payment collected)
   - NOT_DELIVERED / CANCELLED
5. **Token Registration**: Token sheets are validated (sequential check, gap detection, old-book detection) and registered against deliveries
6. **Unplanned Deliveries**: Additional deliveries can be registered for walk-in customers
7. **Complete**: Delivery partner marks session as COMPLETED
8. **Reconciliation**: Calculate loaded vs (token registered + cash sales + returned milk); must balance within 0.01L
9. **Close**: If balanced, session marked CLOSED; reconciliation_status = BALANCED
10. **Reopen (Owner only)**: Closed sessions can be reopened to edit deliveries; audit trail via SessionEdit
11. **Session state machine**: PLANNED -> STARTED -> COMPLETED -> CLOSED <-> COMPLETED (reopen)

### Reconciliation Workflow
1. Calculate: loaded_milk - (token_registered + cash_sales + returned_milk) = difference
2. If |difference| < 0.01, session is balanced
3. Submit includes cash collected, cash sales breakdown, returned milk with reasons, token sheets collected
4. Validation checks for mismatches and pending tokens
5. Can add/remove cash sales during reconciliation

### Token Sheet Validation
1. Checks for active token book for customer + milk type
2. Validates sheet number is within range (1 to total_sheets)
3. Detects non-sequential sheets (skipping ahead)
4. Detects out-of-order sheets (using old sheet)
5. Detects sheets already used
6. Detects old books with remaining sheets when new book started
7. Warnings require acknowledgment before proceeding

---

## Configuration and Environment

### Database Configuration
- **Connection**: `postgresql://postgres:admin@localhost:5432/milk_managemen_ai`
- **Defined in**: `app/database.py` (hardcoded) and `alembic.ini` (sqlalchemy.url)
- **Not using environment variables** for database URL

### Security Configuration (`app/core/config.py`)
```python
SECRET_KEY = "milk_management_secret_key_2026"  # Hardcoded!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Environment Variables (`.env`)
```
NVIDIA_API_KEY=nvapi-...  # Only NVIDIA API key, not used in current codebase
AI_LLM_DISABLED=1         # (optional) disables LLM calls; insights endpoint degrades to stats_only, chat returns 503
AI_LLM_PROVIDER=mock      # default "mock"; future NVIDIA/OpenAI-compatible provider
AI_CHAT_MAX_REQUESTS_PER_MINUTE=20  # sliding-window rate limit for /ai/chat (per user)
AI_CHAT_MAX_TOKENS=512    # max LLM tokens per chat reply
```
AI settings live in `app/core/config.py` (see TECH_DEBT B5 for the disabled-mode caveat).

### Test Configuration
- `USE_ACTUAL_DB=true` (default) - tests use real PostgreSQL
- `TEST_DB_URL` - custom test database URL
- `USE_ACTUAL_DB=false` - falls back to SQLite

---

## Coding Conventions

### Service Layer
- Module-level functions, not class methods
- First parameter is always `db: Session`
- Return SQLAlchemy model objects directly (not schemas) for CRUD operations
- Return dicts for list/detail queries with joins
- Raise custom exceptions for business rule violations
- Use `db.commit()` + `db.refresh()` after writes
- Query pattern: `db.query(Model).filter(...).first()` / `.all()`

### Router Layer
- One `APIRouter` per domain
- Prefix format: `/{domain-name-plural}` (kebab-case)
- Tags: Title Case domain name
- Import and catch domain-specific exceptions, map to HTTP status codes
- Use `Depends(get_db)` for database injection
- Use `response_model=` for type-safe responses
- Create endpoints return `status_code=201` for subscription, employee, delivery-exception, and token-book endpoints
- Some create endpoints use default 200 (routes, customers, milk-types, users)

### Schema Layer
- Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
- Base/Create/Update/Response pattern
- Summary schemas for nested data (CustomerSummaryResponse, MilkTypeSummaryResponse, TokenIdentitySummaryResponse)
- List response schemas (flat dicts, for list endpoints)
- Detail response schemas (nested objects, for single-item endpoints)
- Field validation: `Field(..., gt=0)`, `Field(..., min_length=2, max_length=100)`
- Custom validators via `@model_validator(mode="after")` (ChangePassword, EmployeeCreate, EmployeeCredentialsUpdate)

### Exception Layer
- One file per domain in `exceptions/`
- Base class `BusinessException` exists but is **inconsistently used** (route.py, milk_type.py extend it; most others extend `Exception` directly)
- Each exception class has a custom `__init__` with descriptive message
- Router catches exceptions and maps to HTTP status codes:
  - **404**: Not Found errors
  - **400**: Validation/Duplicate/Conflict errors
  - **401**: Auth failures (raised in core/auth.py, security.py)
  - **403**: Access denied (raised in core/roles.py)

### Soft Delete Pattern
- Every table has `is_active = Column(Boolean, default=True, nullable=False)`
- DELETE endpoints set `is_active = False` instead of removing the row
- All queries filter by `is_active == True`
- Some domain DELETE endpoints also set a status field:
  - Subscription -> "INACTIVE"
  - DeliveryException -> "CANCELLED"

### Auto-Generated Codes
- Customers: `C{NNNNN}` (e.g., C00001, C00002) - auto-incremented from last record's code
- Employees: `E{NNNNN}` (e.g., E00001, E00002) - auto-incremented from last record's code
- Generation: Reads last record ordered by id desc, extracts number, increments

### Query Response Pattern
- **List endpoints**: Return flat dicts from SQLAlchemy joined queries (mapped to ListResponse schemas)
- **Detail endpoints**: Return nested dict structures manually constructed from joined queries (mapped to DetailResponse schemas)
- **Create/Update/Delete**: Return the SQLAlchemy model object directly (mapped to base Response schema via `from_attributes=True`)

---

## Test Infrastructure

### Configuration
- **Database**: Tests run against the real PostgreSQL database (`milk_managemen_ai`)
- **Environment variables**: `USE_ACTUAL_DB=true` (default), `TEST_DB_URL` for custom DB
- **Run tests**: `pytest` (from project root)

### Isolation Strategy
1. **Session-scoped fixture** `setup_teardown_db`: Drops and recreates all tables at start and end of test session
2. **Function-scoped fixture** `db_session`: Opens a real connection, begins a transaction, yields session, then rolls back after each test
3. **Shared connection override**: `override_get_db` shares the same connection with `TestClient` so both test code and API code see the same uncommitted data

### Fixtures Available
| Fixture | Scope | Description |
|---------|-------|-------------|
| `setup_teardown_db` | session | Drop + recreate all tables |
| `db_session` | function | Transaction-isolated session |
| `client` | function | FastAPI TestClient |
| `seed_user` | function | Creates OWNER user "testadmin" |
| `seed_employee_user` | function | Creates EMPLOYEE user "testemployee" |
| `auth_headers` | function | JWT headers for OWNER |
| `employee_auth_headers` | function | JWT headers for EMPLOYEE |
| `seed_route` | function | Creates R001 "Downtown Route" |
| `seed_customer` | function | Creates customer C00001 on R001 |
| `seed_milk_type` | function | Creates "Full Cream Milk" 1000ml |
| `seed_subscription` | function | Creates subscription for seed_customer + seed_milk_type |
| `seed_delivery_exception` | function | Creates VACATION exception (Aug 1-5, 2026) |
| `seed_token_identity` | function | Creates token identity #1001 |
| `seed_token_book_issue` | function | Creates book issue #1 (WAITING status) |
| `seed_token_book_payment` | function | Creates PREPAID payment (500.00, PAID) |

### Test File Organization
- One test file per module
- Tests grouped by class per endpoint: `TestCreateCustomer`, `TestGetCustomers`, `TestUpdateCustomer`, `TestDeleteCustomer`
- Each class tests success cases, error cases, edge cases, and validation failures
- Tests use fixtures for seeding, assertions for HTTP status codes and response data

### After Running Tests
```bash
python scripts/seed.py  # Restore permanent seed data
python scripts/seed_history.py  # Optional: 30 days of sessions/deliveries/bills/payments for the AI pages + reports
```

---

## Seed Data (scripts/seed.py)

**Idempotent** - safely runs multiple times, skips existing records by checking unique fields.

| Entity | Count | Records |
|--------|-------|---------|
| Users | 5 | owner, checker1, delivery1, admin, employee1 |
| Milk Types | 7 | Full Cream (1000ml), Toned (500ml), Double Toned (500ml), Standard (1000ml), Small Pack (250ml), Buffalo (1000ml), Organic (500ml) |
| Routes | 5 | R001-R005 (Downtown, Uptown, Industrial, Suburban, City Center) |
| Customers | 15 | C00001-C00015 (spread across routes, Indian names) |
| Employees | 5 | E00001-E00005 (mix of CHECKER and DELIVERY_PARTNER, some with user_id links) |
| Subscriptions | 5 base (+ 10 additional) | Spread across customers with various milk types and quantities (15 total in DB) |

### Default Credentials
| Username | Password | Role |
|----------|----------|------|
| owner | owner123 | OWNER |
| checker1 | checker123 | CHECKER |
| delivery1 | delivery123 | DELIVERY_PARTNER |
| admin | admin123 | OWNER |
| employee1 | emp123 | EMPLOYEE |

---

## Implementation Status (Actual)

### Fully Implemented + Tested

| Module | CRUD | Tests | Notes |
|--------|------|-------|-------|
| Users | GET, POST only | 4 tests | No update/delete endpoints |
| Auth | Login, Me, Change Password, Owner Dashboard | 14 tests | JWT-based, role-guarded dashboard |
| Routes | Full CRUD | 11 tests | Unique code + name validation |
| Customers | Full CRUD | 15 tests | Auto-generated codes, phone validation |
| Milk Types | Full CRUD | 12 tests | Unique name validation, volume > 0 |
| Employees | Full CRUD + Credentials | 25+ tests | Optional user linking, OWNER-only create/credentials |
| Subscriptions | Full CRUD + By Customer | 16 tests | Joined queries, deactivation, quantity validation |
| Delivery Exceptions | Full CRUD + By Subscription | 22 tests | Overlap detection, date validation |
| Token Identities | Full CRUD + By Customer | 10 tests | Unique constraint on (customer, milk_type, token_number) |
| Token Book Issues | Full CRUD + By Identity | 10 tests | Active book enforcement |
| Token Book Payments | Full CRUD + By Issue | 12 tests | Auto status calculation (PAID/PARTIAL/PENDING) |

### Tested ✅

| Module | Endpoints | Tests | Notes |
|--------|-----------|-------|-------|
| Delivery Sessions | 15 | 7 story + RBAC + auth | Session lifecycle + delivery list generation |
| Delivery Registration | 5 | 8 story + token validation | Token registration, unplanned deliveries, warnings |
| Delivery Reconciliation | 5 | 5 story + balance calc | Balance calculation, submit, cash sales |
| Delivery Edit | 5 | 4 story + reopen/undo | Session reopen, undo delivery, edit, history |
| Payment Management | 14 | 5 story + RBAC + auth | Bills, payments, outstanding calculation |
| Reports & Analytics | 6 | 24 across 6 story areas + RBAC + CSV + auth | Route delivery, revenue, collection, consumption, token utilization, dashboard |
| AI Business Intelligence | 5 | 53 across 5 story areas + RBAC + auth + degradation | Forecast (statistical), anomalies, churn risk, insights narrative (stats-only fallback), chat (rate limit, 503) |

### Completed (Frontend)

| Priority | Module | Status |
|----------|--------|--------|
| Frontend Phase 3 | Subscriptions & Exceptions pages | ✅ Complete (Sprint 10) |
| Frontend Phase 4 | Token Books pages | ✅ Complete (Sprint 10) |
| Frontend Phase 5 | Delivery Management pages | ✅ Complete (specs/007: session list/create/detail, registration, reconciliation, close, reopen, edit history) |
| Frontend Phase 6 | Payments pages | ✅ Complete (specs/008: payment list/form, bill generate/list/detail, outstanding balances, OWNER/ADMIN role guard, 7 E2E specs) |
| Frontend Phase 7 | Reports pages | ✅ Complete (specs/009, commit 4489d6a: DashboardPage, RouteDeliveryReportPage, RevenueReportPage, ConsumptionReportPage, TokenUtilizationPage, CollectionEfficiencyPage + 5 report components + `types/reports.ts`/`api/reports.ts`/`hooks/useReports.ts`; `/` → `/reports/dashboard` redirect; RoleGuards match backend RBAC; 7 E2E specs in `frontend/e2e/reports.spec.ts`) |
| AI Insights page | `/reports/ai` (specs/010) | ✅ Complete (Sprint 14: ForecastSection, AnomalyList, ChurnRiskTable, InsightNarrative, ChatPanel wired into `AIInsightsPage`; `types/ai.ts`/`api/ai.ts`/`hooks/useAI.ts`; nav item in `config/permissions.ts`; RoleGuard OWNER/ADMIN in `App.tsx`) |

### In Progress

| Priority | Module | Reason |
|----------|--------|--------|
| Frontend Phase 8 | Polish & testing | React app |
| Sprint 8 | AI BI Phase 8 (specs/010) | E2E spec (T035), quickstart validation (T036) remain |

### Not Started

| Priority | Module | Reason |
|----------|--------|--------|
| Sprint 8 | AI Features (demand forecasting, anomaly detection) | ✅ Backend + frontend complete (specs/010); route optimization suggestions deferred — not in scope |
| Sprint 10 | Docker/CI-CD/Deployment | Future |
| Extended | Token Register (sheet-level ledger) | Not implemented |
| Extended | Warning Log dashboard | Not implemented |

---

## Key Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM (using legacy `declarative_base()`)
- **Alembic** - Database migrations
- **python-jose[cryptography]** - JWT token creation/verification (HS256)
- **passlib[bcrypt]** - Password hashing
- **pydantic** v2 - Request/response validation
- **pytest** - Test framework
- **httpx** - Available for async TestClient (sync is used)
- **psycopg2** - PostgreSQL driver

---

## Known Issues / Gotchas

1. **DB name typo**: Database is named `milk_managemen_ai` (missing 't' in management) - this is intentional and consistent everywhere
2. **No update/delete on Users**: Users router only has GET and POST, no PUT or DELETE
3. **Base exception class underused**: `BusinessException` exists in `exceptions/base.py` but most newer exceptions extend `Exception` directly (route.py and milk_type.py are exceptions); delivery/payment/report exceptions DO extend BusinessException (inconsistent)
4. **Constants underused**: Status enums defined in `constants/statuses.py` are not enforced at the schema/model level; statuses are stored as plain strings
5. **Empty directories**: `app/common/` and `app/utils/` exist but contain no code
6. **No pagination on original endpoints**: Delivery session list has pagination but original CRUD endpoints do not
7. **No filtering/searching on original endpoints**: Delivery session list has filters but original list endpoints don't
8. **Hardcoded secret**: `SECRET_KEY` in `core/config.py` is hardcoded (not from env)
9. **CORS is now configured**: `app/main.py` allows `http://localhost:5173` (Vite dev server) — was previously missing; also `/api/v1` prefix added with health endpoint (legacy root routes kept for backward compatibility)
10. **Inconsistent status code on create**: Some create endpoints return 201, others default to 200
11. **No repository layer**: Services query models directly, which is fine for this project size
12. **Employee InactiveRouteError class**: Defined in `exceptions/employee.py` separately from `exceptions/route.py` version - same name, different module
13. **Route model missing String length**: `route_code` and `route_name` use `Column(String)` without length constraint in the model (schemas enforce it)
14. **Revenue report cache-hit bug** (found Aug 4, 2026): `get_revenue` in `app/routers/reports.py` returns an **empty** envelope on JSON cache hits instead of the cached data. CSV path OK. See `TECH_DEBT.md` B3.
15. **`UserRole` enum incomplete** (found Aug 4, 2026): `app/constants/roles.py` lacks `ADMIN` (required by reports RBAC) and `EMPLOYEE` (created by `scripts/seed.py`). Roles are stored as plain strings so nothing breaks. See `TECH_DEBT.md` B4.
16. **CORS only allows :5173**: Playwright E2E serves the frontend on `:5174`; tests work only because they hit the API through the Vite proxy (no CORS enforcement). A real browser on `:5174` would be blocked.
