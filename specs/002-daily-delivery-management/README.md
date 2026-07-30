# Daily Delivery Management - Feature Specification

---

## 1. Overview

The Daily Delivery Management feature manages the complete lifecycle of milk delivery operations, from generating daily delivery schedules to route reconciliation and closure. This is the core operational module of the Milk Distribution ERP.

**Status**: PLANNED (Sprint 3)

---

## 2. Business Context

The milk distribution business operates on a daily cycle:

1. **Morning (4:00 AM)**: ERP generates delivery lists
2. **Early Morning (4:30 AM)**: Milk dispatched to delivery partners
3. **Morning (5:00 AM - 9:00 AM)**: Delivery partners distribute milk
4. **Mid-Morning (9:30 AM)**: Checker registers tokens and reconciles
5. **Afternoon (4:00 PM)**: Evening shift begins
6. **Evening (8:00 PM)**: Evening shift ends
7. **Night (9:00 PM)**: Owner reviews reports

---

## 3. Core Components

### 3.1 Token Book Structure

**Important:** Physical token sheets have **sheet numbers only**. Issue numbers are **system-internal references**.

```
Physical Token Sheet (Customer View):
╔═══════════════════════════════════════════════════╗
║           RAJESH MILK DISTRIBUTION                ║
║                                                   ║
║     Token Sheet Number: 5                         ║
║                                                   ║
║     Milk Type: Full Cream (1000ml)                ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

**Customer sees:** Only sheet number (5)
**System tracks:** Sheet number + Issue number + Book ID + Status

### 3.2 Delivery Session

A **Delivery Session** represents one shift (MORNING or EVENING) for one route on one day.

```
Delivery Session
├── Route: Route 1 - Downtown
├── Date: 2026-01-15
├── Shift: MORNING
├── Delivery Partner: Suresh Babu
├── Status: PLANNED → STARTED → COMPLETED → CLOSED
├── Total Milk Loaded: 110 Liters
├── Total Token Registered: 95 Liters
├── Total Cash Sales: 8 Liters
├── Total Returned Milk: 7 Liters
└── Reconciliation Status: BALANCED
```

### 3.3 Daily Delivery Record

A **Daily Delivery Record** represents one customer's delivery for one session.

```
Daily Delivery Record
├── Customer: Mrs. Sharma
├── Milk Type: Full Cream (1000ml)
├── Planned Quantity: 1 Liter
├── Delivered Quantity: 1 Liter
├── Delivery Status: DELIVERED
├── Token Sheet: #3
├── Source: PLANNED
└── Shift: MORNING
```

---

## 4. Delivery Statuses

| Status | Description |
|--------|-------------|
| `DELIVERED` | Milk delivered, token received or pending |
| `PENDING_TOKEN` | Milk delivered, token not yet received |
| `CASH_SALE` | Milk sold for cash, no token |
| `NOT_DELIVERED` | Scheduled but not delivered |
| `CANCELLED` | Delivery cancelled (exception) |

---

## 5. Delivery Sources

| Source | Description |
|--------|-------------|
| `PLANNED` | Customer was on today's schedule |
| `UNPLANNED` | Customer was not on schedule but received milk |

---

## 6. Complete Workflow

### Phase 1: Planning (Automatic)

```
Input: Subscriptions + Exceptions + Date + Shift + Route
Output: List of Daily Delivery Records
```

**Logic:**
1. Query all active subscriptions for the route
2. Check for active delivery exceptions (VACATION, NO_MILK, HOLIDAY)
3. Skip customers with active exceptions
4. Create delivery records for remaining customers
5. Group by route and create delivery session

### Phase 2: Dispatch (Manual)

```
Input: Route + Delivery Partner + Total Milk Loaded
Output: Updated Delivery Session (STARTED)
```

**Logic:**
1. Owner/Checker loads milk into delivery containers
2. Records dispatch in ERP
3. Delivery partner receives milk + checklist
4. Session status changes to STARTED

### Phase 3: Delivery (Physical)

```
Input: Delivery checklist + Physical milk
Output: Collected tokens + Cash + Remaining milk
```

**Responsibilities:**
- Deliver milk to each customer
- Collect token sheets
- Collect cash payments
- Handle special requests
- Return remaining milk

### Phase 4: Registration (Manual)

```
Input: Collected tokens + Cash + Remaining milk
Output: Updated delivery records
```

**For each customer, Checker selects:**
1. **Token Sheet** - Enter sheet number
2. **Pending Token** - Mark as pending
3. **Cash Sale** - Record cash payment
4. **Not Delivered** - Mark as skipped
5. **Add Unplanned** - Add missing customer

### Phase 5: Reconciliation (Automatic)

```
Formula: Loaded = Token Registered + Cash Sales + Returned Milk
```

**Logic:**
1. Calculate total token milk from registered sheets
2. Add cash sales
3. Add returned milk
4. Compare with loaded milk
5. Display difference (if any)

### Phase 6: Route Closing (Manual)

```
Prerequisites: Balanced reconciliation + All customers processed
Output: Closed session + Reports generated
```

**Logic:**
1. Verify all customers processed
2. Verify reconciliation balanced
3. Close session
4. Generate reports
5. Update token ledger

---

## 7. Special Scenarios

### 7.1 Pending Token

Customer receives milk but doesn't provide token sheet.

**Handling:**
- Mark delivery as `PENDING_TOKEN`
- Token can be submitted in any future shift
- No impact on reconciliation (counts as delivered)

### 7.2 Cash Sale

Customer pays cash instead of using token.

**Handling:**
- Mark delivery as `CASH_SALE`
- Record cash amount
- Included in reconciliation as "Cash Sales"

### 7.3 Extra Milk

Customer requests additional milk.

**Handling:**
- Update `delivered_quantity` to actual amount
- Reconciliation uses actual delivered quantity
- Customer may need to provide extra token or pay cash

### 7.4 Unplanned Delivery

Customer not on schedule but receives milk.

**Handling:**
- Add customer manually during registration
- Mark as `UNPLANNED` source
- Include in reconciliation
- Original schedule preserved for audit

### 7.5 Edit Previous Session

Owner corrects mistakes from previous days.

**See**: [Edit Previous Session Specification](edit-previous-session.md)

### 7.6 Customer Changes Mind (Unplanned with Token)

Customer was marked as NOT_DELIVERED or had an exception, but changes their mind during delivery and provides a token sheet.

**Example:**
```
Morning: Mrs. Gupta marked as VACATION
During Delivery: Mrs. Gupta changes mind, wants milk
She provides Token Sheet #5
Partner delivers milk as UNPLANNED
```

**Handling:**
- Add as unplanned delivery
- Register token sheet
- Include in reconciliation
- Log reason for audit

**See**: [Token Sheet Edge Cases Specification](token-sheet-edge-cases.md)

### 7.7 Non-sequential Token Sheets

Customers don't always provide sheets in order. They might skip sheets or provide them out of order.

**Example:**
```
Day 1: Sheet #1 ✓
Day 2: Sheet #2 ✓
Day 3: Sheet #5 (skipped #3, #4) → WARNING
Day 4: Sheet #3 (out of order) → WARNING
```

**Handling:**
- Allow non-sequential sheets
- Show WARNING to Checker
- Checker acknowledges and proceeds
- Log warning for audit

**See**: [Token Sheet Edge Cases Specification](token-sheet-edge-cases.md)

### 7.8 New Book Before Old Finishes

New token book issued before old one is fully used. Customer starts using new book while old still has sheets.

**Example:**
```
Old Book #SM-001: 20/30 sheets used (10 remaining)
New Book #SM-002: Just issued
Customer provides sheet from NEW book
System warns: Old book still has 10 sheets!
```

**Handling:**
- Allow new book usage
- Show WARNING to Checker
- Checker acknowledges and proceeds
- Both books remain ACTIVE
- Log warning for audit

**See**: [Token Sheet Edge Cases Specification](token-sheet-edge-cases.md)

---

## 8. Edge Cases & Warning System

The system includes a comprehensive warning system for edge cases:

### Warning Types

| Warning Code | Description | Severity |
|--------------|-------------|----------|
| `NON_SEQUENTIAL_SHEET` | Sheet skips ahead in sequence | WARNING |
| `SHEET_OUT_OF_ORDER` | Sheet provided after higher numbers used | WARNING |
| `GAP_DETECTED` | Gap in sheet sequence | INFO |
| `SHEET_ALREADY_USED` | Duplicate registration attempt | ERROR |
| `NEW_BOOK_BEFORE_OLD_FINISHED` | New book used while old still active | WARNING |

### Warning Flow

1. Checker enters token sheet number
2. System validates sequence and book status
3. If warnings detected, display to Checker
4. Checker acknowledges warnings
5. Registration proceeds
6. Warnings logged in audit trail

**See**: [Token Sheet Edge Cases Specification](token-sheet-edge-cases.md)

---

## 9. Reconciliation Formula

```
Loaded Milk = Token Milk Registered + Cash Sales + Returned Milk
```

**Example:**
```
Loaded Milk          : 110 L
Token Registered     :  95 L
Cash Sales           :   8 L
Returned Milk        :   7 L
────────────────────────────
Total Accounted      : 110 L
Status               : BALANCED ✅
```

**If Unbalanced:**
```
Loaded Milk          : 110 L
Token Registered     :  94 L
Cash Sales           :   8 L
Returned Milk        :   7 L
────────────────────────────
Total Accounted      : 109 L
Difference           :   1 L
Status               : UNBALANCED ❌
```

---

## 10. Shift Independence

Morning and Evening shifts operate **completely independently**:

- Each shift has its own delivery session
- Each shift has its own dispatch record
- Each shift has its own reconciliation
- Each shift has its own route closing
- Morning delivery does NOT affect Evening delivery

---

## 11. Role Responsibilities

| Phase | Owner | Checker | Delivery Partner |
|-------|-------|---------|-----------------|
| Planning | Configure | Review | - |
| Dispatch | Load milk | Record | Receive |
| Delivery | - | - | Deliver, collect |
| Registration | - | Register tokens | - |
| Reconciliation | View | Perform | - |
| Route Closing | Approve/Reopen | Close | - |
| Edit Previous | Edit | - | - |

---

## 12. Database Tables

### `delivery_sessions`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Session ID |
| route_id | INTEGER FK | Delivery route |
| delivery_date | DATE | Delivery date |
| shift | VARCHAR(10) | MORNING or EVENING |
| delivery_partner_id | INTEGER FK | Assigned partner |
| status | VARCHAR(20) | PLANNED/STARTED/COMPLETED/CLOSED |
| total_milk_loaded | DECIMAL(10,2) | Liters dispatched |
| total_token_registered | DECIMAL(10,2) | Calculated |
| total_cash_sales | DECIMAL(10,2) | Entered by checker |
| total_returned_milk | DECIMAL(10,2) | Entered by checker |
| reconciliation_status | VARCHAR(20) | BALANCED/UNBALANCED |
| reopened_by | INTEGER FK | Owner who reopened |
| reopened_at | TIMESTAMP | When reopened |
| reopen_count | INTEGER | Number of times reopened |
| is_active | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | Record creation |
| updated_at | TIMESTAMP | Last update |

### `daily_deliveries`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Delivery ID |
| session_id | INTEGER FK | Parent session |
| customer_id | INTEGER FK | Customer |
| milk_type_id | INTEGER FK | Milk type |
| planned_quantity | INTEGER | What ERP planned |
| delivered_quantity | INTEGER | What was delivered |
| delivery_status | VARCHAR(20) | DELIVERED/NOT_DELIVERED/etc |
| delivery_source | VARCHAR(20) | PLANNED/UNPLANNED |
| token_sheet_number | INTEGER | Sheet number (if token) |
| token_book_issue_id | INTEGER FK | Token book issue |
| added_by | INTEGER FK | User who added (unplanned) |
| added_reason | VARCHAR(500) | Why unplanned |
| is_edited | BOOLEAN | Was this edited |
| last_edited_by | INTEGER FK | Who edited |
| last_edited_at | TIMESTAMP | When edited |
| shift | VARCHAR(10) | MORNING or EVENING |
| delivery_date | DATE | Delivery date |
| remarks | VARCHAR(500) | Notes |
| is_active | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | Record creation |
| updated_at | TIMESTAMP | Last update |

### `session_edits`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Edit ID |
| session_id | INTEGER FK | Session edited |
| delivery_id | INTEGER FK | Delivery record edited |
| edited_by | INTEGER FK | User who edited |
| edit_type | VARCHAR(30) | Type of edit |
| old_value | JSONB | Previous values |
| new_value | JSONB | New values |
| reason | TEXT | Why edited |
| created_at | TIMESTAMP | When edited |

---

## 13. API Endpoints

### Session Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/deliveries/sessions/` | Create session (generate list) |
| GET | `/deliveries/sessions/` | List sessions |
| GET | `/deliveries/sessions/{id}` | Session detail |
| POST | `/deliveries/sessions/{id}/start` | Start session |
| POST | `/deliveries/sessions/{id}/dispatch` | Record dispatch |
| POST | `/deliveries/sessions/{id}/close` | Close session |
| POST | `/deliveries/sessions/{id}/reopen` | Reopen session (Owner) |

