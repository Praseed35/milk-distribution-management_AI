# Database Guidelines

## Purpose

This document defines the database standards for the Milk Distribution Management System.

Every AI assistant must follow these guidelines when creating or modifying database models, queries, and migrations.

The goal is to maintain a consistent, scalable, and reliable database architecture.

---

# Technology

Database

- PostgreSQL

ORM

- SQLAlchemy ORM

Migration Tool

- Alembic

Raw SQL

Not recommended unless there is a proven performance requirement.

---

# Design Principles

The database should be

- Normalized
- Consistent
- Auditable
- Easy to maintain
- Business driven

Every table should represent a business entity.

---

# Model Organization

Each database table should have

```
Model

↓

Schema

↓

Service

↓

Router
```

Never create a model without integrating it into the application.

---

# Naming Conventions

Tables

Plural snake_case

Examples

```
customers

routes

cash_sales

milk_allocations

token_books
```

Model Classes

PascalCase

```
Customer

Route

CashSale

MilkAllocation
```

Columns

snake_case

```
customer_name

route_id

created_at
```

---

# Primary Keys

Every table must have a primary key.

Preferred naming

```
id
```

Do not create

```
customer_id

route_id
```

as primary key names.

Use them only as foreign keys.

---

# Foreign Keys

Foreign keys should always use

```
<entity>_id
```

Examples

```
customer_id

route_id

employee_id

token_book_id
```

Every relationship should enforce referential integrity.

---

# Relationships

Use SQLAlchemy relationships whenever appropriate.

Example

Customer

↓

Route

One customer belongs to one route.

Route

↓

Customers

One route has many customers.

Token Book

↓

Customer

One customer may own many token books.

Cash Sale

↓

Route

One route has many cash sales.

---

# Required Fields

Business critical fields should never be nullable.

Examples

```
customer_name

route_id

delivery_date

milk_type

quantity
```

Optional fields should explicitly allow NULL.

---

# Audit Fields

Business tables should contain audit information whenever appropriate.

Recommended

```
created_at

updated_at

created_by

updated_by
```

This improves traceability.

---

# Soft Delete

Business records should rarely be permanently deleted.

Preferred

```
is_active = False
```

Avoid

```
DELETE FROM customers
```

Historical business data should remain available.

---

# Business History

Never delete

- Customers
- Routes
- Deliveries
- Token Books
- Cash Sales
- Payments
- Reconciliation Records

History is part of the business.

---

# Constraints

Use database constraints whenever possible.

Examples

Unique

```
username

email

route_code
```

Foreign Keys

```
customer_id

route_id
```

Check Constraints

Positive quantity

Positive amount

---

# Indexes

Create indexes for frequently searched fields.

Recommended

```
customer_name

phone

route_id

delivery_date

created_at
```

Avoid indexing every column.

Indexes improve reads but slow writes.

---

# Transactions

A transaction should represent one business operation.

Example

Issue Token Book

↓

Create Token Book

↓

Generate 30 Token Sheets

↓

Commit

If any step fails

↓

Rollback

Never commit partial business operations.

---

# Session Management

Always use the injected SQLAlchemy session.

Example

```
db: Session
```

Never create new sessions inside services.

Never create multiple sessions for one request.

---

# Query Guidelines

Prefer ORM queries.

Good

```python
customer = (
    db.query(Customer)
    .filter(Customer.id == customer_id)
    .first()
)
```

Avoid unnecessary queries.

Reuse loaded objects whenever possible.

---

# Performance

Avoid

N+1 queries.

Repeated database lookups.

Repeated commits.

Repeated refresh calls.

Load only required data.

---

# Relationships

Prefer explicit relationships.

Example

```python
route = relationship("Route")
```

instead of manually joining everywhere.

---

# Lazy Loading

Use lazy loading carefully.

Use eager loading when retrieving related business data repeatedly.

Avoid unnecessary relationship loading.

---

# Model Responsibilities

Models should contain

- Columns
- Relationships
- Constraints

Models should NOT contain

- Business logic
- Validation
- HTTP handling

Keep models lightweight.

---

# Service Responsibilities

Database operations belong in services.

Services should

- Query
- Create
- Update
- Delete (soft delete)

Routers should never access models directly.

---

# Alembic Rules

Every schema change requires a migration.

Examples

New table

↓

Create migration

↓

Review migration

↓

Apply migration

Never manually modify production schemas.

---

# Migration Naming

Good

```
add_customer_table

add_cash_sale_indexes

add_token_book_status
```

Bad

```
fix

update

temp
```

Migration names should describe the change.

---

# Data Integrity

Always validate

- Foreign keys
- Duplicate records
- Required fields
- Business constraints

Validation should occur

Pydantic

↓

Service

↓

Database

---

# Business Examples

Customer Creation

```
Validate request

↓

Verify route exists

↓

Create customer

↓

Commit
```

Cash Sale

```
Validate milk type

↓

Create cash sale

↓

Update reconciliation

↓

Commit
```

Token Book

```
Validate customer

↓

Create token book

↓

Generate 30 sheets

↓

Commit
```

---

# AI Checklist

Before creating a model

✔ Verify similar models exist

✔ Follow naming conventions

✔ Add relationships

✔ Add constraints

✔ Consider indexes

✔ Preserve business history

Before writing queries

✔ Use ORM

✔ Avoid duplicate queries

✔ Use transactions

✔ Reuse loaded objects

✔ Handle exceptions

Never

- Use raw SQL without reason.
- Delete business history.
- Bypass SQLAlchemy.
- Create unnecessary sessions.
- Commit partial operations.
- Ignore foreign key relationships.

---

# Golden Rule

The database represents the business.

Every table, column, relationship, and transaction should model a real business concept.

Never design the database for convenience alone—design it to accurately reflect the milk distribution workflow.