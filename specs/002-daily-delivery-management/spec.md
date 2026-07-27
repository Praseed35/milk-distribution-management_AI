# Feature Specification: Daily Delivery Management

**Feature Branch**: `002-daily-delivery-management`

**Created**: 2026-07-27

**Status**: Draft (Revised)

**Input**: User description: "Implement daily delivery management - the core operational feature where delivery partners execute daily milk deliveries to customers on their routes."

---

## 1. Feature Overview

Daily Delivery Management is the **core operational feature** of the milk distribution system. It enables the end-to-end lifecycle of a daily delivery run: from session creation, through delivery partner execution (read-only), to checker data entry and reconciliation.

### Revised Workflow

```
OWNER/CHECKER creates session (PLANNED)
    ↓
OWNER/CHECKER generates delivery items from subscriptions
    ↓
OWNER/CHECKER transitions to STARTED
    ↓
DELIVERY_PARTNER views route/customers/subscriptions (READ-ONLY)
    ↓
DELIVERY_PARTNER delivers milk, collects tokens
    ↓
DELIVERY_PARTNER returns tokens to CHECKER
    ↓
CHECKER records delivery status per customer (DELIVERED/SKIPPED)
CHECKER records token sheet consumption
CHECKER transitions to COMPLETED
    ↓
CHECKER performs reconciliation (verify totals)
CHECKER transitions to RECONCILED
    ↓
OWNER/CHECKER transitions to CLOSED (final lock)
```

### Key Design Decision

**Delivery Partner is READ-ONLY** - The partner's job is to deliver milk and collect tokens. They view customer info, subscriptions, and exceptions in the app. All data entry is done by the CHECKER.

This feature bridges the gap between the subscription/ordering layer and the physical delivery execution, consuming data from **Subscriptions**, **Customers**, **Routes**, **Token Books**, and **Delivery Exceptions** to produce a complete daily delivery record.

---

## 2. Business Problem

Currently, the system tracks subscriptions, customers, routes, and token books, but has **no mechanism to manage or record the daily delivery execution**. The current workflow relies on:

- Paper-based delivery tracking
- Manual token sheet counting
- Post-hoc data entry by the checker
- No structured reconciliation process

This creates a dependency on paper records, manual tracking, and post-hoc data entry, leading to errors, disputes, and lack of auditability.

### Current Paper-Based Flow
1. Owner assigns delivery partner to a route
2. Partner goes out with paper list
3. Partner delivers milk, collects tokens
4. Partner returns with collected tokens and paper list
5. Checker manually enters data into system (or keeps paper records)
6. No formal reconciliation process

### Desired Digital Flow
1. Owner/Checker creates delivery session and generates items from subscriptions
2. Partner views route customers, subscriptions, and exceptions in app (read-only)
3. Partner delivers milk, collects tokens
4. Partner returns with collected tokens
5. Checker records delivery status and token consumption in system
6. Checker reconciles totals against physical records
7. Owner closes session (final lock)

---

## 3. Objectives

| ID | Objective | Priority |
|----|-----------|----------|
| O-01 | Enable creation and management of daily delivery sessions per route/shift | P0 |
| O-02 | Auto-generate delivery items from active subscriptions + route customers | P0 |
| O-03 | Allow CHECKER to record delivery status and quantities per customer | P0 |
| O-04 | Track token book sheet consumption at delivery time | P1 |
| O-05 | Record cash sales for non-subscribed walk-in customers | P1 |
| O-06 | Generate daily summary totals for reconciliation | P1 |
| O-07 | Enable CHECKER role to review and verify daily delivery records | P1 |
| O-08 | Enforce business rules around delivery exceptions, token book availability, and session lifecycle | P1 |

---

## 4. Scope

### In Scope

- **Delivery Sessions**: Create, update, start, complete, reconcile, and close daily delivery sessions
- **Delivery Items**: Auto-populate from subscriptions; CHECKER records status/quantity updates
- **Token Sheet Tracking**: CHECKER records which sheet from a token book was consumed per delivery
- **Cash Sales**: CHECKER records direct milk sales (customer_name, phone, milk_type, quantity, amount) within a session
- **Daily Summary**: Aggregate totals per session (liters delivered, liters skipped, cash collected, tokens consumed)
- **Reconciliation**: CHECKER verifies totals match physical records before closing
- **Delivery Partner View**: Partner sees own route's customers, subscriptions, exceptions, and pending tokens (read-only)
- **Querying**: Filter sessions by date range, route, shift, status, delivery partner

### Out of Scope

- **Payment collection/billing logic** (token book payments already exist)
- **Route optimization or geolocation**
- **Mobile app / frontend UI** (API-only in this phase)
- **SMS/push notifications to customers** (future feature)
- **Inventory/dairy stock management**
- **GPS tracking of delivery partners**
- **Multi-day scheduling / recurring session auto-generation** (future feature)
- **Customer self-service or portal**

---

## 5. Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| Dairy Owner | OWNER role | Daily operations visibility, final verification, financial accuracy |
| Checker | CHECKER role | Recording delivery data, token tracking, reconciliation |
| Delivery Partner | DELIVERY_PARTNER role | View route customers, subscriptions, exceptions, pending tokens (read-only) |
| Customer | End consumer | Accurate delivery, correct token deduction |
| System Admin | Technical | System reliability, data integrity |

---

## 6. User Stories

### Epic: Daily Delivery Management

---

#### US-001: Create Delivery Session

**Priority**: P0

**As a** OWNER or CHECKER

**I want** to create a delivery session for a specific date, route, and shift

**So that** a structured delivery run can be planned and tracked

**Description**: The OWNER or CHECKER initiates a delivery session by specifying the delivery date, route, and shift (MORNING/EVENING). The system creates a session in PLANNED status. If a session already exists for the same route + date + shift combination, the system rejects the duplicate.

**Acceptance Scenarios**:

1. **Given** an OWNER is authenticated, **When** they provide a valid date, route_id, and shift, **Then** a delivery session is created with status PLANNED and the response includes session details
2. **Given** a delivery session already exists for route R1 on 2026-07-27 MORNING, **When** another create request is made for R1 / 2026-07-27 / MORNING, **Then** the system returns HTTP 400 with "Session already exists" error
3. **Given** the provided route_id does not exist or is inactive, **When** a session is created, **Then** the system returns HTTP 404 with "Route not found" error
4. **Given** an invalid shift value is provided, **When** the request is submitted, **Then** the system returns HTTP 422 validation error
5. **Given** a CHECKER is authenticated, **When** they create a session, **Then** the system allows it (CHECKER has create permission on sessions)

---

#### US-002: Auto-Generate Delivery Items for a Session

