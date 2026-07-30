# Feature Specification: Daily Delivery Management

**Feature Branch**: `002-daily-delivery-management`

**Created**: 2026-01-27

**Status**: Draft

**Input**: User description: "Implement daily delivery management for milk distribution operations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Daily Delivery List (Priority: P1)

As an Owner/Checker, I want the system to automatically generate delivery lists for each route based on customer subscriptions and exceptions, so that delivery partners know exactly who to deliver to each day.

**Why this priority**: This is the foundation of the daily delivery operation. Without automated list generation, the entire delivery process cannot function efficiently.

**Independent Test**: Can be fully tested by creating subscriptions for customers on a route, adding delivery exceptions, and verifying the system generates correct delivery lists for morning/evening shifts.

**Acceptance Scenarios**:

1. **Given** active customer subscriptions exist for Route 1, **When** the system generates the morning delivery list, **Then** all subscribed customers appear on the list with correct milk types and quantities.
2. **Given** a customer has a VACATION exception for today, **When** the delivery list is generated, **Then** that customer is excluded from today's list.
3. **Given** a customer has a NO_MILK exception for today, **When** the delivery list is generated, **Then** that customer is excluded from today's list.
4. **Given** morning and evening shifts, **When** delivery lists are generated, **Then** each shift has its own independent list.

---

### User Story 2 - Record Milk Dispatch (Priority: P1)

As an Owner/Checker, I want to record the milk dispatched to each delivery partner for each route, so that we can track total milk leaving the facility and reconcile at day end.

**Why this priority**: Dispatch recording is essential for reconciliation - without knowing how much milk was sent, we cannot verify if all milk was accounted for.

**Independent Test**: Can be tested by creating a delivery session, recording dispatch quantities, and verifying the session status changes from PLANNED to STARTED.

**Acceptance Scenarios**:

1. **Given** a delivery session for Route 1 Morning, **When** the Owner records 5 liters dispatched to delivery partner Suresh, **Then** the session shows 5 liters loaded and status changes to STARTED.
2. **Given** a delivery session, **When** dispatch is recorded, **Then** the delivery partner, route, shift, and date are captured.
3. **Given** a delivery session, **When** dispatch is already recorded, **Then** attempting to record dispatch again shows an error.

---

### User Story 3 - Register Token Sheets During Delivery (Priority: P1)

As a Checker, I want to register token sheets collected from customers during delivery, so that we track which customers have used their prepaid tokens.

**Why this priority**: Token registration is the core accounting mechanism - it tracks prepaid milk usage and is essential for financial reconciliation.

**Independent Test**: Can be tested by registering token sheets for delivered customers and verifying the token book issue's current_sheet count increments correctly.

**Acceptance Scenarios**:

1. **Given** Mrs. Sharma receives 1L milk and provides Sheet #3, **When** the Checker registers Sheet #3, **Then** the delivery is marked as DELIVERED with token registered, and the token book issue's current_sheet increments by 1.
2. **Given** Mr. Patel receives milk but has no token sheet, **When** the Checker marks it as PENDING_TOKEN, **Then** the delivery is recorded as delivered with pending token status.
3. **Given** Mrs. Iyer pays cash for milk, **When** the Checker marks it as CASH_SALE and enters the amount, **Then** the delivery is recorded as cash sale with the amount.

---

### User Story 4 - Handle Unplanned Deliveries (Priority: P2)

As a Checker, I want to add customers who weren't on today's schedule but received milk anyway, so that all deliveries are tracked for reconciliation.

**Why this priority**: Real-world operations frequently have unplanned deliveries (customer changes mind, new customer, etc.). Without this capability, reconciliation would fail.

**Independent Test**: Can be tested by adding an unplanned delivery for a customer not on the schedule and verifying it appears in reconciliation.

**Acceptance Scenarios**:

1. **Given** a customer was marked as VACATION but changes their mind, **When** the Checker adds them as unplanned delivery with token sheet, **Then** the delivery is recorded with source UNPLANNED and token is registered.
2. **Given** a new customer not yet in the system, **When** the Checker adds them as unplanned delivery, **Then** a new customer record is created and the delivery is recorded.
3. **Given** an unplanned delivery, **When** reconciliation is performed, **Then** the unplanned delivery is included in the calculation.

---

### User Story 5 - Perform Route Reconciliation (Priority: P1)

As a Checker, I want to reconcile each delivery route by entering cash sales and returned milk, so that we verify all dispatched milk is accounted for.

**Why this priority**: Reconciliation is the critical control point - it ensures no milk is missing and provides financial accountability.

**Independent Test**: Can be tested by entering cash sales and returned milk amounts, then verifying the system calculates whether the route is balanced.

**Acceptance Scenarios**:

1. **Given** 5 liters loaded, 3 liters token-registered, 1 liter cash sale, 1 liter returned, **When** reconciliation is performed, **Then** the route shows BALANCED (5 = 3 + 1 + 1).
2. **Given** 5 liters loaded, 3 liters token-registered, 1 liter cash sale, **When** reconciliation is performed with no returned milk entered, **Then** the route shows UNBALANCED with 1 liter difference.
3. **Given** an unbalanced route, **When** the Checker corrects the figures, **Then** the reconciliation recalculates automatically.

