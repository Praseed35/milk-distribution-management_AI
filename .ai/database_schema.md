# Database Schema (Current Implementation)

> This reflects the ACTUAL database schema as implemented. See also `DATABASE.md` for the detailed reference.

---

## Implemented Tables (17)

> All 17 tables below are implemented. Migration history and indexes are in `DATABASE.md`.

### 1. users
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | VARCHAR(50) | NOT NULL |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |

### 2. routes
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| route_code | VARCHAR | UNIQUE, NOT NULL |
| route_name | VARCHAR | UNIQUE, NOT NULL |
| description | VARCHAR | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 3. customers
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| customer_code | VARCHAR(20) | UNIQUE, NOT NULL |
| customer_name | VARCHAR(100) | NOT NULL |
| primary_phone | VARCHAR(15) | UNIQUE, NOT NULL |
| alternate_phone | VARCHAR(15) | NULLABLE |
| address | VARCHAR(255) | NULLABLE |
| route_id | INTEGER | FK → routes.id, NOT NULL |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 4. milk_types
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| milk_name | VARCHAR(100) | UNIQUE, NOT NULL |
| volume_ml | INTEGER | NOT NULL |
| description | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 5. employees
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| employee_code | VARCHAR(20) | UNIQUE, NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| phone | VARCHAR(20) | UNIQUE, NOT NULL |
| address | VARCHAR(255) | NULLABLE |
| role | VARCHAR(50) | NOT NULL |
| route_id | INTEGER | FK → routes.id, NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| user_id | INTEGER | FK → users.id, NULLABLE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 6. subscriptions
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| customer_id | INTEGER | FK → customers.id, NOT NULL |
| milk_type_id | INTEGER | FK → milk_types.id, NOT NULL |
| morning_quantity | INTEGER | NOT NULL, DEFAULT 0 |
| evening_quantity | INTEGER | NOT NULL, DEFAULT 0 |
| status | VARCHAR(20) | NOT NULL, DEFAULT "ACTIVE" |
| start_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL |
| end_date | TIMESTAMPTZ | NULLABLE |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 7. delivery_exceptions
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| subscription_id | INTEGER | FK → subscriptions.id, NOT NULL |
| exception_type | VARCHAR(20) | NOT NULL |
| start_date | TIMESTAMPTZ | NOT NULL |
| end_date | TIMESTAMPTZ | NULLABLE |
| reason | VARCHAR(255) | NULLABLE |
| status | VARCHAR(20) | NOT NULL, DEFAULT "ACTIVE" |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 8. token_identities
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| customer_id | INTEGER | FK → customers.id, NOT NULL |
| milk_type_id | INTEGER | FK → milk_types.id, NOT NULL |
| token_number | INTEGER | NOT NULL |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

Unique constraint: (customer_id, milk_type_id, token_number)

### 9. token_book_issues
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| token_identity_id | INTEGER | FK → token_identities.id, NOT NULL |
| issue_number | INTEGER | NOT NULL |
| issue_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL |
| completion_date | TIMESTAMPTZ | NULLABLE |
| current_sheet | INTEGER | NOT NULL, DEFAULT 0 |
| status | VARCHAR(20) | NOT NULL, DEFAULT "WAITING" |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 10. token_book_payments
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| token_book_issue_id | INTEGER | FK → token_book_issues.id, NOT NULL |
| payment_mode | VARCHAR(20) | NOT NULL |
| payment_status | VARCHAR(20) | NOT NULL, DEFAULT "PENDING" |
| book_price | NUMERIC(10,2) | NOT NULL |
| amount_paid | NUMERIC(10,2) | NOT NULL, DEFAULT 0 |
| balance_amount | NUMERIC(10,2) | NOT NULL, DEFAULT 0 |
| payment_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL |
| collected_by | INTEGER | FK → users.id, NULLABLE |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