**Priority**: P0

**As a** OWNER or CHECKER

**I want** the system to automatically generate delivery items for all active subscriptions on the session's route and shift

**So that** the delivery partner has a complete work list without manual data entry

**Description**: When a session is created (or on-demand via API call), the system queries all active customers on the session's route who have active subscriptions with a non-zero quantity for the session's shift. For each such subscription, a delivery item is generated with status PENDING and the expected quantity from the subscription. Customers with active delivery exceptions for the delivery date are automatically marked as SKIPPED with the exception type noted.

**Acceptance Scenarios**:

1. **Given** a session for Route R1 MORNING on 2026-07-27, **When** there are 10 active customers on R1 with morning subscriptions, **Then** 10 delivery items are created with status PENDING and quantities matching subscriptions
2. **Given** a customer on R1 has an active VACATION exception covering 2026-07-27, **When** delivery items are generated for the MORNING session, **Then** that customer's item is created with status SKIPPED and reason "VACATION"
3. **Given** a customer on R1 has a subscription with morning_quantity = 0, **When** delivery items are generated for the MORNING session, **Then** that customer is NOT included in the delivery items
4. **Given** a session has existing delivery items, **When** generate is called again, **Then** the system returns HTTP 400 "Items already generated" (idempotent guard)
5. **Given** a customer is inactive (is_active=False), **When** delivery items are generated, **Then** that customer is excluded

---

#### US-003: Record Delivery Status (Checker)

**Priority**: P0

**As a** CHECKER

**I want** to mark each customer's delivery as delivered, skipped, or cancelled based on token collection and partner feedback

**So that** the daily delivery record accurately reflects what was actually delivered

**Description**: After the delivery partner returns, the CHECKER records the delivery status for each customer. The partner provides: (1) collected tokens (proof of delivery), (2) verbal feedback on customers who got milk but didn't give tokens. The checker then updates each delivery item accordingly.

**Acceptance Scenarios**:

1. **Given** a customer who gave a token, **When** CHECKER records DELIVERED with token sheet number, **Then** the item status updates to DELIVERED with token consumption recorded
2. **Given** a customer who got milk but gave no token, **When** CHECKER records DELIVERED with partner's verbal confirmation, **Then** the item status updates to DELIVERED (no token)
3. **Given** a customer who was absent, **When** CHECKER records SKIPPED with reason "Customer not home", **Then** the item status updates to SKIPPED
4. **Given** a customer with a delivery exception (vacation), **When** items were auto-generated as SKIPPED, **Then** CHECKER sees them as already skipped
5. **Given** a session is in COMPLETED or CLOSED status, **When** any delivery item update is attempted, **Then** the system returns HTTP 400 "Session is not active"
6. **Given** a delivery item with status PENDING, **When** CHECKER records actual_quantity_delivered, **Then** the item is updated with the actual quantity

---

#### US-004: Record Token Book Sheet Consumption (Checker)

**Priority**: P1

**As a** CHECKER

**I want** to record the token book sheet number consumed when a customer collects milk

**So that** token book tracking stays synchronized with physical deliveries

**Description**: When recording a DELIVERED item, the CHECKER also records the token consumption details. The delivery partner brings back physical token sheets collected from customers. The checker enters the token_book_issue_id and sheet_number for each delivered customer who used a token book. Customers may use non-sequential sheets or have multiple active token books.

**Acceptance Scenarios**:

1. **Given** a DELIVERED item, **When** CHECKER provides token_book_issue_id and sheet_number, **Then** the token consumption is recorded and linked to the delivery item
2. **Given** a non-DELIVERED item (SKIPPED/CANCELLED), **When** token consumption data is provided, **Then** the system returns HTTP 400 "Token can only be recorded for delivered items"
3. **Given** a token_book_issue_id that is not in ACTIVE status, **When** recording consumption, **Then** the system returns HTTP 400 "Token book is not active"
4. **Given** a token_book_issue_id whose sheet_number exceeds total_sheets, **When** recording consumption, **Then** the system returns HTTP 400 "Sheet number exceeds book capacity"
5. **Given** a delivery item that already has a token consumption record, **When** another is provided, **Then** the system updates the existing record (overwrite)
6. **Given** a customer has multiple active token books, **When** CHECKER records consumption, **Then** CHECKER selects which book and sheet number to record
7. **Given** a customer uses non-sequential sheets (e.g., sheet 5 then sheet 12), **When** recorded, **Then** the system allows it (sheets can be used in any order)
8. **Given** a customer's current book is exhausted, **When** CHECKER needs to record a new delivery, **Then** CHECKER can issue a new book (via token-books API) and record against the new book
9. **Given** a customer with no token book, **When** CHECKER records delivery, **Then** token fields remain null (cash customer scenario)

---

#### US-005: Record Cash Sales (Checker)

**Priority**: P1

**As a** CHECKER

**I want** to record direct milk sales to non-subscribed walk-in customers during a delivery route

**So that** ad-hoc sales are tracked and reconciled alongside subscription deliveries

**Description**: Within an active session, the CHECKER can record cash sales for customers who do not have a subscription. The delivery partner may report walk-in sales during the route. Each cash sale captures customer_name, phone (optional), milk_type, quantity in ml, amount collected, and payment_mode (CASH or UPI).

**Acceptance Scenarios**:

1. **Given** an active session, **When** CHECKER records a cash sale with customer_name, milk_type_id, quantity_ml, and amount, **Then** a cash sale record is created linked to the session
2. **Given** a session in COMPLETED status, **When** a cash sale is attempted, **Then** the system returns HTTP 400 "Session is not active"
3. **Given** a cash sale with quantity_ml = 0, **When** submitted, **Then** the system returns HTTP 422 validation error
4. **Given** a cash sale with amount < 0, **When** submitted, **Then** the system returns HTTP 422 validation error
5. **Given** an inactive milk_type_id, **When** a cash sale is recorded, **Then** the system returns HTTP 404 "Milk type not found"

---

#### US-006: Session Lifecycle Management

**Priority**: P0

**As a** OWNER or CHECKER

**I want** delivery sessions to follow a strict lifecycle (PLANNED → STARTED → COMPLETED → RECONCILED → CLOSED)

**So that** delivery data integrity is maintained and reconciliation is enforced before finalization

**Description**: Sessions follow a linear 5-step state machine:
- **PLANNED**: Session created, items generated, ready to start
- **STARTED**: Delivery partner is out delivering, checker can record items
- **COMPLETED**: All delivery items recorded, ready for reconciliation
- **RECONCILED**: Checker has verified totals match physical records
- **CLOSED**: Fully locked, no modifications allowed

