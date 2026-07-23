# Folder Structure

## Purpose

This document defines the official folder structure of the Milk Distribution Management System.

Every AI assistant must follow this structure when creating new files.

The goal is to keep the project organized, maintainable, and consistent.

---

# Project Structure

```
milk-management/

├── .ai/
├── alembic/
├── app/
├── docs-v1/
├── scripts/
├── tests/
├── main.py
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# app/

The `app` directory contains all application source code.

```
app/

├── common/
├── constants/
├── core/
├── exceptions/
├── models/
├── routers/
├── schemas/
├── services/
├── utils/
├── database.py
├── dependencies.py
└── main.py
```

No business logic should exist outside this directory.

---

# common/

Purpose

Contains reusable components shared across multiple modules.

Examples

- Base classes
- Shared DTOs
- Generic helpers
- Common response objects

Should NOT contain

- Customer logic
- Route logic
- Delivery logic

---

# constants/

Purpose

Contains application constants.

Current Examples

- roles.py
- shifts.py
- statuses.py

Allowed

```python
ADMIN

DELIVERY_PARTNER

CHECKER

ACTIVE

INACTIVE

MORNING_SHIFT
```

Never hardcode constant values inside routers or services.

---

# core/

Purpose

Contains application configuration and security.

Current Files

```
auth.py
config.py
constants.py
roles.py
security.py
```

Responsibilities

- JWT configuration
- Password hashing
- Environment variables
- Security helpers
- Application configuration

Never place business logic here.

---

# exceptions/

Purpose

Contains custom exceptions.

Current Files

```
base.py

customer.py

delivery.py

route.py

token_book.py

user.py
```

Every business module should define its own exceptions.

Example

```
CustomerNotFound

DuplicateCustomer

RouteAlreadyExists

InvalidTokenBook
```

Never raise generic Exception in business code.

---

# models/

Purpose

Contains SQLAlchemy ORM models.

Current Models

```
cash_sale.py

customer.py

employee.py

leave_request.py

milk_allocation.py

reconciliation.py

route.py

token_book.py

user.py
```

Responsibilities

- Table definitions
- Relationships
- Constraints
- Indexes

Models should contain

- Columns
- Foreign Keys
- Relationships

Models should NOT contain

- Business rules
- API validation
- HTTP logic

---

# routers/

Purpose

Defines FastAPI endpoints.

Current Routers

```
auth.py

cash_sales.py

customers.py

dashboard.py

employees.py

milk_allocation.py

reports.py

routes.py

token_books.py

users.py
```

Responsibilities

- Define endpoints
- Validate requests
- Inject dependencies
- Call services
- Return responses

Routers should be thin.

Never

- Query the database
- Implement calculations
- Write business logic

Example

```
POST /customers

↓

customer_service.create_customer()
```

---

# schemas/

Purpose

Contains Pydantic models.

Current Schemas

```
auth.py

cash_sale.py

customer.py

employee.py

route.py

token_book.py

user.py
```

Schema Types

- Create
- Update
- Response
- Login
- Filter

Responsibilities

- Request validation
- Response serialization
- Type validation

Never

- Query the database
- Execute business logic

---

# services/

Purpose

Contains all business logic.

Current Services

```
auth_service.py

customer_service.py

delivery_service.py

reconciliation_service.py

route_service.py

token_service.py

user_service.py
```

Responsibilities

- Business validation
- Workflow execution
- SQLAlchemy operations
- Transactions
- Rule enforcement

Services may use

- Models
- SQLAlchemy Session
- Utilities
- Constants
- Exceptions

Services should never

- Return HTTP responses
- Access FastAPI Request objects
- Define API routes

Every router should delegate work to a service.

---

# utils/

Purpose

Contains helper functions.

Current Files

```
helpers.py

validators.py
```

Examples

- Date formatting
- Phone validation
- Utility methods
- Shared validators

Utilities should remain stateless.

Never access the database from utilities.

---

# database.py

Purpose

Application database configuration.

Responsibilities

- SQLAlchemy Engine
- Session Factory
- Declarative Base
- Database Connection

Every database operation should use the configured session.

---

# dependencies.py

Purpose

Reusable FastAPI dependencies.

Examples

- Database session
- Current user
- JWT authentication
- Role validation

Never implement business workflows here.

---

# main.py

Purpose

Application entry point.

Responsibilities

- Create FastAPI application
- Register routers
- Middleware
- Startup events
- Shutdown events

Never implement business logic inside main.py.

---

# docs-v1/

Purpose

Human-readable project documentation.

Contains

- Business Rules
- Database Design
- API Specification
- Testing Strategy
- Architecture
- Roadmaps

This directory is written for developers.

---

# .ai/

Purpose

Documentation specifically for AI coding assistants.

Contains

- Architecture
- Coding Rules
- Development Rules
- Examples
- Naming Standards
- AI Prompts

Every AI assistant should read this folder before generating code.

---

# scripts/

Purpose

Utility scripts for development and maintenance.

Examples

- Seed data
- Data migration
- Cleanup
- Import/export

Scripts should not contain production business logic.

---

# tests/

Purpose

Automated tests.

Future Structure

```
tests/

unit/

integration/

api/

fixtures/
```

Tests should mirror the application structure.

---

# Dependency Rules

Allowed

```
Router
    ↓
Service
    ↓
Model
    ↓
Database
```

Utilities

```
Service
    ↓
Utils
```

Schemas

```
Router
    ↓
Schema
```

---

# Forbidden Dependencies

Never

```
Router
    ↓
Database
```

Never

```
Router
    ↓
Model
```

Never

```
Model
    ↓
Service
```

Never

```
Utils
    ↓
Router
```

Never

```
Exception
    ↓
Router
```

---

# Creating a New Module

When adding a new feature, create the required files.

Example

Inventory

```
models/inventory.py

schemas/inventory.py

services/inventory_service.py

routers/inventory.py

exceptions/inventory.py
```

Update

- main.py
- module_map.md
- feature_status.md

if required.

---

# AI Instructions

Before creating any file

1. Check whether a similar module already exists.
2. Follow the existing folder structure.
3. Keep routers thin.
4. Place business logic only in services.
5. Use SQLAlchemy ORM consistently.
6. Reuse utilities and constants.
7. Raise custom exceptions.
8. Maintain consistency with existing modules.

Never introduce a new folder or architectural pattern without explicit approval.