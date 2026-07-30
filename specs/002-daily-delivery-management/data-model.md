# Data Model: Daily Delivery Management

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Overview

This document defines the database schema and entity relationships for the Daily Delivery Management feature.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DELIVERY DOMAIN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  delivery_sessions ──────┬───────────────────────────────────┐  │
│                          │                                   │  │
│                          ▼                                   │  │
│  daily_deliveries ───────┴─────── session_edits              │  │
│       │                                    │                  │  │
│       │                                    │                  │  │
│       ▼                                    ▼                  │  │
│  token_sheet_warnings              token_book_issues          │  │
│                                         │                     │  │
│                                         ▼                     │  │
│                                    token_identities           │  │
│                                         │                     │  │
│                                         ▼                     │  │
│                                    customers                  │  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tables

### 1. delivery_sessions

Represents one shift for one route on one day.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Session ID |
| route_id | INTEGER | FK → routes.id, NOT NULL | Delivery route |
| delivery_date | DATE | NOT NULL | Delivery date |
| shift | VARCHAR(10) | NOT NULL | MORNING or EVENING |
| delivery_partner_id | INTEGER | FK → employees.id, NOT NULL | Assigned partner |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'PLANNED' | Session status |
| total_milk_loaded | DECIMAL(10,2) | DEFAULT 0 | Liters dispatched |
| total_token_registered | DECIMAL(10,2) | DEFAULT 0 | Calculated from deliveries |
| total_cash_sales | DECIMAL(10,2) | DEFAULT 0 | Entered by checker |
| total_returned_milk | DECIMAL(10,2) | DEFAULT 0 | Entered by checker |
| reconciliation_status | VARCHAR(20) | DEFAULT 'PENDING' | BALANCED/UNBALANCED/PENDING |
| reopened_by | INTEGER | FK → users.id, NULLABLE | Owner who reopened |
| reopened_at | TIMESTAMP(timezone) | NULLABLE | When reopened |
| reopen_count | INTEGER | DEFAULT 0 | Number of times reopened |
| version | INTEGER | DEFAULT 1 | Optimistic locking version |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| created_at | TIMESTAMP(timezone) | DEFAULT NOW() | Record creation |
| updated_at | TIMESTAMP(timezone) | DEFAULT NOW() | Last update |

**Indexes**:
- `(route_id, delivery_date, shift)` - Unique constraint
- `(status)` - For filtering active sessions
- `(delivery_date)` - For date range queries

**Status Values**:
- PLANNED → STARTED → COMPLETED → CLOSED
- CLOSED → COMPLETED (reopen)

---

### 2. daily_deliveries

Individual customer delivery record.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Delivery ID |
| session_id | INTEGER | FK → delivery_sessions.id, NOT NULL | Parent session |
| customer_id | INTEGER | FK → customers.id, NOT NULL | Customer |
| milk_type_id | INTEGER | FK → milk_types.id, NOT NULL | Milk type |
| planned_quantity | INTEGER | NOT NULL | What ERP planned |
| delivered_quantity | INTEGER | DEFAULT 0 | What was delivered |
| delivery_status | VARCHAR(20) | NOT NULL | Delivery status |
| delivery_source | VARCHAR(20) | NOT NULL, DEFAULT 'PLANNED' | Source type |
| token_sheet_number | INTEGER | NULLABLE | Sheet number (if token) |
| token_book_issue_id | INTEGER | FK → token_book_issues.id, NULLABLE | Token book issue |
| added_by | INTEGER | FK → users.id, NULLABLE | User who added (unplanned) |
| added_reason | VARCHAR(500) | NULLABLE | Why unplanned |
| cash_amount | DECIMAL(10,2) | NULLABLE | Cash payment amount |
| is_edited | BOOLEAN | DEFAULT FALSE | Was this edited |
| last_edited_by | INTEGER | FK → users.id, NULLABLE | Who edited |
| last_edited_at | TIMESTAMP(timezone) | NULLABLE | When edited |
| shift | VARCHAR(10) | NOT NULL | MORNING or EVENING |
| delivery_date | DATE | NOT NULL | Delivery date |
| remarks | VARCHAR(500) | NULLABLE | Notes |
| version | INTEGER | DEFAULT 1 | Optimistic locking version |
| is_active | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| created_at | TIMESTAMP(timezone) | DEFAULT NOW() | Record creation |
| updated_at | TIMESTAMP(timezone) | DEFAULT NOW() | Last update |

**Indexes**:
- `(session_id)` - For session lookups
- `(customer_id, delivery_date)` - For customer history
- `(token_book_issue_id)` - For book tracking
- `(delivery_status)` - For filtering

**Status Values**:
- DELIVERED - Milk delivered, token received or pending
- PENDING_TOKEN - Milk delivered, token not yet received
- CASH_SALE - Milk sold for cash
- NOT_DELIVERED - Scheduled but not delivered
- CANCELLED - Delivery cancelled

