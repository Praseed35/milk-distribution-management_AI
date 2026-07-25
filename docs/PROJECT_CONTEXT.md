# Project Context: Milk Management AI

## Overview

Milk Management AI is a backend API for managing a milk distribution business. It handles the complete lifecycle: customer registration, subscription management, delivery tracking, token bookkeeping, payment reconciliation, and AI-powered business insights.

## Purpose

Replace manual/legacy milk distribution operations with a digital system that supports:
- Multi-shift (morning/evening) milk delivery scheduling
- Route-based customer and delivery management
- Token-based accounting for daily milk transactions
- Financial reconciliation and payment tracking
- AI-driven analytics and business suggestions

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.138.0 |
| ORM | SQLAlchemy 2.0.51 |
| Database | PostgreSQL (via psycopg2-binary 2.9.12) |
| Migrations | Alembic 1.18.4 |
| Auth | JWT (python-jose 3.5.0) + bcrypt (passlib 1.7.4) |
| Validation | Pydantic 2.13.4 |
| Testing | pytest (via TestClient) |
| Server | Uvicorn 0.49.0 |

## Directory Structure

```
milk-management - AI/
├── app/                        # Main application package
│   ├── core/                   # Security, auth, config, roles
│   │   ├── auth.py             # Token verification logic
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── roles.py            # Role constants
│   │   └── security.py         # Password hashing, JWT creation
│   ├── constants/              # Enums (roles, statuses, shifts)
│   │   ├── roles.py
│   │   ├── shifts.py
│   │   └── statuses.py
│   ├── models/                 # SQLAlchemy ORM models (7 implemented)
│   │   ├── customer.py
│   │   ├── delivery_exception.py
│   │   ├── employee.py
│   │   ├── milk_type.py
│   │   ├── route.py
│   │   ├── subscription.py
│   │   └── user.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── delivery_exception.py
│   │   ├── employee.py
│   │   ├── milk_type.py
│   │   ├── route.py
│   │   ├── subscription.py
│   │   └── user.py
│   ├── routers/                # FastAPI route handlers (7 implemented)
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── delivery_exceptions.py
│   │   ├── milk_types.py
│   │   ├── routes.py
│   │   ├── subscriptions.py
│   │   └── users.py
│   ├── services/               # Business logic layer (7 implemented)
│   │   ├── auth_service.py
│   │   ├── customer_service.py
│   │   ├── delivery_exception_service.py
│   │   ├── milk_type_service.py
│   │   ├── route_service.py
│   │   ├── subscription_service.py
│   │   └── user_service.py
│   ├── exceptions/             # Custom exception hierarchy
│   │   ├── base.py
│   │   ├── customer.py
│   │   ├── delivery_exception.py
│   │   ├── milk_type.py
│   │   ├── route.py
│   │   ├── subscription.py
│   │   └── user.py
│   ├── utils/                  # Shared utilities (currently just __init__.py)
│   ├── common/                 # Shared utilities (currently just __init__.py)
│   ├── database.py             # DB engine, session, Base
│   ├── dependencies.py         # FastAPI dependencies (get_db, oauth2)
│   └── main.py                 # FastAPI app creation, router registration
├── alembic/                    # Database migration scripts
│   └── versions/               # 5 migration files (chronological chain)
├── tests/                      # Pytest test suite (6 test files, 170 tests)
├── scripts/                    # Seed data and manual test scripts
├── docs/                       # Detailed design documentation (16 files)
├── .ai/                        # AI knowledge base (this directory)
├── main.py                     # Root-level minimal FastAPI entry (unused?)
└── requirements.txt            # Python dependencies
```

## Key Entities (Implemented)

| Entity | Model File | Schema File | Service File | Router File | Exception File | Has CRUD API |
|--------|-----------|-------------|-------------|------------|----------------|:---:|
| User | `user.py` | `user.py` | `user_service.py` | `users.py` | `user.py` | Partial |
| Route | `route.py` | `route.py` | `route_service.py` | `routes.py` | `route.py` | Yes |
| Customer | `customer.py` | `customer.py` | `customer_service.py` | `customers.py` | `customer.py` | Yes |
| MilkType | `milk_type.py` | `milk_type.py` | `milk_type_service.py` | `milk_types.py` | `milk_type.py` | Yes |
| Employee | `employee.py` | `employee.py` | — | `employees.py` | — | Yes |
| Subscription | `subscription.py` | `subscription.py` | `subscription_service.py` | `subscriptions.py` | `subscription.py` | Yes |
| DeliveryException | `delivery_exception.py` | `delivery_exception.py` | `delivery_exception_service.py` | `delivery_exceptions.py` | `delivery_exception.py` | Yes |

## Key Entities (Planned — Files Deleted During Cleanup, Must Be Rebuilt)

The following empty stub files were removed in a codebase cleanup. They must be recreated when implementing the corresponding features:

| Entity | Purpose | Files That Need Creation |
|--------|---------|--------------------------|
| TokenBook | Token accounting for daily milk delivery tracking | model, schema, service, router, exception |
| MilkAllocation | Daily milk allocation per route/shift | model, schema, router |
| CashSale | Cash-based walk-in milk sales | model, schema, router |
| Reconciliation | Payment and delivery reconciliation | model, service |
| LeaveRequest | Employee leave management | model |
| Delivery | Individual delivery records | service, exception |

**Additional files removed during cleanup (empty stubs with no implementation):**
- **Routers:** `employees.py`, `token_books.py`, `milk_allocation.py`, `cash_sales.py`, `dashboard.py`, `reports.py`
- **Core:** `constants.py` (constants directory has `roles.py`, `shifts.py`, `statuses.py` instead)
- **Utils:** `helpers.py`, `validators.py`
- **Repositories directory:** `app/repositories/` was entirely empty and has been removed
- **API directory:** `app/api/` contained only `__pycache__` and has been removed

## Roles & Access Control

| Role | Description | API Access |
|------|-------------|------------|
| OWNER | Full system access, business owner | All endpoints |
| CHECKER | Verifies deliveries, manages tokens | Token/subscription endpoints |
| DELIVERY_PARTNER | Delivers milk, records deliveries | Delivery endpoints |

## Database

- **PostgreSQL** at `localhost:5432/milk_managemen_ai`
- **6 tables currently in schema:** `users`, `routes`, `customers`, `milk_types`, `employees`, `subscriptions`, `delivery_exceptions`
- All entities use soft-delete via `is_active` boolean flag
- Timestamps use `server_default=func.now()` with timezone

## Registered Routers (in `app/main.py`)

| Router | Prefix | Status |
|--------|--------|--------|
| `users` | — | Implemented |
| `auth` | — | Implemented |
| `routes` | — | Implemented |
| `customers` | — | Implemented |
| `milk_types` | — | Implemented |
| `subscriptions` | — | Implemented |
| `delivery_exceptions` | — | Implemented |

No stub/empty routers are registered. Dashboard and reports routers do not exist yet.

## Current Status

The project is in mid development. A cleanup pass removed all empty stub files and directories that contained no implementation, leaving a clean codebase with only files that have real content. Sprint 1 (Master Data: routes, customers, milk types, employees, users, auth) and Sprint 2 (Subscriptions + Delivery Exceptions) are complete. 170 automated tests are passing against PostgreSQL. Token management, delivery tracking, reconciliation, reports, and dashboard all need to be built.

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed development data
python scripts/seed.py

# Start server
uvicorn app.main:app --reload
```
