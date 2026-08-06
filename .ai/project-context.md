# PROJECT_CONTEXT.md - Milk Management ERP Backend

> **DEPRECATED — SUPERSEDED.** This is an older snapshot of the project context (says 8 migrations, ~218 tests, no delivery/payment/report modules). The canonical, up-to-date project memory is **`PROJECT_CONTEXT.md`** (13 migrations, 466 tests across 14 files, 17 tables, 15 routers + AI module, frontend Phases 1–7 + AI Insights complete). Keep this file only as historical reference.

> Primary project memory for AI assistants. Read this first.

---

## Project Overview

A **Milk Distribution ERP backend** built with FastAPI + PostgreSQL. Manages the full lifecycle of a milk distribution business: master data (customers, routes, milk types, employees), subscriptions, delivery exceptions, and token book management. Designed as a REST API backend that will eventually support a React frontend.

**Business Domain**: Milk distribution cooperatives/dairies that deliver milk to customers on daily routes using subscription-based ordering. Customers receive physical "token books" (prepaid booklets) to collect milk.

---

## Technology Stack

| Component | Technology | Version/Details |
|-----------|-----------|-----------------|
| Framework | FastAPI | Latest |
| ORM | SQLAlchemy 2.0 | `declarative_base()` style (legacy pattern) |
| Database | PostgreSQL | localhost:5432 |
| DB Name | `milk_managemen_ai` | (note: typo is intentional in code) |
| Migrations | Alembic | 8 migration files in `alembic/versions/` |
| Auth | JWT (python-jose) | HS256, 30min expiry |
| Password Hashing | bcrypt (passlib) | CryptContext with auto-deprecation |
| Validation | Pydantic v2 | `model_config = ConfigDict(from_attributes=True)` |
| Testing | pytest + TestClient | ~218 tests across 10 test files |
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

- `app/main.py`: Creates `FastAPI()` instance, includes all 9 routers, defines root `/` health endpoint
- **No middleware**, **no CORS**, **no exception handlers** at the app level yet
- No API prefix (all routes are at root level)

### File Structure