---

### User Story 6 - Close Delivery Route (Priority: P1)

As a Checker/Owner, I want to close a delivery route after reconciliation is balanced, so that the day's operations are finalized and reports are generated.

**Why this priority**: Route closing finalizes the day's work and generates permanent records for accounting and audit.

**Independent Test**: Can be tested by verifying a balanced route can be closed and becomes read-only, while an unbalanced route cannot be closed.

**Acceptance Scenarios**:

1. **Given** a balanced route with all customers processed, **When** the Checker closes the route, **Then** the session status changes to CLOSED and becomes read-only.
2. **Given** an unbalanced route, **When** the Checker attempts to close, **Then** the system prevents closure and shows the difference.
3. **Given** a closed route, **When** anyone attempts to edit, **Then** the system shows an error that the route is closed.

---

### User Story 7 - Edit Previous Delivery Session (Priority: P2)

As an Owner, I want to reopen and edit previous delivery sessions to correct mistakes (e.g., customer said no milk but partner delivered anyway), so that records are accurate and customers can get their token sheets back.

**Why this priority**: Real-world mistakes happen. Without edit capability, incorrect records persist and customers lose their prepaid tokens unfairly.

**Independent Test**: Can be tested by closing a route, reopening it, editing a delivery record, returning a token sheet, and verifying the token book's current_sheet decrements.

**Acceptance Scenarios**:

1. **Given** a closed route from yesterday, **When** the Owner reopens it with a reason, **Then** the session status changes to COMPLETED and delivery records become editable.
2. **Given** Mrs. Sharma's delivery was marked DELIVERED with Sheet #3, **When** the Owner changes it to NOT_DELIVERED and returns the token, **Then** Sheet #3 becomes available for reuse and current_sheet decrements by 1.
3. **Given** a reopened session with edits, **When** the Owner closes it again, **Then** reconciliation is recalculated and the session returns to CLOSED status.

---

### User Story 8 - Handle Non-Sequential Token Sheets (Priority: P2)

As a Checker, I want to register token sheets that are not in sequential order (e.g., Sheet #5 before #4), with appropriate warnings, so that real-world customer behavior is accommodated.

**Why this priority**: Customers frequently provide sheets out of order. Blocking non-sequential sheets would prevent legitimate transactions.

**Independent Test**: Can be tested by registering Sheet #5 when #4 hasn't been used yet, and verifying a warning is displayed but registration proceeds.

**Acceptance Scenarios**:

1. **Given** Sheet #4 hasn't been used yet, **When** the Checker registers Sheet #5, **Then** a WARNING is displayed but registration proceeds after acknowledgment.
2. **Given** Sheets #8, #9, #10 are already used, **When** the Checker registers Sheet #7, **Then** a WARNING about out-of-order sheet is displayed but registration proceeds.
3. **Given** a non-sequential registration, **When** the registration is completed, **Then** the warning is logged in the audit trail.

---

### User Story 9 - Handle New Book Before Old Finishes (Priority: P3)

As a Checker, I want to be notified when a customer uses a new token book while their old book still has unused sheets, so that we can track book transitions accurately.

**Why this priority**: While less common, this scenario occurs when customers lose books or request replacements. Tracking ensures accurate inventory.

**Independent Test**: Can be tested by having two active books for a customer, registering a sheet from the new book, and verifying a warning about the old book's remaining sheets.

**Acceptance Scenarios**:

1. **Given** Old Book #SM-001 has 10 unused sheets and New Book #SM-002 is active, **When** the Checker registers a sheet from New Book, **Then** a WARNING shows old book still has 10 sheets remaining.
2. **Given** a new book warning, **When** the Checker acknowledges and proceeds, **Then** both books remain ACTIVE and the warning is logged.
3. **Given** multiple active books, **When** viewing customer's token status, **Then** all active books and their sheet counts are displayed.

---

### Edge Cases

- What happens when a delivery partner forgets a "no milk" request and delivers anyway?
  - Owner can edit the previous session, change status to NOT_DELIVERED, and return the token sheet.

- What happens when a customer provides a token sheet from a completed book?
  - System shows ERROR - sheet cannot be registered from a COMPLETED book.

- What happens when reconciliation is balanced but a customer claims they didn't receive milk?
  - Owner reopens session, edits the specific delivery, returns token if applicable, and re-balances.

- What happens when a delivery partner returns with more milk than expected?
  - Checker enters the actual returned milk amount, and reconciliation adjusts accordingly.

- What happens when a customer has multiple milk types?
  - Each milk type has its own Token Identity and Token Book. Sheets are tracked separately per milk type.

- What happens when two users try to edit the same session simultaneously?
  - System uses optimistic locking. If a conflict is detected (session was modified by another user), the second user receives an error and must reload the session before retrying.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): Delivery routers handle HTTP concerns only. All business logic (list generation, reconciliation, token registration) lives in services. Models define delivery entities. Schemas define API contracts.

