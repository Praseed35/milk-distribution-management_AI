# Service Patterns

## Purpose

This document defines the implementation patterns for the Service Layer.

Every AI assistant must follow these patterns when creating or modifying services.

The Service Layer is the heart of the application.

It contains all business logic and coordinates interactions between routers, models, utilities, and the database.

---

# Service Responsibilities

A service is responsible for

- Business validation
- Workflow execution
- Database operations
- Transaction management
- Business rule enforcement
- Calling helper functions
- Raising business exceptions

Services are **the only layer where business logic belongs**.

---

# Service Flow

```
HTTP Request

↓

Router

↓

Pydantic Validation

↓

Service

↓

Business Validation

↓

Database Operations

↓

Business Response

↓

Router

↓

HTTP Response
```

---

# Rules

A service should

- Receive validated data
- Validate business rules
- Query the database
- Create or update models
- Raise custom exceptions
- Return domain objects

A service should NOT

- Define API routes
- Return HTTP responses
- Access Request objects
- Perform authentication directly
- Contain presentation logic

---

# Standard Service Structure

```python
class CustomerService:

    @staticmethod
    def create_customer(
        db: Session,
        payload: CustomerCreate,
        current_user: User,
    ) -> Customer:
        ...
```

Rules

- Use descriptive method names
- Use type hints
- Keep methods focused
- Return models or schemas consistently

---

# Validation Order

Always validate in this order.

Step 1

Pydantic

Examples

- Required fields
- Types
- Length
- Email format

↓

Step 2

Business validation

Examples

- Duplicate customer
- Invalid route
- Customer inactive
- Route inactive

↓

Step 3

Database update

↓

Step 4

Commit

↓

Step 5

Return object

---

# Business Validation

Business validation belongs only in services.

Example

```python
if not route:
    raise RouteNotFound()

if not route.is_active:
    raise RouteInactive()
```

Never perform business validation inside routers.

---

# Database Access

Services interact directly with SQLAlchemy.

Example

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

# Create Pattern

Standard workflow

```
Validate request

↓

Business validation

↓

Create model

↓

Add to session

↓

Commit

↓

Refresh

↓

Return
```

Example

```python
customer = Customer(**payload.model_dump())

db.add(customer)

db.commit()

db.refresh(customer)

return customer
```

---

# Update Pattern

Workflow

```
Find record

↓

Validate

↓

Update fields

↓

Commit

↓

Refresh

↓

Return
```

Example

```python
customer.phone = payload.phone

customer.address = payload.address

db.commit()

db.refresh(customer)
```

---

# Delete Pattern

Business records should rarely be deleted.

Preferred

Soft delete.

Example

```python
customer.is_active = False
```

Avoid

```python
db.delete(customer)
```

unless explicitly required.

---

# Transactions

When multiple operations belong together

Use one transaction.

Example

Issue Token Book

↓

Create token book

↓

Generate 30 token sheets

↓

Commit

If any step fails

↓

Rollback

---

# Rollback Pattern

```python
try:
    ...

    db.commit()

except Exception:

    db.rollback()

    raise
```

Never leave partial business data.

---

# Business Workflow Example

Create Customer

```
Validate request

↓

Verify route exists

↓

Verify customer uniqueness

↓

Create customer

↓

Commit

↓

Return customer
```

---

# Token Book Workflow

```
Validate customer

↓

Validate milk type

↓

Generate token book

↓

Generate 30 token sheets

↓

Commit

↓

Return token book
```

All steps must succeed together.

---

# Cash Sale Workflow

```
Validate milk type

↓

Validate quantity

↓

Record cash sale

↓

Update reconciliation totals

↓

Commit
```

---

# Reconciliation Workflow

```
Calculate

Loaded Milk

↓

Delivered Milk

↓

Cash Sales

↓

Returned Milk

↓

Compare

↓

Balanced?

↓

Close Route
```

Routes should never close while unbalanced.

---

# Utility Usage

Services may use

```
helpers.py

validators.py
```

Utilities should never contain business rules.

---

# Constants

Always use constants.

Example

```python
Role.OWNER

Status.ACTIVE
```

Never use

```python
"owner"

"active"
```

---

# Exception Usage

Raise specific exceptions.

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

Log

- Customer created
- Token book issued
- Cash sale recorded
- Reconciliation completed
- User login

Never log

- Passwords
- JWT tokens
- Sensitive personal data

---

# Performance

Avoid

- Duplicate queries
- Nested loops over database results
- Repeated commits

Commit once whenever possible.

---

# Future Services

Every new business module should have its own service.

Example

```
inventory_service.py

subscription_service.py

notification_service.py
```

Never place business logic inside routers to avoid creating unnecessary services.

---

# AI Checklist

Before creating a service

✔ Read existing services

✔ Follow naming conventions

✔ Use SQLAlchemy ORM

✔ Use type hints

✔ Raise custom exceptions

✔ Reuse helper functions

✔ Follow existing workflows

After creating a service

✔ Check imports

✔ Remove duplicate logic

✔ Verify transaction safety

✔ Ensure business rules are preserved

✔ Keep methods concise

---

# Golden Rule

The Service Layer is the single source of truth for business logic.

If a rule affects how the business operates, it belongs in a service—not in a router, model, schema, or utility.