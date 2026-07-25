# Architecture: Milk Management AI

## Layered Architecture

The application follows a 4-layer architecture:

```
┌─────────────────────────────────────┐
│         Routers (API Layer)         │  HTTP endpoints, request parsing,
│   app/routers/*.py                  │  response formatting, status codes
├─────────────────────────────────────┤
│         Services (Business Layer)   │  Domain logic, validation,
│   app/services/*.py                 │  business rules enforcement
├─────────────────────────────────────┤
│         Models (Data Layer)         │  SQLAlchemy ORM models,
│   app/models/*.py                   │  table definitions, relationships
├─────────────────────────────────────┤
│         Database (Persistence)      │  PostgreSQL via SQLAlchemy,
│   app/database.py                   │  Alembic migrations
└─────────────────────────────────────┘
```

**Cross-cutting concerns:**
- `app/core/` — Security (JWT, bcrypt), auth dependencies, role-based access
- `app/exceptions/` — Custom exception classes per domain
- `app/schemas/` — Pydantic validation/response models
- `app/constants/` — Enums for statuses, shifts, roles
- `app/dependencies.py` — FastAPI DI (database session, OAuth2 scheme)

## Data Flow

```
HTTP Request
  → FastAPI Router (app/routers/*.py)
    → Dependency Injection (get_db, get_current_user)
      → Service Method (app/services/*.py)
        → SQLAlchemy ORM (app/models/*.py)
          → PostgreSQL
        ← ORM Result
      ← Service response (ORM model or dict)
    ← Router formats HTTP response
  ← HTTP Response (JSON)
```

## Authentication Flow

```
POST /auth/login (username, password)
  → auth_service.login() verifies credentials
  → Returns JWT access_token (sub=username, role, exp=30min)
  → Client includes "Authorization: Bearer <token>" header

Protected endpoints:
  → Depends(get_current_user) decodes JWT → queries User by username
  → Depends(require_role(["OWNER"])) checks role against allowed list
  → 401 for invalid/missing token, 403 for insufficient role
```

## Error Handling Pattern

All routers follow a consistent exception-mapping pattern:

```python
try:
    result = service.method(db, ...)
    return result
except DomainException as e:
    raise HTTPException(status_code=XXX, detail=str(e))
```

Exception → HTTP status mapping:
| Exception | Status Code |
|-----------|-------------|
| `*NotFoundError` | 404 |
| `*Duplicate*Error` | 400 |
| `Inactive*Error` | 400 |
| `Invalid*Error` | 400 |
| `SamePhoneNumberError` | 400 |

## Soft Delete Pattern

All entities use soft-delete. No hard deletes exist.

```python
# Service layer
entity.is_active = False
db.commit()
return entity

# Query filters
db.query(Model).filter(Model.is_active == True).all()
```

## Key Design Decisions

1. **No repository pattern** — Services interact directly with SQLAlchemy Session
2. **No unit-of-work** — Each service method commits independently
3. **Exception-based error handling** — Custom exceptions mapped to HTTP errors in routers
4. **Pydantic v2** — Using `model_config = ConfigDict(from_attributes=True)` for ORM mode
5. **No global auth middleware** — Authentication is opt-in per endpoint via `Depends()`
6. **PostgreSQL-specific** — Uses `server_default=func.now()` which is PG syntax

## File Inventory

### Implemented (with logic)
- `app/core/config.py` — Constants (SECRET_KEY, ALGORITHM, EXPIRE_MINUTES)
- `app/core/security.py` — hash_password, verify_password, create/decode JWT
- `app/core/auth.py` — get_current_user dependency
- `app/core/roles.py` — require_role dependency factory
- `app/dependencies.py` — get_db, oauth2_scheme
- `app/database.py` — engine, SessionLocal, Base
- `app/models/` — 6 ORM models (User, Route, Customer, MilkType, Employee, Subscription)
- `app/schemas/` — 6 schema modules with Pydantic models
- `app/routers/` — 6 routers (auth, users, routes, customers, milk_types, subscriptions)
- `app/services/` — 5 services (auth, user, route, milk_type, customer, subscription)
- `app/exceptions/` — Exception classes across 4 modules
- `app/constants/` — 3 enum modules (roles, statuses, shifts)

### Empty Stubs (placeholder only)
- `app/routers/employees.py`
- `app/routers/token_books.py`
- `app/routers/milk_allocation.py`
- `app/routers/cash_sales.py`
- `app/routers/reports.py`
- `app/routers/dashboard.py`
- `app/services/token_service.py`
- `app/services/delivery_service.py`
- `app/services/reconciliation_service.py`
- `app/schemas/token_book.py`
- `app/schemas/cash_sale.py`
- `app/exceptions/token_book.py`
- `app/exceptions/delivery.py`
- `app/utils/validators.py`
- `app/utils/helpers.py`
- `app/common/__init__.py`
- `app/core/constants.py`