**Acceptance Scenarios**:

1. **Given** a session in PLANNED status, **When** OWNER transitions it to STARTED, **Then** the session status updates and checker can begin recording deliveries
2. **Given** a session in STARTED status, **When** CHECKER transitions it to COMPLETED, **Then** all delivery items are finalized
3. **Given** a session in COMPLETED status, **When** CHECKER performs reconciliation and transitions to RECONCILED, **Then** the session is marked as reconciled
4. **Given** a session in RECONCILED status, **When** OWNER transitions it to CLOSED, **Then** the session is fully locked with verified_by recorded
5. **Given** a session in PLANNED status, **When** a transition to COMPLETED is attempted (skipping STARTED), **Then** the system returns HTTP 400 "Invalid status transition"
6. **Given** a session in CLOSED status, **When** any modification is attempted, **Then** the system returns HTTP 400 "Session is closed and cannot be modified"
7. **Given** a session in STARTED status, **When** transition to PLANNED is attempted (reverse), **Then** the system returns HTTP 400 "Cannot reverse session status"

---

#### US-007: Daily Summary / Reconciliation (Checker)

**Priority**: P1

**As a** CHECKER

**I want** to view a summary of a completed delivery session showing total liters delivered, skipped, cash sales collected, and tokens consumed

**So that** I can reconcile daily operations and verify totals match physical records

**Description**: The system computes a summary for a session aggregating all delivery items and cash sales. The summary includes: total items, delivered count, skipped count, cancelled count, total liters delivered (by milk type), total cash sales amount, total tokens consumed (across all books), and a breakdown by milk type. The CHECKER uses this to verify against physical token sheets and cash collected before transitioning to RECONCILED status.

**Acceptance Scenarios**:

1. **Given** a session with 10 delivered items (total 20L), 2 skipped, 3 cash sales (5L, Rs.250), **When** CHECKER views the summary, **Then** the response shows totals matching these figures
2. **Given** a session in PLANNED status, **When** the summary is requested, **Then** the system returns the summary with all zeros (pre-execution view)
3. **Given** a non-existent session_id, **When** summary is requested, **Then** the system returns HTTP 404 "Session not found"
4. **Given** a session in COMPLETED status, **When** CHECKER confirms totals match physical records, **Then** CHECKER can transition to RECONCILED

---

#### US-008: Reconciliation and Close (Checker/Owner)

**Priority**: P1

**As a** CHECKER

**I want** to reconcile a completed delivery session and mark it as reconciled, then have OWNER close it

**So that** there is an accountability layer ensuring delivery records are accurate before finalization

**Description**: After recording all deliveries, the CHECKER reviews the session summary and verifies totals match physical records (token sheets collected, cash collected). The CHECKER can add reconciliation remarks and transition the session to RECONCILED. Finally, the OWNER closes the session, which fully locks all records.

**Acceptance Scenarios**:

1. **Given** a session in COMPLETED status, **When** CHECKER confirms totals and transitions to RECONCILED with remarks, **Then** the session status updates to RECONCILED
2. **Given** a session in RECONCILED status, **When** OWNER transitions to CLOSED, **Then** the session is fully locked with verified_by recorded
3. **Given** a session in PLANNED or STARTED status, **When** a CHECKER attempts to reconcile, **Then** the system returns HTTP 400 "Only completed sessions can be reconciled"
4. **Given** a session in COMPLETED status, **When** a DELIVERY_PARTNER attempts to reconcile, **Then** the system returns HTTP 403 "Access denied"
5. **Given** a session already in CLOSED status, **When** any modification is attempted, **Then** the system returns HTTP 400 "Session is closed and cannot be modified"

---

#### US-009: Query and Filter Delivery Sessions

**Priority**: P1

**As a** OWNER, CHECKER, or DELIVERY_PARTNER

**I want** to query delivery sessions by date range, route, shift, status, and delivery partner

**So that** I can quickly find and review specific delivery runs

**Description**: The system provides list endpoints with filtering capabilities. DELIVERY_PARTNER role can only see sessions for their assigned route (read-only). OWNER and CHECKER can see all sessions.

**Acceptance Scenarios**:

1. **Given** multiple sessions exist, **When** OWNER queries with date_from=2026-07-01 and date_to=2026-07-31, **Then** all sessions within July 2026 are returned
2. **Given** a DELIVERY_PARTNER is authenticated, **When** they query sessions, **Then** only sessions for their assigned route are returned
3. **Given** filter params route_id=1 and shift=MORNING, **When** queried, **Then** only MORNING sessions for route 1 are returned
4. **Given** a DELIVERY_PARTNER, **When** they query sessions, **Then** they see only session details (no edit permissions)

---

#### US-011: Delivery Partner View (Read-Only)

**Priority**: P0

**As a** DELIVERY_PARTNER

**I want** to view my assigned route's customers, their subscriptions, delivery exceptions, and pending token books

**So that** I know which customers need delivery today and their requirements

**Description**: The delivery partner has read-only access to view information needed for their daily route. This includes customer details, their active subscriptions (milk type and quantities), any delivery exceptions (vacation, holiday), and pending token books. No write access is provided.

**Acceptance Scenarios**:

1. **Given** a DELIVERY_PARTNER is authenticated, **When** they view their route's customers, **Then** they see all active customers on their assigned route
2. **Given** a customer has active subscriptions, **When** the partner views the customer, **Then** they see subscription details (milk type, morning/evening quantities)
3. **Given** a customer has a delivery exception for today, **When** the partner views the customer, **Then** they see the exception details (type, reason)
4. **Given** a customer has pending token books, **When** the partner views the customer, **Then** they see token book status and remaining sheets
5. **Given** a DELIVERY_PARTNER tries to update any data, **When** they attempt a write operation, **Then** the system returns HTTP 403 "Access denied"

---

#### US-010: View Session Details with Delivery Items

**Priority**: P0

**As a** OWNER, CHECKER, or DELIVERY_PARTNER

**I want** to view the full details of a delivery session including all its delivery items and cash sales

**So that** I can inspect individual delivery records within a session

**Acceptance Scenarios**:

1. **Given** a session with 10 delivery items and 2 cash sales, **When** the detail endpoint is called, **Then** the response includes the session metadata, a list of all delivery items with customer info and status, and a list of cash sales
2. **Given** a non-existent session_id, **When** the detail is requested, **Then** the system returns HTTP 404 "Session not found"

---

## 7. Functional Requirements

### 7.1 Delivery Session Management

