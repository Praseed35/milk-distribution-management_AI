# Coding Rules

## Purpose

This document defines the coding standards for the Milk Distribution Management System.

Every AI assistant must follow these rules whenever creating or modifying code.

The goal is to keep the codebase consistent, readable, maintainable, and scalable.

---

# General Principles

Always write code that is

- Simple
- Readable
- Maintainable
- Reusable
- Explicit
- Predictable

Never sacrifice readability for cleverness.

Always prefer clarity over brevity.

---

# Python Standards

Follow

- PEP 8
- PEP 484 (Type Hints)

Always use

- snake_case for variables and functions
- PascalCase for classes
- UPPER_CASE for constants

Example

Good

```python
def create_customer():
    ...
```

Bad

```python
def CreateCustomer():
    ...
```

---

# Type Hints

Every function must use type hints.

Good

```python
def create_customer(
    customer: CustomerCreate,
    db: Session
) -> Customer:
```

Bad

```python
def create_customer(customer, db):
```

---

# File Organization

Every file should have one responsibility.

Avoid creating files larger than approximately 500 lines.

If a service becomes too large, split it into smaller services.

---

# Router Rules

Routers are responsible only for HTTP.

Routers should

- Validate request schemas
- Inject dependencies
- Call services
- Return responses

Routers should never

- Query the database
- Contain business logic
- Perform calculations
- Access ORM models directly

Good

```python
return customer_service.create_customer(db, payload)
```

Bad

```python
customer = Customer(...)
db.add(customer)
db.commit()
```

---

# Service Rules

The Service Layer contains all business logic.

Services should

- Validate business rules
- Query the database
- Update models
- Raise business exceptions
- Return domain objects

Services should never

- Return HTTP responses
- Access FastAPI Request objects
- Define routes

---

# SQLAlchemy Rules

Always use

SQLAlchemy ORM.

Avoid raw SQL unless performance requires it.

Use

- relationships
- foreign keys
- indexes

appropriately.

Always commit transactions intentionally.

Never commit multiple unrelated operations together.

---

# Schema Rules

Use Pydantic models for

- Requests
- Responses
- Validation

Never expose SQLAlchemy models directly in API responses.

---

# Validation

Validation occurs in two stages.

Stage 1

Pydantic

- Required fields
- Types
- Formats

Stage 2

Service

- Business rules
- Duplicate checks
- Route existence
- Token availability

---

# Exception Handling

Never raise generic Exception.

Use custom exceptions.

Example

Good

```python
raise CustomerNotFound()
```

Bad

```python
raise Exception("Customer missing")
```

---

# Logging

Log important business events.

Examples

- User login
- Customer creation
- Token book issuance
- Route reconciliation
- Cash sale creation

Never log

- Passwords
- JWT tokens
- Sensitive information

---

# Database Transactions

Group related operations inside one transaction.

Example

Issue token book

↓

Create book

↓

Create token sheets

↓

Commit

If any step fails

↓

Rollback

---

# Reusability

Before writing new code

Check whether

- helper exists
- validator exists
- service exists
- constant exists

Reuse existing code whenever possible.

---

# Constants

Never hardcode

Roles

Statuses

Shift names

Milk types

Example

Good

```python
Role.ADMIN
```

Bad

```python
"admin"
```

---

# Naming

Choose meaningful names.

Good

```python
calculate_daily_allocation()
```

Bad

```python
calc()
```

---

# Comments

Write comments only when necessary.

Good comments explain

WHY

not

WHAT

Bad

```python
# Increment i

i += 1
```

Good

```python
# Prevent duplicate token issuance
```

---

# Imports

Import only what is required.

Order

1 Standard Library

2 Third-party

3 Local Project

Example

```python
from datetime import datetime

from fastapi import APIRouter

from app.models.customer import Customer
```

---

# API Responses

Always return

- Response schemas
- Consistent messages
- Proper status codes

Never return ORM objects directly.

---

# Performance

Avoid

- N+1 queries
- Duplicate database calls
- Repeated calculations

Use eager loading where appropriate.

---

# Security

Never

- Store passwords
- Log secrets
- Trust client input
- Skip authentication

Always validate user permissions before performing protected operations.

---

# Code Duplication

Never duplicate business logic.

If logic is used multiple times

↓

Extract helper

↓

Extract utility

↓

Extract service

---

# Future Development

New modules should follow existing architecture.

Example

Inventory

```
models/inventory.py

schemas/inventory.py

services/inventory_service.py

routers/inventory.py

exceptions/inventory.py
```

Do not invent new patterns.

Follow existing project conventions.

---

# AI Instructions

Before writing code

1. Read the existing implementation.
2. Reuse existing services.
3. Follow project architecture.
4. Use SQLAlchemy ORM.
5. Use custom exceptions.
6. Use type hints.

After writing code

- Check imports
- Check formatting
- Check naming
- Verify consistency
- Preserve backward compatibility

Never

- Put business logic inside routers.
- Return ORM models directly.
- Duplicate code.
- Hardcode business values.
- Break existing APIs.