### 11. delivery_sessions
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| route_id | INTEGER | FK → routes.id, NOT NULL |
| delivery_date | DATE | NOT NULL |
| shift | VARCHAR(10) | NOT NULL (MORNING/EVENING) |
| delivery_partner_id | INTEGER | FK → employees.id, NOT NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT "PLANNED" (PLANNED/STARTED/COMPLETED/CLOSED) |
| total_milk_loaded | NUMERIC(10,2) | DEFAULT 0 |
| total_token_registered | NUMERIC(10,2) | DEFAULT 0 (auto-calculated) |
| total_cash_sales | NUMERIC(10,2) | DEFAULT 0 |
| total_returned_milk | NUMERIC(10,2) | DEFAULT 0 |
| reconciliation_status | VARCHAR(20) | DEFAULT "PENDING" (PENDING/BALANCED/UNBALANCED) |
| reopened_by | INTEGER | FK → users.id, NULLABLE |
| reopened_at | TIMESTAMPTZ | NULLABLE |
| reopen_count | INTEGER | DEFAULT 0 |
| version | INTEGER | NOT NULL, DEFAULT 1 (optimistic locking) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

Unique constraint: (route_id, delivery_date, shift). State machine: PLANNED -> STARTED -> COMPLETED -> CLOSED <-> COMPLETED (reopen).

### 12. daily_deliveries
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| session_id | INTEGER | FK → delivery_sessions.id, NOT NULL |
| customer_id | INTEGER | FK → customers.id, NOT NULL |
| milk_type_id | INTEGER | FK → milk_types.id, NOT NULL |
| planned_quantity | INTEGER | NOT NULL (from subscription) |
| delivered_quantity | INTEGER | DEFAULT 0 |
| delivery_status | VARCHAR(20) | NOT NULL (DELIVERED/PENDING_TOKEN/CASH_SALE/NOT_DELIVERED/CANCELLED) |
| delivery_source | VARCHAR(20) | NOT NULL, DEFAULT "PLANNED" (PLANNED/UNPLANNED) |
| token_sheet_number | INTEGER | NULLABLE |
| token_book_issue_id | INTEGER | FK → token_book_issues.id, NULLABLE |
| added_by | INTEGER | FK → users.id, NULLABLE |
| added_reason | VARCHAR(500) | NULLABLE |
| cash_amount | NUMERIC(10,2) | NULLABLE |
| is_edited | BOOLEAN | DEFAULT FALSE |
| last_edited_by | INTEGER | FK → users.id, NULLABLE |
| last_edited_at | TIMESTAMPTZ | NULLABLE |
| shift | VARCHAR(10) | NOT NULL (denormalized from session) |
| delivery_date | DATE | NOT NULL (denormalized from session) |
| remarks | VARCHAR(500) | NULLABLE |
| version | INTEGER | NOT NULL, DEFAULT 1 (optimistic locking) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

Rules: DELIVERED requires token_sheet_number; CASH_SALE requires cash_amount; concurrent writes raise ConcurrentEditError.

### 13. session_edits (immutable audit log)
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| session_id | INTEGER | FK → delivery_sessions.id, NOT NULL |
| delivery_id | INTEGER | FK → daily_deliveries.id, NULLABLE (NULL for session-level edits/reopen) |
| edited_by | INTEGER | FK → users.id, NOT NULL |
| edit_type | VARCHAR(30) | NOT NULL (SESSION_REOPEN/STATUS_CHANGE) |
| old_value | JSONB | NOT NULL (snapshot before) |
| new_value | JSONB | NOT NULL (snapshot after) |
| reason | TEXT | NOT NULL |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |

No is_active / no updated_at — immutable audit trail, records never deleted.

### 14. token_sheet_warnings
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| delivery_id | INTEGER | FK → daily_deliveries.id, NOT NULL |
| warning_code | VARCHAR(30) | NOT NULL |
| warning_message | TEXT | NOT NULL |
| sheet_number | INTEGER | NOT NULL |
| expected_sheet | INTEGER | NULLABLE |
| book_issue_id | INTEGER | FK → token_book_issues.id, NULLABLE |
| metadata | JSONB | NULLABLE |
| acknowledged_by | INTEGER | FK → users.id, NULLABLE |
| acknowledged_at | TIMESTAMPTZ | NULLABLE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |

