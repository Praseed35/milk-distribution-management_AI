# DATABASE.md - Complete Database Schema

> All 17 tables with columns, constraints, relationships, and migration history.

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
User ──────────────────────────────────────────────────────┐
  │                                                        │
  ├──< Employee (user_id)                                 │
  ├──< TokenBookPayment (collected_by)                    │
  ├──< DeliverySession (reopened_by)                      │
  ├──< DailyDelivery (added_by, last_edited_by)           │
  └──< SessionEdit (edited_by)                            │
                                                           │
Route ─────────────────────────────────────────────────────┤
  │                                                        │
  ├──< Customer (route_id)                                 │
  │     │                                                  │
  │     ├──< Subscription (customer_id)                    │
  │     │     │                                            │
  │     │     ├──< DeliveryException (subscription_id)     │
  │     │     └──> MilkType (milk_type_id)                 │
  │     │                                                  │
  │     ├──< TokenIdentity (customer_id)                   │
  │     │     └──> MilkType (milk_type_id)                 │
  │     │                                                  │
  │     ├──< TokenBookIssue (customer_id)                  │
  │     │     └──> MilkType (milk_type_id)                 │
  │     │                                                  │
  │     └──< DailyDelivery (customer_id)                   │
  │           └──> MilkType (milk_type_id)                 │
  │                                                        │
  ├──< Employee (route_id)                                 │
  ├──< DeliverySession (route_id)                          │
  │     │                                                  │
  │     ├──< DailyDelivery (session_id)                    │
  │     │     │                                            │
  │     │     ├──< TokenSheetWarning (delivery_id)         │
  │     │     │     └──> TokenBookIssue (book_issue_id)    │
  │     │     └──< SessionEdit (delivery_id)               │
  │     │                                                  │
  │     └──< SessionEdit (session_id)                      │
  │                                                        │
  └──< DeliverySession (delivery_partner_id -> employees)  │
                                                           │
TokenIdentity ───< TokenBookIssue (token_identity_id)      │
                      │                                    │
                      ├──< TokenBookPayment                │
                      │     (token_book_issue_id)          │
                      │                                    │
                      ├──< DailyDelivery                   │
                      │     (token_book_issue_id)          │
                      │                                    │
                      └──< TokenSheetWarning               │
                            (book_issue_id)                │
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
| customer_id | INTEGER | FK -> customers.id, NOT NULL | Denormalized for query performance |
| milk_type_id | INTEGER | FK -> milk_types.id, NOT NULL | Denormalized for query performance |
| issue_number | INTEGER | NOT NULL | Sequential book number |
| book_number | VARCHAR(50) | NOT NULL | Human-readable book number |
| total_sheets | INTEGER | NOT NULL | Total sheets in this book |
| issue_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL | |
| completion_date | TIMESTAMPTZ | NULLABLE | Set when all sheets used |
| current_sheet | INTEGER | NOT NULL, DEFAULT 0 | Current sheet counter |
| status | VARCHAR(20) | NOT NULL, DEFAULT "WAITING" | WAITING/ACTIVE/COMPLETED |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: token_identity_id -> token_identities.id, customer_id -> customers.id, milk_type_id -> milk_types.id
**Relationships**: Belongs to TokenIdentity/Customer/MilkType; has many TokenBookPayments, DailyDeliveries, TokenSheetWarnings

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

---
 
## Table: delivery_sessions

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| route_id | INTEGER | FK -> routes.id, NOT NULL | |
| delivery_date | DATE | NOT NULL | |
| shift | VARCHAR(10) | NOT NULL | MORNING/EVENING |
| delivery_partner_id | INTEGER | FK -> employees.id, NOT NULL | |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'PLANNED' | PLANNED/STARTED/COMPLETED/CLOSED |
| total_milk_loaded | NUMERIC(10,2) | DEFAULT 0 | Liters loaded for dispatch |
| total_token_registered | NUMERIC(10,2) | DEFAULT 0 | Auto-calculated from deliveries |
| total_cash_sales | NUMERIC(10,2) | DEFAULT 0 | |
| total_returned_milk | NUMERIC(10,2) | DEFAULT 0 | |
| reconciliation_status | VARCHAR(20) | DEFAULT 'PENDING' | PENDING/BALANCED/UNBALANCED |
| reopened_by | INTEGER | FK -> users.id, NULLABLE | Owner who reopened |
| reopened_at | TIMESTAMPTZ | NULLABLE | |
| reopen_count | INTEGER | DEFAULT 0 | Number of times reopened |
| version | INTEGER | NOT NULL, DEFAULT 1 | Optimistic locking |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Unique constraints**: (route_id, delivery_date, shift) — only one session per route/date/shift
**Foreign keys**: route_id -> routes.id, delivery_partner_id -> employees.id, reopened_by -> users.id
**Relationships**: Has many DailyDeliveries, has many SessionEdits

