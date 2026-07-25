# DATABASE.md - Complete Database Schema

> All 10 tables with columns, constraints, relationships, and migration history.

---

## Connection

```
PostgreSQL @ localhost:5432
Database: milk_managemen_ai
User: postgres
Password: admin
URL: postgresql://postgres:admin@localhost:5432/milk_managemen_ai
```

---

## Entity Relationship Diagram

```
users ─────────────┐
                    │
routes ────────┐   │
    │          │   │
    │     customers
    │          │   │
    │          ├───┼── employees.user_id
    │          │   │
    │     subscriptions
    │          │
    │     delivery_exceptions
    │
    ├─── token_identities
    │         │
    │    token_book_issues
    │         │
    │    token_book_payments
    │              └── token_book_payments.collected_by -> users.id
    │
    └─── employees.route_id
```

---

## Table: users

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY | Auto-increment |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Login identifier |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hash |
| role | VARCHAR(50) | NOT NULL | OWNER/CHECKER/DELIVERY_PARTNER/EMPLOYEE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |

**Unique constraints**: username
**Foreign keys**: None
**Relationships**: Referenced by employees.user_id, token_book_payments.collected_by

---

## Table: routes

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| route_code | VARCHAR | UNIQUE, NOT NULL | e.g., "R001" |
| route_name | VARCHAR | UNIQUE, NOT NULL | e.g., "Downtown Route" |
| description | VARCHAR | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: route_code, route_name
**Foreign keys**: None
**Relationships**: Has many customers, has many employees

---

## Table: customers

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| customer_code | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated: C00001, C00002... |
| customer_name | VARCHAR(100) | NOT NULL | |
| primary_phone | VARCHAR(15) | UNIQUE, NOT NULL | 10-digit phone |
| alternate_phone | VARCHAR(15) | NULLABLE | 10-digit phone |
| address | VARCHAR(255) | NULLABLE | |
| route_id | INTEGER | FK -> routes.id, NOT NULL | |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: customer_code, primary_phone
**Foreign keys**: route_id -> routes.id
**Relationships**: Belongs to Route, has many Subscriptions, has many TokenIdentities

**Business rule**: `customer_code` auto-generated as `C{NNNNN}` by incrementing the last ID's code.

---

## Table: milk_types

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| milk_name | VARCHAR(100) | UNIQUE, NOT NULL | e.g., "Full Cream Milk" |
| volume_ml | INTEGER | NOT NULL | e.g., 1000, 500, 250 |
| description | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: milk_name
**Foreign keys**: None
**Relationships**: Referenced by Subscriptions, TokenIdentities

---

## Table: employees

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| employee_code | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated: E00001, E00002... |
| name | VARCHAR(100) | NOT NULL | |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | |
| address | VARCHAR(255) | NULLABLE | |
| role | VARCHAR(50) | NOT NULL | CHECKER/DELIVERY_PARTNER/etc |
| route_id | INTEGER | FK -> routes.id, NULLABLE | Assigned delivery route |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| user_id | INTEGER | FK -> users.id, NULLABLE | Optional linked user account |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: employee_code, phone
**Foreign keys**: route_id -> routes.id, user_id -> users.id
**Relationships**: Belongs to Route (optional), optionally linked to User

**Properties**: `username` property returns `self.user.username if self.user else None`

**Business rule**: `employee_code` auto-generated as `E{NNNNN}`. Employee creation can optionally create a linked User account (requires username, password, confirm_password all provided together).

---

## Table: subscriptions

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| customer_id | INTEGER | FK -> customers.id, NOT NULL | |
| milk_type_id | INTEGER | FK -> milk_types.id, NOT NULL | |
| morning_quantity | INTEGER | NOT NULL, DEFAULT 0 | Units per morning shift |
| evening_quantity | INTEGER | NOT NULL, DEFAULT 0 | Units per evening shift |
| status | VARCHAR(20) | NOT NULL, DEFAULT "ACTIVE" | ACTIVE/INACTIVE |
| start_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL | |
| end_date | TIMESTAMPTZ | NULLABLE | Set when deactivated |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: customer_id -> customers.id, milk_type_id -> milk_types.id
**Relationships**: Belongs to Customer, belongs to MilkType, has many DeliveryExceptions

**Business rules**:
- At least one of morning_quantity or evening_quantity must be > 0
- No duplicate active subscription for same customer + milk_type
- Deactivation sets is_active=False AND status="INACTIVE"

---

