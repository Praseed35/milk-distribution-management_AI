# Module Implementation Guide

## Purpose

This document defines the standard implementation pattern for every new business module in the Milk Distribution Management System.

Every module must follow the same architecture, coding standards, and business validation flow to ensure consistency across the project.

This guide applies to both manually written code and AI-generated code.

---

# Standard Module Structure

Every business module should contain the following components.

```
app/

models/
    customer.py

schemas/
    customer.py

services/
    customer_service.py

routers/
    customer.py

exceptions/
    customer.py
```

If a module requires constants, utilities, or validators, they should be placed in the existing shared directories instead of creating module-specific utility folders.

---

# Module Development Order

Always build modules in the following sequence.

```
Business Rules

↓

Database Model

↓

Pydantic Schemas

↓

Business Exceptions

↓

Service Layer

↓

API Router

↓

Database Migration

↓

Automated Tests

↓

Documentation
```

Do not skip intermediate steps.

---

# Step 1 — Business Analysis

Before writing code, identify:

- Business purpose
- Business owner (Owner, Checker, Delivery Partner)
- Relationships with existing modules
- Validation rules
- Reporting impact
- Audit requirements

Questions to answer

- What problem does this module solve?
- Which workflow does it belong to?
- What historical data must be preserved?

---

# Step 2 — Database Model

Create the SQLAlchemy model.

Example

```
Customer
```

Include

- Primary key
- Foreign keys
- Relationships
- Constraints
- Audit fields

Avoid putting business logic inside models.

---

# Step 3 — Schemas

Create request and response schemas.

Typical schemas

```
CustomerCreate

CustomerUpdate

CustomerResponse

CustomerListResponse
```

Validation belongs in schemas only for

- Required fields
- Types
- Length
- Formats

Business validation belongs in services.

---

# Step 4 — Exceptions

Create module-specific exceptions.

Example

```
CustomerNotFound

DuplicateCustomer

InactiveCustomer
```

Exceptions should describe business problems rather than technical failures.

---

# Step 5 — Service Layer

The service contains all business logic.

Typical responsibilities

- Validation
- Database operations
- Transactions
- Exception handling
- Business workflow execution

Never place business logic in routers.

---

# Step 6 — Router

Routers expose REST endpoints.

Responsibilities

- Request validation
- Dependency injection
- Authentication
- Calling services
- Returning response schemas

Routers must remain thin.

---

# Step 7 — Database Migration

If the schema changes

```
Modify model

↓

Generate Alembic migration

↓

Review migration

↓

Apply migration

↓

Verify schema
```

Never modify production tables manually.

---

# Step 8 — Tests

Every module should include

Unit Tests

- Business validation
- Exceptions

Service Tests

- Business workflow
- Database changes

API Tests

- Authentication
- Authorization
- Status codes
- Response schemas

Integration Tests

- End-to-end workflow

---

# Standard CRUD Operations

Most modules should implement

```
Create

Read

List

Update

Deactivate (preferred)

Delete (only if business allows)
```

Deletion should be avoided for operational data.

---

# Business Validation Pattern

Every create or update operation should follow this order.

```
Validate Request

↓

Verify Related Records

↓

Check Business Rules

↓

Perform Operation

↓

Commit Transaction

↓

Return Response
```

---

# Authentication Pattern

Every protected endpoint should

```
Receive JWT

↓

Validate User

↓

Check Role

↓

Execute Service
```

Do not bypass dependency injection.

---

# Error Handling Pattern

Business validation failures

↓

Custom Exceptions

↓

Global Exception Handler

↓

Consistent API Response

Do not return ad hoc error structures.

---

# Audit Requirements

Each module should consider

- Who created the record?
- When was it created?
- Who modified it?
- When was it modified?
- Is the change traceable?

Business-critical actions should remain auditable.

---

# Performance Guidelines

When adding a module

- Avoid N+1 queries.
- Reuse loaded entities.
- Commit once per business transaction.
- Add indexes only where justified.

---

# Example Modules

Current modules

- Authentication
- Customers
- Routes
- Employees
- Token Books
- Deliveries
- Cash Sales
- Payments
- Reconciliation

Future modules

- Inventory
- Customer Subscriptions
- Notifications
- Reports
- Vehicle Management
- Branch Management

Each should follow the same implementation pattern.

---

# Module Checklist

Before creating a module

✔ Understand the business workflow.

✔ Identify related entities.

✔ Design the database model.

✔ Define request and response schemas.

✔ Create custom exceptions.

✔ Implement business logic in services.

✔ Expose REST endpoints.

✔ Create database migrations.

✔ Write automated tests.

✔ Update documentation.

---

# AI Instructions

When implementing a new module

1. Follow the standard module structure.
2. Reuse existing services and utilities whenever possible.
3. Keep business logic in the Service Layer.
4. Use SQLAlchemy ORM.
5. Follow existing API conventions.
6. Preserve backward compatibility.
7. Ensure every business rule is enforced.

Never

- Skip business validation.
- Place business logic in routers.
- Duplicate existing functionality.
- Introduce a new architectural pattern.
- Modify unrelated modules unnecessarily.

---

# Golden Rule

Every module should look and behave as if it was developed by the same engineer.

Consistency across modules is more valuable than individual implementation preferences.