Warning codes: NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, GAP_DETECTED, SHEET_ALREADY_USED, NEW_BOOK_BEFORE_OLD_FINISHED.

### 15. customer_bills
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| customer_id | INTEGER | FK → customers.id, NOT NULL |
| bill_date | DATE | SERVER DEFAULT current_date, NOT NULL |
| bill_period_start | DATE | NOT NULL (INDEXED) |
| bill_period_end | DATE | NOT NULL |
| total_amount | NUMERIC(10,2) | NOT NULL |
| paid_amount | NUMERIC(10,2) | DEFAULT 0 |
| balance_amount | NUMERIC(10,2) | DEFAULT 0 |
| status | VARCHAR(20) | NOT NULL, DEFAULT "PENDING" (PENDING/PARTIAL/PAID/OVERDUE/CANCELLED) |
| due_date | DATE | NULLABLE |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

Generated from daily deliveries (DELIVERED/CASH_SALE) in a period × milk type unit_price. See BUSINESS_RULES §19.

### 16. customer_bill_items
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| bill_id | INTEGER | FK → customer_bills.id, NOT NULL |
| milk_type_id | INTEGER | FK → milk_types.id, NOT NULL |
| quantity | INTEGER | NOT NULL |
| unit_price | NUMERIC(10,2) | NOT NULL |
| amount | NUMERIC(10,2) | NOT NULL (quantity × unit_price) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |

Defined in the same file as CustomerBill (`app/models/customer_bill.py`); `milk_name` property exposes the milk type name.

### 17. customer_payments
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, INDEX |
| customer_id | INTEGER | FK → customers.id, NOT NULL |
| payment_date | TIMESTAMPTZ | SERVER DEFAULT now(), NOT NULL (INDEXED) |
| amount | NUMERIC(10,2) | NOT NULL |
| payment_mode | VARCHAR(20) | NOT NULL (CASH/UPI/CARD/CHEQUE/BANK_TRANSFER) |
| payment_type | VARCHAR(20) | NOT NULL (ADVANCE/BILL_PAYMENT) |
| reference_number | VARCHAR(50) | NULLABLE |
| bill_id | INTEGER | FK → customer_bills.id, NULLABLE (required for BILL_PAYMENT) |
| collected_by | INTEGER | FK → users.id, NULLABLE |
| remarks | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE |
| created_at | TIMESTAMPTZ | SERVER DEFAULT now() |
| updated_at | TIMESTAMPTZ | SERVER DEFAULT now(), onupdate |

Rules: BILL_PAYMENT requires bill_id; bill must not be PAID or CANCELLED; recording a payment updates the bill's paid/balance amounts and status. See BUSINESS_RULES §18.

---

## Planned Tables (Not Yet Implemented)

The tables below are the only ones still planned. Everything previously listed as "planned" has either been implemented under a different design or is no longer needed:

| Table | Sprint | Purpose | Status |
|-------|--------|---------|--------|
| token_register | Sprint 4 ext | Sheet-level token ledger | STILL PLANNED |
| token_ledger | Sprint 4 ext | Token transaction history | STILL PLANNED |

**Superseded designs (implemented differently)**:
- `delivery_sessions`, `delivery_items` → implemented as `delivery_sessions` + `daily_deliveries` (Sprint 5)
- `reconciliation_sessions`, `reconciliation_items` → folded into `delivery_sessions.reconciliation_status` + `daily_deliveries` (Sprint 5)
- `payment_ledger` → implemented as `customer_payments` (Sprint 6)
- `warning_logs` → implemented as `token_sheet_warnings` (Sprint 5)

---

## Design Principles (Actual)

1. **Integer primary keys** (not UUIDs as originally planned)
2. **Soft delete via is_active** boolean on every table
3. **Timestamps** (created_at, updated_at) on all tables except users
4. **Foreign key enforcement** at database level
5. **String statuses** (not enum columns) - business logic enforces valid values
6. **No created_by/updated_by** audit columns (not yet implemented)