- **Role-Based Access Control** (Principle II): 
  - OWNER: Can edit previous sessions, reopen closed routes, view all reports
  - CHECKER: Can register tokens, perform reconciliation, close routes, add unplanned deliveries
  - DELIVERY_PARTNER: Can view delivery checklists for assigned routes

- **Soft Deletes** (Principle IV): All delivery records use `is_active` flag. Closed routes are not deleted, just marked as CLOSED.

- **Schema-Driven Contracts** (Principle V): Every delivery endpoint has dedicated Create, Update, and Response schemas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically generate delivery lists from active subscriptions minus active exceptions for each route/shift/date combination.
- **FR-002**: System MUST record milk dispatch with route, delivery partner, shift, date, and total liters loaded.
- **FR-003**: System MUST register token sheets with automatic validation (customer, token number, milk type, active book, sequence, duplicates).
- **FR-004**: System MUST support PENDING_TOKEN status for deliveries where token sheet is not yet provided.
- **FR-005**: System MUST support CASH_SALE status for deliveries paid with cash instead of tokens.
- **FR-006**: System MUST allow adding unplanned deliveries for customers not on the original schedule.
- **FR-007**: System MUST calculate reconciliation using formula: Loaded Milk = Token Registered + Cash Sales + Returned Milk. "Returned Milk" = undelivered milk that remained with the delivery partner.
- **FR-008**: System MUST prevent route closure unless reconciliation is balanced.
- **FR-009**: System MUST allow Owner to reopen closed sessions and edit previous delivery records.
- **FR-010**: System MUST return token sheets when delivery status changes from DELIVERED to NOT_DELIVERED, decrementing current_sheet on the token book issue.
- **FR-011**: System MUST display warnings for non-sequential token sheets but allow registration after acknowledgment.
- **FR-012**: System MUST display warnings when new book is used before old book finishes.
- **FR-013**: System MUST log all edits, warnings, and status changes in an audit trail.
- **FR-014**: System MUST generate reports after route closure (delivery, reconciliation, token collection, pending tokens, cash sales, returned milk).
- **FR-015**: System MUST keep morning and evening shifts completely independent.
- **FR-016**: System MUST support configurable sheet count per token book (stored in database).
- **FR-017**: System MUST use optimistic locking to prevent concurrent edit conflicts on the same session.
- **FR-018**: System MUST allow multiple active token books per customer (no limit), each tied to a specific milk type and token number.
- **FR-019**: System MUST allow Owner to reopen any past session without time limit.

### Key Entities

- **Delivery Session**: Represents one shift for one route on one day. Tracks status (PLANNED→STARTED→COMPLETED→CLOSED), dispatch quantities, reconciliation totals, and reopen history.

- **Daily Delivery**: Individual customer delivery record. Tracks planned vs delivered quantities, delivery status, token sheet number, source (PLANNED/UNPLANNED), and edit history.

- **Session Edit**: Audit record for changes to previous sessions. Tracks old/new values, editor, reason, and timestamp.

- **Token Sheet Warning**: Audit record for non-sequential sheets or new book usage warnings. Tracks warning code, message, acknowledgment status.

- **Token Book**: Represents a physical book issued to a customer. Tied to a specific milk type (e.g., Full Cream 1L) and token number. Customers can have multiple active books simultaneously for different milk types, sizes, or quantities (e.g., 3L subscription = 3 separate 1L books, or 1.5L = 1L book + 0.5L book).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Delivery lists can be generated for a 50-customer route in under 5 seconds.
- **SC-002**: Token sheet registration with validation completes in under 3 seconds.
- **SC-003**: Reconciliation calculation completes instantly when figures are entered.
- **SC-004**: 100% of dispatched milk is accounted for in reconciliation (balanced routes).
- **SC-005**: All edits to previous sessions are permanently logged with reason and editor identity.
- **SC-006**: Zero data loss - all original records preserved even after edits (audit trail).
- **SC-007**: Checkers can process a 30-customer route (registration + reconciliation) in under 15 minutes.

## Clarifications

### Session 2026-01-27

- Q: How many sheets per token book? → A: Configurable per token book (stored in database)
- Q: How to handle concurrent edits on same session? → A: Optimistic locking (last-write-wins with conflict detection)
- Q: Maximum active token books per customer? → A: No limit - customers can have multiple active books for different milk types/sizes/quantities (e.g., 3L subscription = 3 books of 1L each, or 1.5L = 1L book + 0.5L book)
- Q: What does "returned milk" include in reconciliation? → A: "Returned milk" = undelivered milk that remained with the delivery partner (not customer-refused)
- Q: Time limit for reopening past sessions? → A: No time limit - any past session can be reopened by Owner

## Assumptions

- Existing subscription, customer, route, milk type, and token book modules are already implemented and functional.
- Each customer can have multiple token books (one per milk type, or multiple for same milk type).
- Morning and evening shifts operate completely independently with separate sessions.
- Only Owner can edit previous sessions; Checker can only edit current day before closing.
- Delivery partners do not interact with the ERP during delivery - they work with physical checklists.
- Physical token sheets have only sheet numbers visible to customers; issue numbers are system-internal references.