**State machine**: PLANNED -> STARTED -> COMPLETED -> CLOSED <-> COMPLETED (reopen)
**Optimistic locking**: `version` column incremented on each write; concurrent writes checked

---

## Table: daily_deliveries

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| session_id | INTEGER | FK -> delivery_sessions.id, NOT NULL | |
| customer_id | INTEGER | FK -> customers.id, NOT NULL | |
| milk_type_id | INTEGER | FK -> milk_types.id, NOT NULL | |
| planned_quantity | INTEGER | NOT NULL | From subscription |
| delivered_quantity | INTEGER | DEFAULT 0 | Actual delivered |
| delivery_status | VARCHAR(20) | NOT NULL | DELIVERED/PENDING_TOKEN/CASH_SALE/NOT_DELIVERED/CANCELLED |
| delivery_source | VARCHAR(20) | NOT NULL, DEFAULT 'PLANNED' | PLANNED/UNPLANNED |
| token_sheet_number | INTEGER | NULLABLE | Token sheet # used |
| token_book_issue_id | INTEGER | FK -> token_book_issues.id, NULLABLE | |
| added_by | INTEGER | FK -> users.id, NULLABLE | Who added unplanned delivery |
| added_reason | VARCHAR(500) | NULLABLE | Reason for unplanned delivery |
| cash_amount | NUMERIC(10,2) | NULLABLE | Amount for cash sales |
| is_edited | BOOLEAN | DEFAULT FALSE | Edited from reopened session |
| last_edited_by | INTEGER | FK -> users.id, NULLABLE | |
| last_edited_at | TIMESTAMPTZ | NULLABLE | |
| shift | VARCHAR(10) | NOT NULL | Denormalized from session |
| delivery_date | DATE | NOT NULL | Denormalized from session |
| remarks | VARCHAR(500) | NULLABLE | |
| version | INTEGER | NOT NULL, DEFAULT 1 | Optimistic locking |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: session_id -> delivery_sessions.id, customer_id -> customers.id, milk_type_id -> milk_types.id, token_book_issue_id -> token_book_issues.id, added_by -> users.id, last_edited_by -> users.id
**Relationships**: Belongs to Session/Customer/MilkType/TokenBookIssue; has many SessionEdits, has many TokenSheetWarnings

**Business rules**:
- DELIVERED status requires a token_sheet_number
- CASH_SALE status requires cash_amount
- Optimistic locking via version column (ConcurrentEditError on mismatch)

---

## Table: session_edits (immutable audit log)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| session_id | INTEGER | FK -> delivery_sessions.id, NOT NULL | |
| delivery_id | INTEGER | FK -> daily_deliveries.id, NULLABLE | NULL for session-level edits (reopen) |
| edited_by | INTEGER | FK -> users.id, NOT NULL | |
| edit_type | VARCHAR(30) | NOT NULL | SESSION_REOPEN/STATUS_CHANGE |
| old_value | JSONB | NOT NULL | Snapshot before change |
| new_value | JSONB | NOT NULL | Snapshot after change |
| reason | TEXT | NOT NULL | Why the edit was made |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |

**Foreign keys**: session_id -> delivery_sessions.id, delivery_id -> daily_deliveries.id, edited_by -> users.id
**Note**: This table has NO is_active or updated_at — it's an immutable audit trail. Records are never deleted.

---

## Table: token_sheet_warnings

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| delivery_id | INTEGER | FK -> daily_deliveries.id, NOT NULL | |
| warning_code | VARCHAR(30) | NOT NULL | NON_SEQUENTIAL_SHEET/SHEET_OUT_OF_ORDER/GAP_DETECTED/SHEET_ALREADY_USED/NEW_BOOK_BEFORE_OLD_FINISHED |
| warning_message | TEXT | NOT NULL | Human-readable description |
| sheet_number | INTEGER | NOT NULL | The sheet that triggered the warning |
| expected_sheet | INTEGER | NULLABLE | What sheet was expected |
| book_issue_id | INTEGER | FK -> token_book_issues.id, NULLABLE | |
| metadata | JSONB | NULLABLE | Additional context |
| acknowledged_by | INTEGER | FK -> users.id, NULLABLE | Who acknowledged |
| acknowledged_at | TIMESTAMPTZ | NULLABLE | When acknowledged |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |

**Foreign keys**: delivery_id -> daily_deliveries.id, book_issue_id -> token_book_issues.id, acknowledged_by -> users.id
**Relationships**: Belongs to DailyDelivery/TokenBookIssue

**Warning codes**: NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, GAP_DETECTED, SHEET_ALREADY_USED, NEW_BOOK_BEFORE_OLD_FINISHED

---

