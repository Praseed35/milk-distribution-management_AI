# PROJECT_CONTEXT.md - Milk Management ERP Backend

> Primary project memory for AI assistants. Read this first.

---

## Project Overview

A **Milk Distribution ERP backend** built with FastAPI + PostgreSQL. Manages the full lifecycle of a milk distribution business: master data (customers, routes, milk types, employees), subscriptions, delivery exceptions, and token book management. Designed as a REST API backend that will eventually support a React frontend.

**Business Domain**: Milk distribution cooperatives/dairies that deliver milk to customers on daily routes using subscription-based ordering. Customers receive physical "token books" (prepaid booklets) to collect milk.

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | Latest |
| ORM | SQLAlchemy 2.0 | `declarative_base()` style |
| Database | PostgreSQL | localhost:5432 |
| DB Name | `milk_managemen_ai` | (note: typo is intentional in code) |
| Migrations | Alembic | 8 migration files |
| Auth | JWT (python-jose) | HS256, 30min expiry |
| Password Hashing | bcrypt (passlib) | CryptContext |
| Validation | Pydantic v2 | `model_config = ConfigDict(from_attributes=True)` |
| Testing | pytest + TestClient | 218 tests |
| Test DB | Same PostgreSQL DB | Transaction rollback isolation |

---

## Architecture

### Layered Architecture (No Repository Layer)

```
Router (HTTP) -> Service (Business Logic) -> SQLAlchemy ORM (Data Access)
     |                    |                          |
  schemas/           exceptions/                  models/
```

**Key Pattern**: Services are **module-level functions** (not classes). They accept `db: Session` as first argument. No repository abstraction layer exists - services query SQLAlchemy models directly.

### File Structure

```
app/
├── main.py                 # FastAPI app, router registration, health endpoint
├── database.py             # Engine, SessionLocal, Base (declarative_base)
├── dependencies.py         # get_db() generator, OAuth2PasswordBearer
├── core/
│   ├── config.py           # SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
│   ├── security.py         # hash_password, verify_password, JWT encode/decode
│   ├── auth.py             # get_current_user() dependency
│   └── roles.py            # require_role() dependency factory
├── constants/
│   ├── roles.py            # UserRole enum (OWNER, CHECKER, DELIVERY_PARTNER)
│   ├── shifts.py           # Shift enum (MORNING, EVENING)
│   └── statuses.py         # Multiple status enums (Session, Payment, Token, Delivery, Exception, BookIssue, PaymentMode)
├── models/                 # 10 SQLAlchemy ORM models
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
│   ├── auth.py
│   ├── user.py
│   ├── route.py
│   ├── customer.py
│   ├── milk_type.py
│   ├── employee.py
│   ├── subscription.py
│   ├── delivery_exception.py
│   ├── token_identity.py
│   └── token_book.py       # Contains both issue and payment schemas
├── routers/                # FastAPI APIRouters
│   ├── auth.py
│   ├── users.py
│   ├── routes.py
│   ├── customers.py
│   ├── milk_types.py
│   ├── employees.py
│   ├── subscriptions.py
│   ├── delivery_exceptions.py
│   └── token_books.py      # Single router for identities, issues, and payments
├── services/               # Business logic (module-level functions)
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
│   ├── user.py
│   ├── route.py
│   ├── customer.py
│   ├── milk_type.py
│   ├── employee.py
│   ├── subscription.py
│   ├── delivery_exception.py
│   └── token_book.py
├── common/                 # Empty (placeholder for shared utilities)
└── utils/                  # Empty (placeholder for utilities)
```

---

## Role Hierarchy

```
OWNER > CHECKER > DELIVERY_PARTNER > EMPLOYEE
```

- **OWNER**: Full system access, can manage employees and credentials
- **CHECKER**: Can verify/check deliveries
- **DELIVERY_PARTNER**: Assigned to routes for delivery
- **EMPLOYEE**: Basic access

Currently, only the employee router and owner-dashboard enforce role-based access via `require_role()`.