```
app/
├── main.py                 # FastAPI app, router registration, health endpoint
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
│   └── statuses.py         # Multiple status enums (SessionStatus, PaymentStatus, TokenStatus, DeliveryStatus, ExceptionType, ExceptionStatus, BookIssueStatus, PaymentMode)
├── models/                 # 10 SQLAlchemy ORM models
│   ├── __init__.py         # Imports all models (required for Alembic autogenerate)
│   ├── user.py
│   ├── route.py
│   ├── customer.py
│   ├── milk_type.py
│   ├── employee.py
│   ├── subscription.py
│   ├── delivery_exception.py
│   ├── token_identity.py
│   ├── token_book_issue.py
│   └── token_book_payment.py
├── schemas/                # Pydantic request/response schemas
│   ├── __init__.py         # Empty
│   ├── auth.py             # LoginRequest, ChangePassword
│   ├── user.py             # UserCreate
│   ├── route.py            # RouteBase, RouteCreate, RouteUpdate, RouteResponse
│   ├── customer.py         # CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSummaryResponse
│   ├── milk_type.py        # MilkTypeBase, MilkTypeCreate, MilkTypeUpdate, MilkTypeResponse, MilkTypeSummaryResponse
│   ├── employee.py         # EmployeeBase, EmployeeCreate, EmployeeCredentialsUpdate, EmployeeUpdate, EmployeeResponse, EmployeeSummaryResponse
│   ├── subscription.py     # SubscriptionBase, SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionListResponse, SubscriptionDetailResponse
│   ├── delivery_exception.py # DeliveryExceptionBase, DeliveryExceptionCreate, DeliveryExceptionUpdate, DeliveryExceptionResponse, DeliveryExceptionListResponse, DeliveryExceptionDetailResponse, SubscriptionSummaryResponse
│   ├── token_identity.py   # TokenIdentityBase, TokenIdentityCreate, TokenIdentityUpdate, TokenIdentityResponse, TokenIdentityListResponse, TokenIdentityDetailResponse, TokenIdentitySummaryResponse
│   └── token_book.py       # TokenBookIssueBase/Create/Update/Response/ListResponse/DetailResponse, TokenBookPaymentBase/Create/Update/Response/ListResponse/DetailResponse, TokenBookIssueSummaryResponse
├── routers/                # FastAPI APIRouters
│   ├── __init__.py
│   ├── auth.py             # /auth prefix
│   ├── users.py            # /users prefix
│   ├── routes.py           # /routes prefix
│   ├── customers.py        # /customers prefix
│   ├── milk_types.py       # /milk-types prefix
│   ├── employees.py        # /employees prefix
│   ├── subscriptions.py    # /subscriptions prefix
│   ├── delivery_exceptions.py # /delivery-exceptions prefix
│   └── token_books.py      # /token-books prefix (identities, issues, payments)
├── services/               # Business logic (module-level functions)
│   ├── __init__.py         # Empty
│   ├── auth_service.py
│   ├── user_service.py
│   ├── route_service.py
│   ├── customer_service.py
│   ├── milk_type_service.py
│   ├── employee_service.py
│   ├── subscription_service.py
│   ├── delivery_exception_service.py
│   └── token_book_service.py   # Single service for identities, issues, payments
├── exceptions/             # Custom exception classes per domain
│   ├── base.py             # BusinessException base class
│   ├── user.py             # UserAlreadyExistsError, InvalidCredentialsError
│   ├── route.py            # DuplicateRouteCodeError, DuplicateRouteNameError, RouteNotFoundError, InactiveRouteError
│   ├── customer.py         # CustomerNotFoundError, DuplicatePrimaryPhoneError, DuplicateCustomerCodeError, SamePhoneNumberError
│   ├── milk_type.py        # DuplicateMilkNameError, MilkTypeError
│   ├── employee.py         # EmployeeNotFoundError, DuplicateEmployeeCodeError, DuplicateEmployeePhoneError, EmployeeRouteNotFoundError, InactiveRouteError, EmployeeUserNotFoundError, InactiveUserError, DuplicateUsernameError, EmployeeNoLinkedUserError
│   ├── subscription.py     # SubscriptionNotFoundError, DuplicateSubscriptionError, InactiveCustomerError, InactiveMilkTypeError, InvalidSubscriptionQuantityError, SubscriptionAlreadyInactiveError
│   ├── delivery_exception.py # DeliveryExceptionNotFoundError, DeliveryExceptionOverlapError, InvalidDeliveryExceptionDateError, InactiveSubscriptionError, DeliveryExceptionAlreadyInactiveError
│   └── token_book.py       # TokenIdentityNotFoundError, DuplicateTokenIdentityError, TokenBookIssueNotFoundError, ActiveBookExistsError, DuplicateIssueNumberError, TokenBookPaymentNotFoundError, InvalidPaymentAmountError
├── common/                 # Empty (placeholder for shared utilities)
└── utils/                  # Empty (placeholder for utilities)

scripts/
├── seed.py                 # Idempotent database seeder
├── seed_history.py         # Seeds 30 days of sessions/deliveries/bills/payments for the AI pages + reports
└── test_subscriptions.py   # Manual test script

tests/
├── conftest.py             # Test fixtures, DB isolation, seed data
├── test_auth.py            # 14 tests (login, me, change-password, owner-dashboard)
├── test_users.py           # 4 tests (list, create)
├── test_routes.py          # 11 tests (CRUD)
├── test_customers.py       # 15 tests (CRUD, auto-code, validation)
├── test_milk_types.py      # 12 tests (CRUD, validation)
├── test_employees.py       # 25+ tests (CRUD, credentials, auth)
├── test_subscriptions.py   # 16 tests (CRUD, customer lookup, validation)
├── test_delivery_exceptions.py # 22 tests (CRUD, overlap, dates)
├── test_token_books.py     # 36 tests (identities, issues, payments)

alembic/
├── env.py                  # Imports Base.metadata, app.models for autogenerate
└── versions/               # 8 migration files (chronological order)
    ├── cd5183b67dae_initial_schema.py
    ├── de893ed2ffb7_add_customers_table.py
    ├── 2a032b2352b4_add_subscriptions_table.py
    ├── 3f8a1b2c4d5e_create_delivery_exceptions_table.py
    ├── 4085a4134c96_add_milk_types_and_employees_tables.py
    ├── 4e5f6a7b8c9d_create_token_books_tables.py
    ├── b3c4d5e6f7a8_add_employee_fields.py
    └── 1154a3a25414_remove_is_active_in_update_customer_.py
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

Currently, only the employee router (POST, PUT credentials) and owner-dashboard enforce role-based access via `require_role()`. Most CRUD endpoints are unprotected.

---

## Database Schema (10 Tables)

All tables use `is_active` boolean for soft-delete (never physically delete records). All tables have `created_at` and `updated_at` timestamp columns (except `users`).

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `users` | id, username (unique), password_hash, role, is_active | Referenced by employees (user_id), token_book_payments (collected_by) |
| `routes` | id, route_code (unique), route_name (unique), description, is_active, created_at, updated_at | Has many customers, has many employees |
| `customers` | id, customer_code (unique), customer_name, primary_phone (unique), alternate_phone, address, route_id (FK->routes), remarks, is_active, created_at, updated_at | Belongs to Route, has many Subscriptions, has many TokenIdentities |
| `milk_types` | id, milk_name (unique), volume_ml, description, is_active, created_at, updated_at | Referenced by Subscriptions, TokenIdentities |
| `employees` | id, employee_code (unique), name, phone (unique), address, role, route_id (FK nullable), user_id (FK nullable), is_active, created_at, updated_at | Belongs to Route (optional), optionally linked to User. Has @property username |
| `subscriptions` | id, customer_id (FK), milk_type_id (FK), morning_quantity, evening_quantity, status, start_date, end_date, remarks, is_active, created_at, updated_at | Belongs to Customer and MilkType, has many DeliveryExceptions |
| `delivery_exceptions` | id, subscription_id (FK), exception_type, start_date, end_date, reason, status, is_active, created_at, updated_at | Belongs to Subscription |
| `token_identities` | id, customer_id (FK), milk_type_id (FK), token_number, is_active, created_at, updated_at | Unique constraint on (customer_id, milk_type_id, token_number). Has many BookIssues |
| `token_book_issues` | id, token_identity_id (FK), issue_number, issue_date, completion_date, current_sheet, status, remarks, is_active, created_at, updated_at | Belongs to TokenIdentity, has many Payments |
| `token_book_payments` | id, token_book_issue_id (FK), payment_mode, payment_status, book_price (Numeric), amount_paid (Numeric), balance_amount (Numeric), payment_date, collected_by (FK->users nullable), remarks, is_active, created_at, updated_at | Belongs to TokenBookIssue, optionally references User (collector) |

### Entity Relationship Diagram (Text)

```
User ─────────────────────────────────────────────────┐
  │                                                   │
  ├──< Employee (user_id)                            │
  │                                                   │
  └──< TokenBookPayment (collected_by)               │
                                                     │
