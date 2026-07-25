# Database Schema (Current Implementation)

> This reflects the ACTUAL database schema as implemented. See also `DATABASE.md` for the detailed reference.

---

## Implemented Tables (10)

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

---

## Planned Tables (Not Yet Implemented)

These are needed for future sprints:

| Table | Sprint | Purpose |
|-------|--------|---------|
| delivery_sessions | Sprint 3 | Daily delivery session per route/shift |
| delivery_items | Sprint 3 | Per-subscription delivery record |
| token_register | Sprint 4 ext | Sheet-level token tracking |
| token_ledger | Sprint 4 ext | Token transaction history |
| warning_logs | Sprint 4 ext | Alert/warning records |
| reconciliation_sessions | Sprint 5 | Daily reconciliation per route |
| reconciliation_items | Sprint 5 | Per-subscription reconciliation |
| payment_ledger | Sprint 6 | Customer payment tracking |

---

## Design Principles (Actual)

1. **Integer primary keys** (not UUIDs as originally planned)
2. **Soft delete via is_active** boolean on every table
3. **Timestamps** (created_at, updated_at) on all tables except users
4. **Foreign key enforcement** at database level
5. **String statuses** (not enum columns) - business logic enforces valid values
6. **No created_by/updated_by** audit columns (not yet implemented)