---

## Database Schema (10 Tables)

All tables use `is_active` boolean for soft-delete (never physically delete records).

| Table | Key Columns | Relationships |
|-------|-------------|---------------|
| `users` | id, username (unique), password_hash, role, is_active | - |
| `routes` | id, route_code (unique), route_name (unique), description, is_active | Has many customers, employees |
| `customers` | id, customer_code (unique), customer_name, primary_phone (unique), alternate_phone, address, route_id (FK), remarks, is_active | Belongs to Route, has many Subscriptions |
| `milk_types` | id, milk_name (unique), volume_ml, description, is_active | Referenced by Subscriptions, TokenIdentities |
| `employees` | id, employee_code (unique), name, phone (unique), address, role, route_id (FK nullable), user_id (FK nullable), is_active | Belongs to Route, optionally linked to User |
| `subscriptions` | id, customer_id (FK), milk_type_id (FK), morning_quantity, evening_quantity, status, start_date, end_date, remarks, is_active | Belongs to Customer and MilkType, has many DeliveryExceptions |
| `delivery_exceptions` | id, subscription_id (FK), exception_type, start_date, end_date, reason, status, is_active | Belongs to Subscription |
| `token_identities` | id, customer_id (FK), milk_type_id (FK), token_number, is_active | Unique constraint on (customer_id, milk_type_id, token_number), has many BookIssues |
| `token_book_issues` | id, token_identity_id (FK), issue_number, issue_date, completion_date, current_sheet, status, remarks, is_active | Belongs to TokenIdentity, has many Payments |
| `token_book_payments` | id, token_book_issue_id (FK), payment_mode, payment_status, book_price, amount_paid, balance_amount, payment_date, collected_by (FK->users), remarks, is_active | Belongs to TokenBookIssue |

---

## API Endpoints Summary

### Authentication (`/auth`)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Login, returns JWT | No |
| GET | `/auth/me` | Current user profile | Yes |
| PUT | `/auth/change-password` | Change password | Yes |
| GET | `/auth/owner-dashboard` | Owner-only endpoint | OWNER |

### Users (`/users`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/` | List all users |
| POST | `/users/` | Create user |

### Routes (`/routes`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/routes/` | List active routes |
| GET | `/routes/{id}` | Get by ID |
| POST | `/routes/` | Create route |
| PUT | `/routes/{id}` | Update route |
| DELETE | `/routes/{id}` | Soft-delete route |

### Customers (`/customers`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/customers/` | List active customers |
| GET | `/customers/{id}` | Get by ID |
| POST | `/customers/` | Create (auto-generates customer_code CXXXXX) |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Soft-delete customer |

### Milk Types (`/milk-types`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/milk-types/` | List active milk types |
| GET | `/milk-types/{id}` | Get by ID |
| POST | `/milk-types/` | Create milk type |
| PUT | `/milk-types/{id}` | Update milk type |
| DELETE | `/milk-types/{id}` | Soft-delete milk type |

### Employees (`/employees`)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/employees/` | List active employees | No |
| GET | `/employees/{id}` | Get by ID | No |
| POST | `/employees/` | Create employee (optional user creation) | OWNER |
| PUT | `/employees/{id}` | Update employee | No |
| PUT | `/employees/{id}/credentials` | Update linked user credentials | OWNER |
| DELETE | `/employees/{id}` | Soft-delete employee | No |

### Subscriptions (`/subscriptions`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/subscriptions/` | List active (joined with customer, route, milk_type) |
| GET | `/subscriptions/{id}` | Get detail (nested customer + milk_type objects) |
| GET | `/subscriptions/customer/{id}` | Get by customer |
| POST | `/subscriptions/` | Create subscription |
| PUT | `/subscriptions/{id}` | Update quantities/status |
| DELETE | `/subscriptions/{id}` | Deactivate (sets status=INACTIVE) |