### Delivery Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/deliveries/sessions/{id}/checklist` | Get delivery checklist |
| POST | `/deliveries/` | Record delivery |
| PUT | `/deliveries/{id}` | Update delivery |
| POST | `/deliveries/unplanned` | Add unplanned delivery |
| PUT | `/deliveries/{id}/edit` | Edit previous delivery |

### Reconciliation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/deliveries/sessions/{id}/reconciliation` | Get reconciliation |
| POST | `/deliveries/sessions/{id}/reconcile` | Perform reconciliation |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/deliveries/sessions/{id}/report` | Get session report |
| GET | `/deliveries/sessions/{id}/edit-history` | Get edit history |

---

## 14. Error Handling

### Custom Exceptions

```python
class SessionNotFoundError(Exception):
    """Delivery session not found"""
    pass

class SessionAlreadyClosedError(Exception):
    """Session is already closed"""
    pass

class SessionNotBalancedError(Exception):
    """Cannot close unbalanced session"""
    pass

class OwnerRequiredError(Exception):
    """Only Owner can perform this action"""
    pass

class TokenSheetReturnError(Exception):
    """Cannot return token sheet"""
    pass

class DeliveryAlreadyEditError(Exception):
    """Delivery has already been edited"""
    pass
```

---

## 15. Reports Generated

After route closure, the ERP generates:

1. **Delivery Report** - All deliveries for the session
2. **Route Summary** - High-level metrics
3. **Token Collection Report** - All tokens registered
4. **Pending Token Report** - Tokens not yet received
5. **Cash Sales Report** - Cash transactions
6. **Returned Milk Report** - Undelivered milk
7. **Daily Reconciliation Report** - Balance sheet
8. **Session Edit History** - All edits made (if any)

---

## 16. Implementation Order

### Phase 1: Database

1. Create `delivery_sessions` table
2. Create `daily_deliveries` table
3. Create `session_edits` table
4. Create Alembic migration

### Phase 2: Models

1. Create `delivery_session.py` model
2. Create `daily_delivery.py` model
3. Create `session_edit.py` model

### Phase 3: Exceptions

1. Create `delivery.py` exceptions
2. Create `delivery_edit.py` exceptions

### Phase 4: Schemas

1. Create `delivery_session.py` schemas
2. Create `daily_delivery.py` schemas
3. Create `delivery_edit.py` schemas

### Phase 5: Services

1. Create `delivery_service.py` - Session management
2. Create `delivery_registration.py` - Token registration
3. Create `delivery_reconciliation.py` - Reconciliation logic
4. Create `delivery_edit_service.py` - Edit previous sessions

### Phase 6: Routers

1. Create `deliveries.py` router
2. Create `delivery_edit_router.py` router

### Phase 7: Testing

1. Unit tests for all services
2. Integration tests for complete workflow
3. Test with seed data

---

## 17. Summary

The Daily Delivery Management feature provides:

1. **Automated delivery list generation** from subscriptions
2. **Flexible registration** (token, pending, cash, unplanned)
3. **Automatic reconciliation** with formula validation
4. **Route closing** with audit trail
5. **Edit previous sessions** for error correction
6. **Token sheet return** mechanism
7. **Edge case handling** (non-sequential sheets, new book usage)
8. **Warning system** for Checker notifications
9. **Complete reporting** for business analytics

This module is the heart of the milk distribution operation, connecting customer subscriptions to daily delivery activities and financial reconciliation.