## Table: delivery_exceptions

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| subscription_id | INTEGER | FK -> subscriptions.id, NOT NULL | |
| exception_type | VARCHAR(20) | NOT NULL | VACATION/NO_MILK/HOLIDAY |
| start_date | TIMESTAMPTZ | NOT NULL | |
| end_date | TIMESTAMPTZ | NULLABLE | None = single-day exception |
| reason | VARCHAR(255) | NULLABLE | |
| status | VARCHAR(20) | NOT NULL, DEFAULT "ACTIVE" | ACTIVE/COMPLETED/CANCELLED |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: subscription_id -> subscriptions.id
**Relationships**: Belongs to Subscription

**Business rules**:
- Subscription must exist and be active
- end_date must be >= start_date
- No overlapping exceptions for the same subscription
- Cancellation sets is_active=False AND status="CANCELLED"

**Overlap detection**: `_check_overlap()` helper checks for date range intersection.

---

## Table: token_identities

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| customer_id | INTEGER | FK -> customers.id, NOT NULL | |
| milk_type_id | INTEGER | FK -> milk_types.id, NOT NULL | |
| token_number | INTEGER | NOT NULL | Physical token number |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: (customer_id, milk_type_id, token_number) composite
**Foreign keys**: customer_id -> customers.id, milk_type_id -> milk_types.id
**Relationships**: Has many TokenBookIssues

**Business rule**: A token identity uniquely identifies a customer's milk-type token. Each customer can have multiple token identities (one per milk type they subscribe to), each with a unique token number.

---

## Table: token_book_issues

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| token_identity_id | INTEGER | FK -> token_identities.id, NOT NULL | |
| issue_number | INTEGER | NOT NULL | Sequential book number |
| issue_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL | |
| completion_date | TIMESTAMPTZ | NULLABLE | Set when all sheets used |
| current_sheet | INTEGER | NOT NULL, DEFAULT 0 | Current sheet counter |
| status | VARCHAR(20) | NOT NULL, DEFAULT "WAITING" | WAITING/ACTIVE/COMPLETED |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: token_identity_id -> token_identities.id
**Relationships**: Belongs to TokenIdentity, has many TokenBookPayments

**Business rules**:
- Only one ACTIVE book per token identity at a time
- Duplicate issue_number not allowed per token identity
- Status transitions: WAITING -> ACTIVE -> COMPLETED

---

## Table: token_book_payments

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| token_book_issue_id | INTEGER | FK -> token_book_issues.id, NOT NULL | |
| payment_mode | VARCHAR(20) | NOT NULL | PREPAID/POSTPAID |
| payment_status | VARCHAR(20) | NOT NULL, DEFAULT "PENDING" | PAID/PARTIAL/PENDING |
| book_price | NUMERIC(10,2) | NOT NULL | Total book price |
| amount_paid | NUMERIC(10,2) | NOT NULL, DEFAULT 0 | Amount paid so far |
| balance_amount | NUMERIC(10,2) | NOT NULL, DEFAULT 0 | book_price - amount_paid |
| payment_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL | |
| collected_by | INTEGER | FK -> users.id, NULLABLE | User who collected payment |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: token_book_issue_id -> token_book_issues.id, collected_by -> users.id
**Relationships**: Belongs to TokenBookIssue, optionally references User (collector)

**Business rules**:
- amount_paid must not exceed book_price
- balance_amount = book_price - amount_paid (auto-calculated)
- payment_status auto-determined: balance<=0 -> PAID, amount>0 -> PARTIAL, else PENDING
- On update, balance and status are recalculated automatically

---

## Alembic Migration History

| # | Revision | Description |
|---|----------|-------------|
| 1 | cd5183b67dae | Initial schema (users, routes) |
| 2 | de893ed2ffb7 | Add customers table |
| 3 | 4085a4134c96 | Add milk_types and employees tables |
| 4 | b3c4d5e6f7a8 | Add employee fields (user_id, etc.) |
| 5 | 2a032b2352b4 | Add subscriptions table |
| 6 | 3f8a1b2c4d5e | Create delivery_exceptions table |
| 7 | 4e5f6a7b8c9d | Create token_books tables (3 tables) |
| 8 | 1154a3a25414 | Remove is_active in update customer |

### Useful Commands
```bash
alembic upgrade head          # Apply all pending migrations
alembic downgrade -1          # Rollback one migration
alembic history               # Show migration history
alembic revision --autogenerate -m "description"  # Create new migration
```

---

## Indexes

The following columns have explicit indexes (via `index=True`):
- customers.id
- routes.id
- milk_types.id
- employees.id
- subscriptions.id
- delivery_exceptions.id
- token_identities.id
- token_book_issues.id
- token_book_payments.id

Unique constraints (implicit indexes):
- users.username
- routes.route_code
- routes.route_name
- customers.customer_code
- customers.primary_phone
- milk_types.milk_name
- employees.employee_code
- employees.phone
- token_identities (customer_id, milk_type_id, token_number)