| ID | Requirement |
|----|-------------|
| FR-001 | System MUST create delivery sessions with date, route_id, shift, and status=PLANNED |
| FR-002 | System MUST enforce unique constraint on (route_id, delivery_date, shift) for active sessions |
| FR-003 | System MUST follow session lifecycle: PLANNED → STARTED → COMPLETED → RECONCILED → CLOSED |
| FR-004 | System MUST NOT allow reverse status transitions |
| FR-005 | System MUST record assigned_delivery_partner_id (employee_id) on the session |
| FR-006 | System MUST record created_by (user_id), reconciled_by (user_id), and verified_by (user_id) on the session |
| FR-007 | System MUST soft-delete sessions using is_active pattern |

### 7.2 Delivery Item Management

| ID | Requirement |
|----|-------------|
| FR-010 | System MUST auto-generate delivery items from active subscriptions for the session's route and shift |
| FR-011 | System MUST exclude customers with is_active=False |
| FR-012 | System MUST exclude subscriptions where the shift quantity is 0 |
| FR-013 | System MUST auto-mark items as SKIPPED when a delivery exception covers the delivery date |
| FR-014 | System MUST record expected_quantity (from subscription) and actual_quantity_delivered (from partner) |
| FR-015 | System MUST track delivery status: PENDING -> DELIVERED / SKIPPED / CANCELLED |
| FR-016 | System MUST allow DELIVERED items to only be modified by CHECKER/OWNER (not delivery partner) |
| FR-017 | System MUST record skip_reason for SKIPPED items |

### 7.3 Token Sheet Tracking

| ID | Requirement |
|----|-------------|
| FR-020 | System MUST allow token consumption recording only for DELIVERED items |
| FR-021 | System MUST link token consumption to a valid ACTIVE token_book_issue |
| FR-022 | System MUST validate that the token book has remaining sheets |
| FR-023 | System MUST record token_book_issue_id and sheet_number on the delivery item |
| FR-024 | System MUST update token_book_issue current_sheet to highest consumed sheet after recording |
| FR-025 | System MUST allow non-sequential sheet usage within a book |
| FR-026 | System MUST allow multiple active token books per customer per milk type |
| FR-027 | System MUST allow CHECKER to select which book to record against |

### 7.4 Cash Sales

| ID | Requirement |
|----|-------------|
| FR-030 | System MUST record cash sales linked to a delivery session |
| FR-031 | System MUST capture customer_name, phone (optional), milk_type_id, quantity_ml, amount, payment_mode |
| FR-032 | System MUST validate milk_type_id is active |
| FR-033 | System MUST only allow cash sales on active sessions (PLANNED or STARTED status) |

### 7.5 Daily Summary

| ID | Requirement |
|----|-------------|
| FR-040 | System MUST compute summary totals on-demand for any session |
| FR-041 | Summary MUST include: total items, delivered count, skipped count, cancelled count |
| FR-042 | Summary MUST include total liters delivered grouped by milk_type |
| FR-043 | Summary MUST include total cash sale amount and count |
| FR-044 | Summary MUST include total token sheets consumed |
| FR-045 | Summary MUST be used by CHECKER for reconciliation before transitioning to RECONCILED |

### 7.6 Checker Verification

| ID | Requirement |
|----|-------------|
| FR-050 | Only CHECKER roles MAY reconcile a session |
| FR-051 | Only OWNER roles MAY close a session |
| FR-052 | System MUST record reconciled_by (user_id) when transitioning to RECONCILED |
| FR-053 | System MUST record verified_by (user_id) when transitioning to CLOSED |
| FR-054 | System MUST accept optional reconciliation_remarks on reconcile |
| FR-055 | Only sessions in COMPLETED status MAY be reconciled |
| FR-056 | Only sessions in RECONCILED status MAY be closed |

### 7.7 Role-Based Access

| ID | Requirement |
|----|-------------|
| FR-060 | OWNER: Full CRUD on sessions, items, cash sales. Status transitions (START, CLOSE). Summary. |
| FR-061 | CHECKER: Create sessions. Record delivery status. Record token consumption. Record cash sales. Reconcile sessions. Read all sessions. |
| FR-062 | DELIVERY_PARTNER: Read-only access to sessions on assigned route. View customers, subscriptions, exceptions, pending tokens. No write access. |
| FR-063 | DELIVERY_PARTNER view endpoints: GET /delivery-partner/route-customers, GET /delivery-partrier/route-sessions |

---

## 8. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-001 | All new endpoints MUST follow the existing layered architecture: Router -> Service -> ORM |
| NFR-002 | All new models MUST follow the soft-delete pattern (is_active) |
| NFR-003 | All new schemas MUST use Pydantic v2 with ConfigDict(from_attributes=True) |
| NFR-004 | All service functions MUST be module-level functions accepting db: Session |
| NFR-005 | All business errors MUST use custom exception classes inheriting from BusinessException |
| NFR-006 | Alembic migration MUST be provided for all new tables |
| NFR-007 | All datetime fields MUST use timezone-aware datetime |
| NFR-008 | Database indexes MUST be placed on frequently queried columns (date, route_id, shift, status) |
| NFR-009 | Delivery item generation MUST complete within 2 seconds for routes with up to 500 customers |
| NFR-010 | All new constants MUST use Python enums in app/constants/ |

---

## 9. Business Rules

### Session Lifecycle Rules

| Rule ID | Rule |
|---------|------|
| BR-001 | A delivery session is uniquely identified by (route_id, delivery_date, shift) |
| BR-002 | Session status transitions are strictly linear: PLANNED → STARTED → COMPLETED → RECONCILED → CLOSED |
| BR-003 | Reverse transitions are NOT allowed |
| BR-004 | PLANNED sessions allow item generation and editing |
| BR-005 | STARTED sessions allow CHECKER to record delivery status and tokens |
| BR-006 | COMPLETED sessions allow CHECKER to reconcile |
| BR-007 | RECONCILED sessions allow OWNER to close |
| BR-008 | CLOSED sessions are fully locked |

### Delivery Item Rules

| Rule ID | Rule |
|---------|------|
| BR-010 | Items are auto-generated from subscriptions where (customer.route_id = session.route) AND (subscription shift quantity > 0) AND (subscription.status = ACTIVE) AND (customer.is_active = True) |
| BR-011 | Customers with active delivery exceptions covering the session date are auto-marked SKIPPED |
| BR-012 | Only CHECKER and OWNER can update delivery item status (DELIVERY_PARTNER is read-only) |
| BR-013 | DELIVERED items can only be modified by CHECKER or OWNER in STARTED status |
| BR-014 | Token consumption can only be recorded for DELIVERED items |
| BR-015 | Each delivery item can have at most one token consumption record |
| BR-016 | DELIVERY_PARTNER can view delivery items on their assigned route (read-only) |

### Token Book Rules