Route ────────────────────────────────────────────────┤
  │                                                   │
  ├──< Customer (route_id)                           │
  │     │                                             │
  │     ├──< Subscription (customer_id)               │
  │     │     │                                       │
  │     │     ├──< DeliveryException (subscription_id)│
  │     │     │                                       │
  │     │     └──> MilkType (milk_type_id)            │
  │     │                                             │
  │     └──< TokenIdentity (customer_id)              │
  │           │                                       │
  │           ├──> MilkType (milk_type_id)            │
  │           │                                       │
  │           └──< TokenBookIssue (token_identity_id) │
  │                 │                                 │
  │                 └──< TokenBookPayment             │
  │                       (token_book_issue_id)       │
  │                                                   │
  └──< Employee (route_id)                            │
```

---

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

**Total: 39 API endpoints across 9 routers**

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
4. Can be cancelled (sets status=CANCELLED)

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
```

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
| Subscriptions | 5 | Spread across customers with various milk types and quantities |

### Default Credentials
| Username | Password | Role |
|----------|----------|------|
| owner | owner123 | OWNER |
| checker1 | checker123 | CHECKER |
| delivery1 | delivery123 | DELIVERY_PARTNER |
| admin | admin123 | OWNER |
| employee1 | emp123 | EMPLOYEE |

---

## Implementation Status

### Completed (Sprints 1, 2, 4-Core)

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

### Planned (Not Implemented)

| Sprint | Module | Depends On |
|--------|--------|------------|
| Sprint 3 | Daily Delivery Management | Sprint 1, 2 |
| Sprint 4 (remaining) | Token Register | Sprint 3 |
| Sprint 4 (remaining) | Token Ledger | Sprint 3, 5 |
| Sprint 4 (remaining) | Warning Log | Sprint 3, 5 |
| Sprint 5 | Reconciliation | Sprint 3 |
| Sprint 6 | Payment Management | Sprint 5 |
| Sprint 7 | Reports and Analytics | All above |
| Sprint 8 | AI Business Intelligence | Sprint 7 |
| Sprint 9 | Frontend (React) | All backend |
| Sprint 10 | Testing and Deployment | All |

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
3. **Base exception class underused**: `BusinessException` exists in `exceptions/base.py` but most newer exceptions extend `Exception` directly (route.py and milk_type.py are exceptions)
4. **Constants underused**: Status enums defined in `constants/statuses.py` are not enforced at the schema/model level; statuses are stored as plain strings
5. **Empty directories**: `app/common/` and `app/utils/` exist but contain no code
6. **No pagination**: All list endpoints return all active records
7. **No filtering/searching**: List endpoints have no query parameters for filtering
8. **Hardcoded secret**: `SECRET_KEY` in `core/config.py` is hardcoded (not from env)
9. **No CORS middleware**: Not configured yet (needed for frontend)
10. **Inconsistent status code on create**: Some create endpoints return 201, others default to 200
11. **No repository layer**: Services query models directly, which is fine for this project size
12. **Employee InactiveRouteError class**: Defined in `exceptions/employee.py` separately from `exceptions/route.py` version - same name, different module
13. **Route model missing String length**: `route_code` and `route_name` use `Column(String)` without length constraint in the model (schemas enforce it)