### Delivery Exceptions (`/delivery-exceptions`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/delivery-exceptions/` | List active (joined with customer, route) |
| GET | `/delivery-exceptions/{id}` | Get detail (nested subscription + customer) |
| GET | `/delivery-exceptions/subscription/{id}` | Get by subscription |
| POST | `/delivery-exceptions/` | Create exception |
| PUT | `/delivery-exceptions/{id}` | Update exception |
| DELETE | `/delivery-exceptions/{id}` | Cancel (sets status=CANCELLED) |

### Token Books (`/token-books`)
| Method | Path | Description |
|--------|------|-------------|
| **Identities** | | |
| POST | `/token-books/identities/` | Create token identity |
| GET | `/token-books/identities/` | List all |
| GET | `/token-books/identities/{id}` | Get detail (nested customer + milk_type) |
| GET | `/token-books/identities/customer/{id}` | Get by customer |
| PUT | `/token-books/identities/{id}` | Update token_number |
| DELETE | `/token-books/identities/{id}` | Soft-delete identity |
| **Book Issues** | | |
| POST | `/token-books/issues/` | Issue new book |
| GET | `/token-books/issues/` | List all |
| GET | `/token-books/issues/{id}` | Get detail (nested identity + customer) |
| GET | `/token-books/issues/identity/{id}` | Get by identity |
| PUT | `/token-books/issues/{id}` | Update status/sheet/completion |
| DELETE | `/token-books/issues/{id}` | Soft-delete issue |
| **Payments** | | |
| POST | `/token-books/payments/` | Record payment |
| GET | `/token-books/payments/` | List all |
| GET | `/token-books/payments/{id}` | Get detail (full nested hierarchy) |
| GET | `/token-books/payments/issue/{id}` | Get by issue |
| PUT | `/token-books/payments/{id}` | Update payment amounts |
| DELETE | `/token-books/payments/{id}` | Soft-delete payment |

---

## Coding Conventions

### Service Layer
- Module-level functions, not class methods
- First parameter is always `db: Session`
- Return SQLAlchemy model objects directly (not schemas)
- Raise custom exceptions for business rule violations
- Use `db.commit()` + `db.refresh()` after writes
- Query pattern: `db.query(Model).filter(...).first()`

### Router Layer
- One `APIRouter` per domain
- Prefix format: `/{domain-name-plural}` (kebab-case)
- Tags: Title Case domain name
- Import and catch domain-specific exceptions, map to HTTP status codes
- Use `Depends(get_db)` for database injection
- Use `response_model=` for type-safe responses
- Create endpoints return `status_code=201`

### Schema Layer
- Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
- Base/Create/Update/Response pattern
- Summary schemas for nested data (CustomerSummaryResponse, MilkTypeSummaryResponse)
- List response schemas (flat, for list endpoints)
- Detail response schemas (nested objects, for single-item endpoints)
- Field validation: `Field(..., gt=0)`, `Field(..., min_length=2, max_length=100)`
- Custom validators via `@model_validator(mode="after")`

### Exception Layer
- One file per domain in `exceptions/`
- Base class `BusinessException` exists but not all exceptions extend it
- Each exception class has a custom `__init__` with descriptive message
- Router catches exceptions and maps to HTTP status codes:
  - 404: Not Found errors
  - 400: Validation/Duplicate/Conflict errors
  - 401: Auth failures
  - 403: Access denied

### Soft Delete Pattern
- Every table has `is_active = Column(Boolean, default=True, nullable=False)`
- DELETE endpoints set `is_active = False` instead of removing the row
- All queries filter by `is_active == True`
- Some domain DELETE endpoints also set a status field (e.g., Subscription -> "INACTIVE", DeliveryException -> "CANCELLED")

### Auto-Generated Codes
- Customers: `C{NNNNN}` (e.g., C00001, C00002) - auto-incremented from last record
- Employees: `E{NNNNN}` (e.g., E00001, E00002) - auto-incremented from last record

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
2. **Function-scoped fixture** `db_session`: Opens a real connection, begins a transaction, yields session, then rolls back after each test. This means tests never commit permanent changes.
3. **Shared connection override**: `override_get_db` shares the same connection with `TestClient` so both test code and API code see the same uncommitted data.