## Table: customer_bills

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| customer_id | INTEGER | FK -> customers.id, NOT NULL | |
| bill_date | DATE | SERVER DEFAULT current_date, NOT NULL | |
| bill_period_start | DATE | NOT NULL | Start of billing period (INDEXED) |
| bill_period_end | DATE | NOT NULL | End of billing period |
| total_amount | NUMERIC(10,2) | NOT NULL | Sum of line items |
| paid_amount | NUMERIC(10,2) | DEFAULT 0 | Paid so far |
| balance_amount | NUMERIC(10,2) | DEFAULT 0 | total - paid |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'PENDING' | PENDING/PAID/CANCELLED |
| due_date | DATE | NULLABLE | |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: customer_id -> customers.id
**Relationships**: Belongs to Customer; has many CustomerBillItems, has many CustomerPayments

---

## Table: customer_bill_items

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| bill_id | INTEGER | FK -> customer_bills.id, NOT NULL | |
| milk_type_id | INTEGER | FK -> milk_types.id, NOT NULL | |
| quantity | INTEGER | NOT NULL | Total delivered qty |
| unit_price | NUMERIC(10,2) | NOT NULL | |
| amount | NUMERIC(10,2) | NOT NULL | quantity × unit_price |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |

**Foreign keys**: bill_id -> customer_bills.id, milk_type_id -> milk_types.id
**Relationships**: Belongs to CustomerBill and MilkType. `milk_name` property exposes `milk_type.milk_name`.
**Note**: Defined in the same file as CustomerBill (`app/models/customer_bill.py`).

---

## Table: customer_payments

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | PRIMARY KEY, INDEX | Auto-increment |
| customer_id | INTEGER | FK -> customers.id, NOT NULL | |
| payment_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL | (INDEXED for reports) |
| amount | NUMERIC(10,2) | NOT NULL | |
| payment_mode | VARCHAR(20) | NOT NULL | CASH/UPI/CARD/CHEQUE/BANK_TRANSFER |
| payment_type | VARCHAR(20) | NOT NULL | ADVANCE/BILL_PAYMENT |
| reference_number | VARCHAR(50) | NULLABLE | |
| bill_id | INTEGER | FK -> customer_bills.id, NULLABLE | Required for BILL_PAYMENT |
| collected_by | INTEGER | FK -> users.id, NULLABLE | User who collected |
| remarks | VARCHAR(255) | NULLABLE | |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() | |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate now() | |

**Foreign keys**: customer_id -> customers.id, bill_id -> customer_bills.id, collected_by -> users.id
**Relationships**: Belongs to Customer, optionally belongs to CustomerBill, optionally references User (collector)

**Business rules**:
- payment_type = BILL_PAYMENT requires a bill_id
- For BILL_PAYMENT, bill status must not already be PAID or CANCELLED
- Recording a payment updates the bill's paid_amount and balance_amount; if balance <= 0, bill status becomes PAID
- Bill cannot be cancelled if it has payments

---

## Alembic Migration History

| # | Revision | Description |
|---|----------|-------------|
| 1 | cd5183b67dae | Initial schema (users, routes) |
| 2 | de893ed2ffb7 | Add customers table |
| 3 | 4085a4134c96 | Add milk_types and employees tables |
| 4 | b3c4d5e6f7a8 | Add employee fields (employee_code, role, route_id, user_id, timestamps) |
| 5 | 2a032b2352b4 | Add subscriptions table |
| 6 | 3f8a1b2c4d5e | Create delivery_exceptions table |
| 7 | 4e5f6a7b8c9d | Create token_books tables (token_identities, token_book_issues, token_book_payments) |
| 8 | **5a6b7c8d9e0f** | **Create delivery tables (delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings)** |
| 9 | 1154a3a25414 | Remove is_active in update customer (EMPTY — no upgrade/downgrade logic) |
| 10 | aeecd8f99d6d | Merge token_books and delivery heads |
| 11 | 6a0f9777a5cb | Add payment management tables (customer_bills, customer_bill_items, customer_payments) |
| 12 | 119aa199d5d7 | Add report indexes (delivery_status, payment_date, bill_period_start) |

### Useful Commands
```bash
alembic upgrade head          # Apply all pending migrations
alembic downgrade -1          # Rollback one migration
alembic history               # Show migration history
alembic revision --autogenerate -m "description"  # Create new migration
```

---

## Indexes

All primary key columns have explicit indexes (via `index=True`):
- users.id, routes.id, customers.id, milk_types.id, employees.id
- subscriptions.id, delivery_exceptions.id
- token_identities.id, token_book_issues.id, token_book_payments.id
- delivery_sessions.id, daily_deliveries.id, session_edits.id, token_sheet_warnings.id
- customer_bills.id, customer_bill_items.id, customer_payments.id

Additional composite unique constraints (implicit indexes):
- users.username
- routes.route_code, routes.route_name
- customers.customer_code, customers.primary_phone
- milk_types.milk_name
- employees.employee_code, employees.phone
- token_identities (customer_id, milk_type_id, token_number)
- delivery_sessions (route_id, delivery_date, shift)

Report indexes added in migration `119aa199d5d7`:
- daily_deliveries.delivery_status (for reports filtering)
- customer_payments.payment_date
- customer_bills.bill_period_start
