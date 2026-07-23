# PROJECT CONTEXT - Milk Distribution ERP

> **Read this file first when starting a new session.** It provides a complete overview of the project, its current state, and how to work with it.

---

## What Is This Project?

A **Milk Distribution ERP** (Enterprise Resource Planning) system for managing daily milk delivery operations. It replaces manual registers used by milk distribution companies with a digital system.

**Real-world analogy:** Think of it like Zomato/Swiggy but for daily milk delivery - managing customers, routes, subscriptions, daily deliveries, token-based payments, and reconciliation.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (JSON Web Tokens) |
| Python Version | 3.14 |

---

## Project Structure

```
milk-management - AI/
├── .ai/                    # AI documentation (read before coding)
├── alembic/                # Database migrations
│   └── versions/           # Migration files
├── app/                    # Main application code
│   ├── common/             # Shared components
│   ├── constants/          # roles.py, shifts.py, statuses.py
│   ├── core/               # auth.py, config.py, security.py
│   ├── exceptions/         # Custom exceptions per module
│   ├── models/             # SQLAlchemy ORM models
│   ├── repositories/       # Empty (not yet implemented)
│   ├── routers/            # FastAPI endpoints
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic
│   ├── utils/              # Helper functions
│   ├── database.py         # DB engine, session, base
│   ├── dependencies.py     # FastAPI dependencies (get_db)
│   └── main.py             # App entry point
├── docs/                   # Human-readable documentation
├── scripts/                # Utility scripts (seed, test)
├── tests/                  # Test files (empty)
├── alembic.ini             # Alembic configuration
├── requirements.txt        # Python dependencies
└── main.py                 # Root main.py (DO NOT USE - use app/main.py)
```

**IMPORTANT:** Run the app with `uvicorn app.main:app --reload`, NOT `uvicorn main:app`

---

## Architecture Pattern

```
HTTP Request
    ↓
Router (thin - validates request)
    ↓
Service (business logic)
    ↓
Model (SQLAlchemy ORM)
    ↓
Database (PostgreSQL)
```

**Rules:**
- Business logic goes in services, NOT routers
- Routers only validate and call services
- No SQL in routers
- Use dependency injection for DB sessions

---

## Database Connection

```python
# From alembic.ini
postgresql://postgres:admin@localhost:5432/milk_managemen_ai
```

---

## Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Owner | `owner` | `owner123` |
| Checker | `checker1` | `checker123` |
| Delivery Partner | `delivery1` | `delivery123` |
| Admin | `admin` | `admin123` |

---

## Seeded Data

| Entity | Count | IDs |
|--------|-------|-----|
| Users | 4 | 1-4 |
| Customers | 15 | 1-15 |
| Routes | 5 | 1-5 |
| Milk Types | 7 | 1-7 |
| Employees | 5 | 1-5 |

---

## Current Module Status (July 2026)

### Completed Modules

| Module | Model | Router | Service | Endpoints |
|--------|-------|--------|---------|-----------|
| Authentication | User | auth | auth_service | POST /auth/login, GET /auth/me |
| Users | User | users | user_service | CRUD |
| Customers | Customer | customers | customer_service | CRUD |
| Routes | Route | routes | route_service | CRUD |
| Milk Types | MilkType | milk_types | milk_type_service | CRUD |
| Employees | Employee | employees | - | CRUD |
| Subscriptions | Subscription | subscriptions | subscription_service | CRUD |

### In-Progress Modules (Partial)

| Module | Model | Router | Service | Status |
|--------|-------|--------|---------|--------|
| Token Books | TokenBook | token_books | token_service | Partial |
| Cash Sales | CashSale | cash_sales | - | Partial |
| Milk Allocation | MilkAllocation | milk_allocation | delivery_service | Partial |
| Reconciliation | Reconciliation | - | reconciliation_service | Partial |

### Not Started

- Daily Delivery Planning
- Token Ledger
- Payment Management
- Reports (Router exists, service incomplete)
- AI Reports
- Frontend (React)

---

## API Base URL

```
http://localhost:8000
```

All endpoints require JWT token except `/auth/login`.

**Headers for authenticated requests:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

---

## Key Business Rules

1. **Delivery and Payment are Independent** - Milk delivered even if payment not received immediately
2. **Token Books are Payment Instruments** - Used for payment, not delivery decisions
3. **Subscriptions Determine Delivery** - What customer gets is based on subscription
4. **Reconciliation Ensures Accountability** - Every route must be balanced before closing
5. **Soft Delete** - Records are deactivated, never permanently deleted
6. **Re-subscription Allowed** - After deactivation, customer can re-subscribe

---

## Module Dependency Chain

```
Customer → Subscription → Daily Delivery → Token Ledger → Reports
    ↓
   Route
```

**Next module to build:** Daily Delivery Planning (depends on Subscriptions)

---

## How to Add a New Module

Follow this order for every new module:

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create exceptions in `app/exceptions/`
4. Create service in `app/services/`
5. Create router in `app/routers/`
6. Register router in `app/main.py`
7. Update `app/models/__init__.py`
8. Generate Alembic migration
9. Test with Postman or test script

---

## Common Commands

```bash
# Run the app
uvicorn app.main:app --reload

# Generate migration
python -m alembic revision --autogenerate -m "description"

# Apply migration
python -m alembic upgrade head

# Seed database
python scripts/seed.py

# Run tests
python scripts/test_subscriptions.py
```

---

## Documentation Locations

| Folder | Purpose |
|--------|---------|
| `.ai/` | AI-specific docs (architecture, rules, patterns) |
| `docs/` | Human-readable docs (business rules, API spec) |

**AI should read `.ai/` folder before generating code.**

---

## Known Issues

- Reports API router exists but service is incomplete
- No automated tests yet
- `app/repositories/` folder is empty (planned for future)
- Root `main.py` is empty - always use `app/main.py`

---

## Next Steps (Priority Order)

1. **Daily Delivery Planning** - Generate daily delivery lists from subscriptions
2. **Token Ledger** - Track token usage per customer
3. **Payment Management** - Handle token book payments
4. **Reports** - Complete reporting module
5. **Frontend** - React application

---

*Last updated: July 2026*