| Rule ID | Rule |
|---------|------|
| BR-020 | The token_book_issue must be in ACTIVE status to record consumption |
| BR-021 | Sheet numbers can be used in any order (non-sequential) within a book |
| BR-022 | A customer may have multiple active token books for the same milk type |
| BR-023 | After recording, the token_book_issue current_sheet is updated to the highest consumed sheet in that book |
| BR-024 | If a customer's current book is exhausted, a new book can be issued and used |
| BR-025 | CHECKER selects which book and sheet number to record for each delivery |
| BR-026 | A customer may have no token book (cash customer) - token fields remain null |
| BR-027 | Multiple deliveries to same customer on same day can use different books |

### Cash Sale Rules

| Rule ID | Rule |
|---------|------|
| BR-030 | Cash sales are only allowed on sessions in PLANNED or STARTED status |
| BR-031 | Cash sale quantity_ml must be > 0 |
| BR-032 | Cash sale amount must be >= 0 |

### Summary Rules

| Rule ID | Rule |
|---------|------|
| BR-040 | Summary is computed in real-time from underlying data (not stored) |
| BR-041 | Liters are calculated as: actual_quantity_delivered (or expected_quantity for auto-skipped) * milk_type.volume_ml / 1000 |
| BR-042 | Token sheets consumed count includes all token books used across all customers |

---

## 10. Validation Rules

| Field | Rule |
|-------|------|
| session.delivery_date | Required, must be a valid date |
| session.route_id | Required, must reference an active Route |
| session.shift | Required, must be valid Shift enum (MORNING, EVENING) |
| session.assigned_delivery_partner_id | Optional, must reference an active Employee with DELIVERY_PARTNER role |
| session.reconciliation_remarks | Optional, required when transitioning to RECONCILED |
| session.verification_remarks | Optional, required when transitioning to CLOSED |
| item.delivery_status | Required on update, must be valid DeliveryStatus enum |
| item.actual_quantity_delivered | Required when status=DELIVERED, must be > 0 |
| item.skip_reason | Required when status=SKIPPED, max 255 chars |
| item.token_book_issue_id | Optional, must reference active TokenBookIssue when provided (customer may have multiple active books) |
| item.sheet_number | Required when token_book_issue_id is provided, must be > 0 and <= book's total_sheets (non-sequential allowed) |
| item.token_remarks | Optional, max 255 chars (remarks about token usage) |
| cash_sale.customer_name | Required, max 100 chars |
| cash_sale.phone | Optional, max 15 chars |
| cash_sale.milk_type_id | Required, must reference an active MilkType |
| cash_sale.quantity_ml | Required, must be > 0 |
| cash_sale.amount | Required, must be >= 0 |
| cash_sale.payment_mode | Required, must be "CASH" or "UPI" |

---

## 11. Edge Cases

| ID | Scenario | Expected Behavior |
|----|----------|-------------------|
| EC-001 | Two users create a session for the same route/date/shift simultaneously | Database unique constraint rejects the second; system returns HTTP 400 "Session already exists" |
| EC-002 | Generate items called when customer's subscription was just deactivated | Deactivated subscription is excluded; only active subscriptions generate items |
| EC-003 | Customer's delivery exception is created AFTER items were already generated | System does NOT retroactively skip the item. Exception must be handled manually or items re-generated (if session is still PLANNED) |
| EC-004 | Customer has no token book (cash customer or book not yet issued) | Item is marked DELIVERED without token data. Token fields remain null. CHECKER can record as cash sale instead. |
| EC-005 | Token book has 1 sheet remaining and checker tries to record sheet #30 | System validates sheet_number <= total_sheets; rejects if out of range |
| EC-016 | Customer uses non-sequential sheets (e.g., sheet 5 then sheet 12 from same book) | Allowed - sheets can be used in any order within a book |
| EC-017 | Customer has multiple active token books for same milk type | Checker selects which book to record against for each delivery |
| EC-018 | Customer's current book is exhausted mid-delivery | Checker can issue new book (via token-books API) and record against new book |
| EC-019 | Customer uses sheet from Book A, then sheet from Book B on same day | Allowed - multiple books can be used for same customer |
| EC-006 | Session has delivery items but no cash sales | Summary returns cash sale totals as 0. No error. |
| EC-007 | Delivery partner tries to update item on a session they are not assigned to | System returns HTTP 403 "Access denied" (partner is read-only anyway) |
| EC-008 | OWNER attempts to start a session that has no delivery items | System allows it (items can be added later or this is intentional) |
| EC-009 | CHECKER closes a session with PENDING items still remaining | System allows it but includes pending_count in summary. CHECKER is expected to review. |
| EC-010 | Delivery date is in the past | System allows creating sessions for past dates (data correction scenario) |
| EC-011 | Delivery date is more than 7 days in the future | System allows it (planning scenario). [ASSUMPTION: No restriction on future date range] |
| EC-012 | Active session exists and same route/date/shift session is soft-deleted, then re-created | Soft-deleted session has is_active=False; unique constraint checks only active sessions. New session can be created. |
| EC-013 | Delivery partner updates a SKIPPED item to DELIVERED | Allowed while session is STARTED. This handles the case where partner arrives late and customer is now available. |
| EC-014 | Cash sale with payment_mode not in allowed values | HTTP 422 validation error |
| EC-015 | Session is STARTED but all items are still PENDING | Allowed. Partner may not have started recording yet. |

---

## 12. Data Requirements

### 12.1 New Database Tables

#### Table: `delivery_sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, indexed | Auto-increment primary key |
| delivery_date | Date | NOT NULL | The date of delivery |
| route_id | Integer | FK(routes.id), NOT NULL | Route for this session |
| shift | String(10) | NOT NULL | MORNING or EVENING |
| status | String(20) | NOT NULL, default='PLANNED' | PLANNED, STARTED, COMPLETED, RECONCILED, CLOSED |
| assigned_delivery_partner_id | Integer | FK(employees.id), NULLABLE | Assigned delivery partner |
| created_by | Integer | FK(users.id), NOT NULL | User who created the session |
| reconciled_by | Integer | FK(users.id), NULLABLE | CHECKER who reconciled the session |
| verified_by | Integer | FK(users.id), NULLABLE | OWNER who closed the session |
| reconciliation_remarks | String(255) | NULLABLE | Checker's remarks on reconciliation |
| verification_remarks | String(255) | NULLABLE | OWNER's remarks on close |
| remarks | String(255) | NULLABLE | General remarks |
| is_active | Boolean | NOT NULL, default=True | Soft delete flag |
| created_at | DateTime(timezone) | server_default=now() | Creation timestamp |
| updated_at | DateTime(timezone) | server_default=now(), onupdate=now() | Last update timestamp |