### Fixtures Available
- `seed_user` - Creates a test OWNER user
- `seed_employee_user` - Creates a test EMPLOYEE user
- `auth_headers` - JWT headers for OWNER
- `employee_auth_headers` - JWT headers for EMPLOYEE
- `seed_route` - Creates R001 route
- `seed_customer` - Creates customer C00001 on R001
- `seed_milk_type` - Creates "Full Cream Milk" 1000ml
- `seed_subscription` - Creates subscription for seed_customer + seed_milk_type
- `seed_delivery_exception` - Creates VACATION exception for seed_subscription
- `seed_token_identity` - Creates token identity #1001
- `seed_token_book_issue` - Creates book issue #1
- `seed_token_book_payment` - Creates PREPAID payment for issue

### Test File Organization
- One test file per module: `test_users.py`, `test_customers.py`, etc.
- Tests grouped by class per endpoint: `TestCreateCustomer`, `TestGetCustomers`, etc.
- Each class tests success cases, error cases, edge cases, and validation failures

### After Running Tests
```bash
python -m scripts.seed  # Restore permanent seed data
```

---

## Seed Data (scripts/seed.py)

**Idempotent** - safely runs multiple times, skips existing records.

| Entity | Records |
|--------|---------|
| Users | owner, checker1, delivery1, admin, employee1 |
| Milk Types | Full Cream, Toned, Double Toned, Standard, Small Pack, Buffalo, Organic |
| Routes | R001-R005 (Downtown, Uptown, Industrial, Suburban, City Center) |
| Customers | C00001-C00015 (spread across routes) |
| Employees | E00001-E00005 (mix of CHECKER and DELIVERY_PARTNER) |
| Subscriptions | 5 active subscriptions |

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
| Users | GET, POST | Yes | Simple create, no update/delete |
| Auth | Login, Me, Change Password, Owner Dashboard | Yes | JWT-based |
| Routes | Full CRUD | Yes | |
| Customers | Full CRUD | Yes | Auto-generated codes |
| Milk Types | Full CRUD | Yes | |
| Employees | Full CRUD + Credentials | Yes | Optional user linking, OWNER-only create/credentials |
| Subscriptions | Full CRUD + By Customer | Yes | Joined queries, deactivation |
| Delivery Exceptions | Full CRUD + By Subscription | Yes | Overlap detection, date validation |
| Token Identities | Full CRUD + By Customer | Yes | Unique constraint on (customer, milk_type, number) |
| Token Book Issues | Full CRUD + By Identity | Yes | Active book enforcement |
| Token Book Payments | Full CRUD + By Issue | Yes | Auto status calculation |

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

- FastAPI
- SQLAlchemy 2.0
- Alembic
- python-jose[cryptography] (JWT)
- passlib[bcrypt] (password hashing)
- pydantic (v2)
- pytest
- httpx (for TestClient async support, though sync is used)
- PostgreSQL driver (psycopg2)

---

## Known Issues / Gotchas

1. **DB name typo**: Database is named `milk_managemen_ai` (missing 't' in management) - this is intentional and consistent everywhere
2. **No update/delete on Users**: Users router only has GET and POST, no PUT or DELETE
3. **Base exception class underused**: `BusinessException` exists in `exceptions/base.py` but many newer exceptions extend `Exception` directly instead
4. **Constants underused**: Status enums defined in `constants/statuses.py` are not enforced at the schema/model level; statuses are stored as plain strings
5. **Empty directories**: `app/common/` and `app/utils/` exist but contain no code
6. **No pagination**: All list endpoints return all active records
7. **No filtering/searching**: List endpoints have no query parameters for filtering
8. **Hardcoded secret**: `SECRET_KEY` in `core/config.py` is hardcoded (not from env)
9. **No CORS middleware**: Not configured yet (needed for frontend)