**Source Values**:
- PLANNED - Customer was on schedule
- UNPLANNED - Customer was not on schedule

---

### 3. session_edits

Audit record for changes to previous sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Edit ID |
| session_id | INTEGER | FK → delivery_sessions.id, NOT NULL | Session edited |
| delivery_id | INTEGER | FK → daily_deliveries.id, NULLABLE | Delivery record edited |
| edited_by | INTEGER | FK → users.id, NOT NULL | User who edited |
| edit_type | VARCHAR(30) | NOT NULL | Type of edit |
| old_value | JSONB | NOT NULL | Previous values |
| new_value | JSONB | NOT NULL | New values |
| reason | TEXT | NOT NULL | Why edited |
| created_at | TIMESTAMP(timezone) | DEFAULT NOW() | When edited |

**Indexes**:
- `(session_id)` - For session history
- `(delivery_id)` - For delivery history
- `(edited_by)` - For user audit

**Edit Types**:
- STATUS_CHANGE - Delivery status changed
- TOKEN_RETURN - Token sheet returned
- QUANTITY_CHANGE - Delivered quantity changed
- SESSION_REOPEN - Session reopened
- SESSION_CLOSE - Session closed

---

### 4. token_sheet_warnings

Audit record for non-sequential sheets or new book usage warnings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Warning ID |
| delivery_id | INTEGER | FK → daily_deliveries.id, NOT NULL | Related delivery |
| warning_code | VARCHAR(30) | NOT NULL | Warning type |
| warning_message | TEXT | NOT NULL | Human-readable message |
| sheet_number | INTEGER | NOT NULL | Sheet being registered |
| expected_sheet | INTEGER | NULLABLE | What was expected |
| book_issue_id | INTEGER | FK → token_book_issues.id, NULLABLE | Related book |
| metadata | JSONB | NULLABLE | Additional details |
| acknowledged_by | INTEGER | FK → users.id, NULLABLE | Who acknowledged |
| acknowledged_at | TIMESTAMP(timezone) | NULLABLE | When acknowledged |
| created_at | TIMESTAMP(timezone) | DEFAULT NOW() | When created |

**Indexes**:
- `(delivery_id)` - For delivery warnings
- `(warning_code)` - For filtering by type

**Warning Codes**:
- NON_SEQUENTIAL_SHEET - Sheet skips ahead
- SHEET_OUT_OF_ORDER - Sheet provided after higher numbers
- GAP_DETECTED - Gap in sequence
- SHEET_ALREADY_USED - Duplicate registration
- NEW_BOOK_BEFORE_OLD_FINISHED - New book used early

---

## Relationships

### delivery_sessions → daily_deliveries
- One session has many deliveries
- Cascade: RESTRICT (prevent session delete with deliveries)

### daily_deliveries → session_edits
- One delivery can have many edits
- Cascade: RESTRICT

### daily_deliveries → token_sheet_warnings
- One delivery can have many warnings
- Cascade: RESTRICT

### daily_deliveries → token_book_issues
- One delivery links to one book issue (nullable)
- Cascade: SET NULL

---

## State Transitions

### Delivery Session States

```
PLANNED → STARTED → COMPLETED → CLOSED
                          ↑           │
                          └───────────┘ (reopen)
```

### Daily Delivery States

```
PLANNED → DELIVERED
    │         │
    │         ├── PENDING_TOKEN
    │         │
    │         └── CASH_SALE
    │
    └── NOT_DELIVERED / CANCELLED
```

---

## Validation Rules

### Delivery Session
- route_id must reference active route
- delivery_partner_id must reference active employee
- shift must be MORNING or EVENING
- status transitions must follow valid path
- cannot close unless reconciliation is balanced

### Daily Delivery
- customer_id must reference active customer
- milk_type_id must reference active milk type
- session_id must reference active session
- delivered_quantity must be >= 0
- token_sheet_number required if status is DELIVERED with token
- cash_amount required if status is CASH_SALE

### Token Registration
- customer must have active token book for milk type
- sheet number must be within book range
- sheet must not already be used
- book must be ACTIVE status

---

## Soft Delete Rules

All entities use `is_active` flag:
- DELETE endpoints set `is_active = False`
- List endpoints filter by `is_active = True`
- Foreign keys use `ON DELETE SET NULL` or `ON DELETE RESTRICT`

---

## Migration Strategy

1. Create new tables in order:
   - delivery_sessions
   - daily_deliveries
   - session_edits
   - token_sheet_warnings

2. Add foreign key constraints

3. Create indexes for performance

4. No data migration needed (new feature)

---

## Summary

The data model supports:
- Complete delivery lifecycle tracking
- Comprehensive audit trail
- Token sheet management with warnings
- Optimistic locking for concurrent edits
- Soft deletes for data integrity

All tables follow existing project patterns and constitution requirements.