**Unique Constraint**: (route_id, delivery_date, shift) WHERE is_active = True
**Indexes**: (delivery_date), (route_id, delivery_date), (status)

#### Table: `delivery_items`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, indexed | Auto-increment primary key |
| delivery_session_id | Integer | FK(delivery_sessions.id), NOT NULL | Parent session |
| customer_id | Integer | FK(customers.id), NOT NULL | Customer receiving delivery |
| subscription_id | Integer | FK(subscriptions.id), NULLABLE | Source subscription (null for cash sales) |
| milk_type_id | Integer | FK(milk_types.id), NOT NULL | Type of milk |
| expected_quantity | Integer | NOT NULL | Quantity from subscription |
| actual_quantity_delivered | Integer | NULLABLE | Actual quantity delivered |
| delivery_status | String(20) | NOT NULL, default='PENDING' | PENDING, DELIVERED, SKIPPED, CANCELLED |
| skip_reason | String(255) | NULLABLE | Reason for skip |
| token_book_issue_id | Integer | FK(token_book_issues.id), NULLABLE | Token book used (customer may have multiple) |
| sheet_number | Integer | NULLABLE | Sheet number consumed (can be non-sequential) |
| token_remarks | String(255) | NULLABLE | Remarks about token usage |
| is_active | Boolean | NOT NULL, default=True | Soft delete flag |
| created_at | DateTime(timezone) | server_default=now() | Creation timestamp |
| updated_at | DateTime(timezone) | server_default=now(), onupdate=now() | Last update timestamp |

**Indexes**: (delivery_session_id), (customer_id), (delivery_status), (token_book_issue_id)

#### Table: `cash_sales`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PK, indexed | Auto-increment primary key |
| delivery_session_id | Integer | FK(delivery_sessions.id), NOT NULL | Parent session |
| customer_name | String(100) | NOT NULL | Walk-in customer name |
| phone | String(15) | NULLABLE | Optional phone number |
| milk_type_id | Integer | FK(milk_types.id), NOT NULL | Type of milk sold |
| quantity_ml | Integer | NOT NULL | Quantity in ml |
| amount | Numeric(10,2) | NOT NULL | Amount collected |
| payment_mode | String(20) | NOT NULL | CASH or UPI |
| remarks | String(255) | NULLABLE | Optional remarks |
| is_active | Boolean | NOT NULL, default=True | Soft delete flag |
| created_at | DateTime(timezone) | server_default=now() | Creation timestamp |
| updated_at | DateTime(timezone) | server_default=now(), onupdate=now() | Last update timestamp |

**Indexes**: (delivery_session_id)

### 12.2 Entity Relationship

```
Route 1---M Customer 1---M Subscription
                         |
                         | 1
DeliverySession 1---M DeliveryItem ---M TokenBookIssue
     |                                     |
     | 1                                   | 1
     +---M CashSale                        +---M TokenBookPayment
     
Employee (delivery partner) --- assigned to DeliverySession
User (creator) --- created_by on DeliverySession
User (checker) --- verified_by on DeliverySession
MilkType --- referenced by DeliveryItem and CashSale
DeliveryException --- consulted during item generation
```

---

## 13. API Considerations

### 13.1 New Router: `/delivery-sessions`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/delivery-sessions/` | Create a new session | OWNER, CHECKER |
| GET | `/delivery-sessions/` | List sessions (with filters) | ALL roles (filtered) |
| GET | `/delivery-sessions/{session_id}` | Get session detail with items and cash sales | ALL roles (filtered) |
| PUT | `/delivery-sessions/{session_id}` | Update session (partner assignment, remarks) | OWNER, CHECKER |
| PUT | `/delivery-sessions/{session_id}/start` | Transition to STARTED | OWNER, CHECKER |
| PUT | `/delivery-sessions/{session_id}/complete` | Transition to COMPLETED | CHECKER |
| PUT | `/delivery-sessions/{session_id}/reconcile` | Transition to RECONCILED | CHECKER |
| PUT | `/delivery-sessions/{session_id}/close` | Transition to CLOSED (final lock) | OWNER |
| POST | `/delivery-sessions/{session_id}/generate-items` | Auto-generate delivery items | OWNER, CHECKER |
| GET | `/delivery-sessions/{session_id}/summary` | Get daily summary | ALL roles (filtered) |
| DELETE | `/delivery-sessions/{session_id}` | Soft-delete session | OWNER |

### 13.1b New Router: `/delivery-partner` (Read-Only)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/delivery-partner/route-customers` | View customers on partner's assigned route | DELIVERY_PARTNER |
| GET | `/delivery-partner/route-sessions` | View sessions for partner's assigned route | DELIVERY_PARTNER |

### 13.2 Nested Endpoints under Sessions

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/delivery-sessions/{session_id}/items` | List all delivery items for session | ALL roles (filtered) |
| PUT | `/delivery-sessions/{session_id}/items/{item_id}` | Update delivery item status | CHECKER, OWNER |
| POST | `/delivery-sessions/{session_id}/items/{item_id}/token` | Record token consumption | CHECKER, OWNER |
| POST | `/delivery-sessions/{session_id}/cash-sales` | Record a cash sale | CHECKER, OWNER |
| GET | `/delivery-sessions/{session_id}/cash-sales` | List cash sales for session | ALL roles (filtered) |
| PUT | `/delivery-sessions/{session_id}/cash-sales/{sale_id}` | Update a cash sale | CHECKER, OWNER |
| DELETE | `/delivery-sessions/{session_id}/cash-sales/{sale_id}` | Soft-delete a cash sale | OWNER |

### 13.3 Query Parameters for Session List

| Parameter | Type | Description |
|-----------|------|-------------|
| date_from | Date | Filter sessions from this date |
| date_to | Date | Filter sessions up to this date |
| route_id | Integer | Filter by route |
| shift | Shift enum | Filter by shift |
| status | SessionStatus enum | Filter by status |
| delivery_partner_id | Integer | Filter by assigned partner |

### 13.4 Error Response Format

Follow existing exception pattern:

```python
# app/exceptions/delivery_session.py

class DeliverySessionNotFoundError(Exception):
    def __init__(self):
        super().__init__("Delivery session not found.")

class DuplicateDeliverySessionError(Exception):
    def __init__(self, route_id, date, shift):
        super().__init__(
            f"Delivery session already exists for route {route_id} on {date} ({shift})."
        )

class InvalidSessionStatusTransitionError(Exception):
    def __init__(self, current_status, target_status):
        super().__init__(
            f"Cannot transition from {current_status} to {target_status}."
        )

class SessionNotActiveError(Exception):
    def __init__(self):
        super().__init__("Session is not active. Cannot modify items.")

class ItemsAlreadyGeneratedError(Exception):
    def __init__(self):
        super().__init__("Delivery items already generated for this session.")

class DeliveryItemNotFoundError(Exception):
    def __init__(self):
        super().__init__("Delivery item not found.")

class InvalidDeliveryItemUpdateError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CashSaleNotFoundError(Exception):
    def __init__(self):
        super().__init__("Cash sale not found.")

class TokenRecordingError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SessionNotAssignedError(Exception):
    def __init__(self):
        super().__init__("You are not assigned to this delivery session.")
```

---

## 14. Database Impact

### 14.1 New Tables (3)

| Table | Purpose |
|-------|---------|
| `delivery_sessions` | Session header per route/date/shift |
| `delivery_items` | Individual customer delivery records |
| `cash_sales` | Ad-hoc milk sales within a session |

### 14.2 Modified Tables (1)

| Table | Change |
|-------|--------|
| `app/constants/statuses.py` | Add RECONCILED to SessionStatus enum |

### 14.3 New Columns on delivery_sessions

| Column | Type | Description |
|--------|------|-------------|
| reconciled_by | Integer (FK users.id) | CHECKER who reconciled |
| reconciliation_remarks | String(255) | Checker's reconciliation remarks |

### 14.4 Indirect Read Dependencies

| Existing Table | Read For |
|----------------|----------|
| `subscriptions` | Item generation (query active subscriptions per route/shift) |
| `customers` | Item generation (query active customers per route), partner view |
| `routes` | Session creation (validate route), partner route assignment |
| `milk_types` | Item generation (volume_ml for summary), cash sale validation |
| `employees` | Delivery partner assignment validation, partner route lookup |
| `delivery_exceptions` | Item generation (auto-skip for exceptions), partner view |
| `token_identities` | Token book lookup for sheet tracking, partner view |
| `token_book_issues` | Token consumption recording, partner view |
| `users` | Audit fields (created_by, reconciled_by, verified_by) |

### 14.4 New Alembic Migration

A single migration file `create_delivery_tables.py` will create all 3 new tables with appropriate indexes and constraints.

---

## 15. UI Considerations

> API-only phase. However, the API responses should be designed to support future UI needs.

- Session list response should include computed counts (total_items, delivered_count, pending_count) for dashboard display
- Summary response should be structured for direct chart/table rendering
- Delivery items should include nested customer and milk_type details for display without extra API calls
- Status fields should use human-readable enum values (PLANNED, STARTED, etc.)

---

## 16. Security Considerations

| ID | Consideration |
|----|---------------|
| SC-001 | All endpoints MUST require JWT authentication |
| SC-002 | DELIVERY_PARTNER can only view sessions for their assigned route (read-only) |
| SC-003 | DELIVERY_PARTNER has NO write access to delivery items, cash sales, or session status |
| SC-004 | DELIVERY_PARTNER view endpoints are isolated to their assigned route only |
| SC-005 | Only CHECKER can record delivery status, token consumption, and reconcile |
| SC-006 | Only OWNER can close sessions (final lock) |
| SC-007 | created_by, reconciled_by, and verified_by MUST be set from the authenticated user's ID, never from request body |
| SC-008 | Soft-delete prevents data loss; only OWNER can soft-delete sessions |

---

## 17. Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R-001 | Large routes (500+ customers) may slow item generation | Use bulk insert with SQLAlchemy; add database indexes on lookup columns |
| R-002 | Concurrent session creation for same route/date/shift | Database unique constraint handles this; application returns clear error |
| R-003 | Delivery partner reports wrong quantities verbally | CHECKER records data; reconciliation step verifies totals match physical records |
| R-004 | Token book data inconsistency between delivery record and book issue | System updates current_sheet atomically with delivery item update |
| R-005 | Sessions left in STARTED status indefinitely | [ASSUMPTION] No auto-cleanup in this phase. OWNER can manually close or soft-delete. |

---

## 18. Assumptions

1. **Employee model linkage**: The `employees` table already has a `user_id` FK and `role` field. Delivery partners are employees with role='DELIVERY_PARTNER'. The system can look up the employee record from the authenticated user via `Employee.user_id`.

2. **Session date flexibility**: Sessions can be created for past dates (data correction) and future dates (planning). No artificial date range restrictions.

3. **Delivery exceptions are pre-registered**: The system relies on delivery exceptions being created BEFORE the delivery session items are generated. Retroactive exceptions require manual handling.

4. **Token book sheet model**: The `current_sheet` field on `TokenBookIssue` represents the last consumed sheet number. Sheet numbers are sequential integers starting from 1.

5. **No inventory deduction**: This feature records deliveries but does NOT deduct from any dairy-side inventory. Inventory management is out of scope.

6. **Single delivery partner per session**: A session is assigned to one delivery partner. Routes requiring multiple partners per shift need multiple sessions.

7. **Cash sales are not linked to customers**: Walk-in customers may not exist in the customer table. Cash sales capture name/phone directly without requiring a customer record.

8. **Session summary is computed, not stored**: Summary data is calculated on-the-fly from delivery_items and cash_sales tables. No denormalized summary table is needed at this stage.

9. **No auto-cleanup of stale sessions**: Sessions left in PLANNED or STARTED status are not automatically closed or cleaned up.

10. **Delivery date is a date, not datetime**: The session stores a calendar date (YYYY-MM-DD), not a timestamp. Shift (MORNING/EVENING) provides the time resolution.

11. **Delivery Partner is READ-ONLY**: The delivery partner's job is to deliver milk and collect tokens. They view customer info in the app but do not enter data. All data entry is done by the CHECKER.

12. **Reconciliation before close**: Sessions must go through RECONCILED status before being CLOSED. This ensures the checker verifies totals match physical records.

---

## 19. Decisions Made

| ID | Question | Decision |
|----|----------|----------|
| OQ-001 | Should OWNER role also be able to act as a delivery partner? | **No** - Owner is not a delivery person |
| OQ-002 | Should DELIVERY_PARTNER have write access? | **No** - Partner is read-only, CHECKER records everything |
| OQ-003 | What is the maximum number of sheets in a token book? | **30 sheets** (fixed for now) |
| OQ-004 | Should completed delivery items automatically update token_book_issue's current_sheet? | **Yes** - Update atomically during recording |
| OQ-005 | Can a session be soft-deleted while it has DELIVERED items? | **No** - COMPLETED/CLOSED sessions cannot be deleted |
| OQ-006 | Should the delivery item generation be automatic on session creation? | **No** - Separate API call for flexibility |
| OQ-007 | Should cash sales support partial payments? | **No** - Immediate full payment only |
| OQ-008 | What is the session lifecycle? | **PLANNED → STARTED → COMPLETED → RECONCILED → CLOSED** |
| OQ-009 | Who can view delivery partner's data? | **Partner sees only own route** (read-only) |

---

## 20. Acceptance Criteria (Summary)

| AC | Criteria |
|----|----------|
| AC-001 | Owner/Checker can create a delivery session for a route/date/shift |
| AC-002 | System rejects duplicate sessions for same route/date/shift |
| AC-003 | System auto-generates delivery items from active subscriptions for the session route and shift |
| AC-004 | Customers with delivery exceptions are auto-marked as SKIPPED during item generation |
| AC-005 | CHECKER can update PENDING items to DELIVERED/SKIPPED/CANCELLED |
| AC-006 | Token consumption is recorded only for DELIVERED items against active token books |
| AC-007 | Cash sales can be recorded by CHECKER within active sessions |
| AC-008 | Session lifecycle follows PLANNED → STARTED → COMPLETED → RECONCILED → CLOSED |
| AC-009 | Only CHECKER can reconcile sessions |
| AC-010 | Only OWNER can close sessions (final lock) |
| AC-011 | Daily summary accurately reflects all delivery items and cash sales |
| AC-012 | RECONCILED sessions can be closed by OWNER |
| AC-013 | CLOSED sessions are fully locked from modification |
| AC-014 | DELIVERY_PARTNER can only see sessions for their assigned route (read-only) |
| AC-015 | DELIVERY_PARTNER has NO write access to delivery items or sessions |
| AC-016 | All new endpoints follow layered architecture pattern |
| AC-017 | Alembic migration creates all 3 new tables successfully |

---

## 21. Implementation Notes

### 21.1 File Structure (New Files)

```
app/
  models/
    delivery_session.py          # DeliverySession ORM model
    delivery_item.py             # DeliveryItem ORM model
    cash_sale.py                 # CashSale ORM model
  schemas/
    delivery_session.py          # Pydantic schemas for sessions
    delivery_item.py             # Pydantic schemas for items
    cash_sale.py                 # Pydantic schemas for cash sales
  services/
    delivery_session_service.py  # Session lifecycle + item generation
    delivery_item_service.py     # Item CRUD + token tracking
    cash_sale_service.py         # Cash sale CRUD
  routers/
    delivery_sessions.py         # All delivery session endpoints
    delivery_partner.py          # Read-only endpoints for delivery partners
  exceptions/
    delivery_session.py          # Session-specific exceptions
    delivery_item.py             # Item-specific exceptions
    cash_sale.py                 # Cash sale-specific exceptions
  constants/
    delivery_statuses.py         # DeliveryItemStatus enum (PENDING, DELIVERED, SKIPPED, CANCELLED)
alembic/versions/
    <timestamp>_create_delivery_tables.py
```

### 21.2 Constants to Add

```python
# app/constants/delivery_statuses.py
class DeliveryItemStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"

# Note: SessionStatus needs to be updated in app/constants/statuses.py
# Add RECONCILED to existing: PLANNED, STARTED, COMPLETED, RECONCILED, CLOSED
```

### 21.3 Key Service Method Signatures

```python
# delivery_session_service.py
def create(db: Session, session: DeliverySessionCreate, created_by_user_id: int) -> DeliverySession
def get_all(db: Session, filters: SessionFilters, current_user: User) -> list[dict]
def get_by_id(db: Session, session_id: int, current_user: User) -> dict
def update(db: Session, session_id: int, session: DeliverySessionUpdate) -> DeliverySession
def transition_status(db: Session, session_id: int, target_status: str, user: User) -> DeliverySession
def generate_items(db: Session, session_id: int) -> list[DeliveryItem]
def get_summary(db: Session, session_id: int) -> dict
def soft_delete(db: Session, session_id: int) -> DeliverySession
def reconcile(db: Session, session_id: int, remarks: str, user: User) -> DeliverySession
def close(db: Session, session_id: int, remarks: str, user: User) -> DeliverySession

# delivery_item_service.py
def get_by_session(db: Session, session_id: int) -> list[dict]
def update_status(db: Session, session_id: int, item_id: int, update: DeliveryItemUpdate, user: User) -> DeliveryItem
def record_token(db: Session, session_id: int, item_id: int, token_data: TokenConsumptionCreate) -> DeliveryItem
def batch_update(db: Session, session_id: int, updates: list[BatchItemUpdate], user: User) -> list[DeliveryItem]

# cash_sale_service.py
def create(db: Session, session_id: int, sale: CashSaleCreate) -> CashSale
def get_by_session(db: Session, session_id: int) -> list[CashSale]
def update(db: Session, session_id: int, sale_id: int, sale: CashSaleUpdate) -> CashSale
def soft_delete(db: Session, session_id: int, sale_id: int) -> CashSale

# delivery_partner_service.py (Read-only)
def get_route_customers(db: Session, employee_id: int) -> list[dict]
def get_route_sessions(db: Session, employee_id: int, filters: SessionFilters) -> list[dict]
```

### 21.4 Items Already Provided by Codebase

| Item | Status |
|------|--------|
| `SessionStatus` enum (PLANNED, STARTED, COMPLETED, CLOSED) | Already exists in `app/constants/statuses.py` - **ADD RECONCILED** |
| `Shift` enum (MORNING, EVENING) | Already exists in `app/constants/shifts.py` |
| `DeliveryStatus` enum (DELIVERED, SKIPPED, CANCELLED) | Already exists in `app/constants/statuses.py` - **EXTEND with PENDING** |
| `require_role` dependency | Already exists in `app/core/roles.py` |
| `get_current_user` dependency | Already exists in `app/core/auth.py` |
| `Base` declarative base | Already exists in `app/database.py` |
| `BusinessException` base class | Already exists in `app/exceptions/base.py` |
| Soft-delete pattern | Established across all existing models |

### 21.5 Migration Strategy

Single Alembic migration creating all 3 tables in order:
1. `delivery_sessions` (no dependencies on new tables)
2. `delivery_items` (depends on `delivery_sessions`)
3. `cash_sales` (depends on `delivery_sessions`)

All foreign keys reference existing tables + `delivery_sessions`. Include proper indexes as specified in Section 12.1.

### 21.6 Constants Update

Update `app/constants/statuses.py` to add RECONCILED to SessionStatus:
```python
class SessionStatus(str, Enum):
    PLANNED = "PLANNED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    RECONCILED = "RECONCILED"
    CLOSED = "CLOSED"
```

---

*End of Specification*
