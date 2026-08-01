# Feature Specification: Delivery Management Pages

**Feature Branch**: `007-delivery-management-pages`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Delivery Management Pages"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Delivery Sessions (Priority: P1)

As a Checker/Owner/Admin, I want to create a delivery session (route + date + shift + delivery partner), see all sessions in a filterable list, and open a session detail page, so that daily delivery operations begin and are trackable.

**Why this priority**: The session is the container for the entire daily delivery workflow. Nothing else (dispatch, registration, reconciliation) can happen without it, so this is the foundation.

**Independent Test**: Can be fully tested by creating a session for a route/date/shift, seeing it appear in the session list with correct status PLANNED, filtering the list by date/route/status, and opening the detail page which shows the dispatch section.

**Acceptance Scenarios**:

1. **Given** active routes and delivery partners exist, **When** the Checker creates a session with route, date, shift, and partner, **Then** the session appears in the list with status PLANNED.
2. **Given** a duplicate session for the same route + date + shift already exists, **When** the Checker tries to create it again, **Then** an error is shown and no session is created.
3. **Given** the session list, **When** the Checker filters by date, route, or status, **Then** only matching sessions are shown.
4. **Given** a PLANNED session, **When** the Checker opens it, **Then** the detail page shows the Dispatch section (record total milk loaded) and the operation transitions the session to STARTED.

---

### User Story 2 - Register Deliveries and Token Sheets (Priority: P1)

As a Checker, I want to view the session checklist (expected customers from active subscriptions, honoring exceptions) and register each customer's delivery status and token sheet, so that the daily record is accurate and prepaid token usage is tracked.

**Why this priority**: Delivery registration is the core daily accounting operation — every customer outcome (delivered, pending token, cash sale, not delivered, cancelled) must be captured so reconciliation can balance.

**Independent Test**: Can be fully tested by opening a session's checklist, changing each customer's status (DELIVERED with token sheet, PENDING_TOKEN, CASH_SALE with amount, NOT_DELIVERED, CANCELLED), observing token validation warnings with acknowledgment, and adding unplanned deliveries.

**Acceptance Scenarios**:

1. **Given** a session on the checklist, **When** the Checker marks a customer DELIVERED and enters the token sheet number, **Then** the token sheet is validated against the customer's token book and registered.
2. **Given** a token sheet that is out of sequence (e.g., Sheet #5 before #4), **When** the Checker enters it, **Then** a warning is shown that must be acknowledged before registration proceeds.
3. **Given** a customer with no token sheet, **When** the Checker marks them PENDING_TOKEN, **Then** the delivery is recorded as pending token.
4. **Given** a customer paying cash, **When** the Checker marks them CASH_SALE and enters the amount, **Then** the delivery and cash amount are recorded.
5. **Given** a customer who did not receive milk, **When** the Checker marks them NOT_DELIVERED or CANCELLED, **Then** the delivery is recorded without token registration.
6. **Given** an unplanned delivery (customer not on the schedule or a walk-in cash customer), **When** the Checker adds it via the "Add Unplanned Delivery" form, **Then** it appears in the checklist with source UNPLANNED and is included in reconciliation.

---

### User Story 3 - Reconcile and Close Session (Priority: P1)

As a Checker, I want to review the reconciliation summary (loaded vs token-registered vs cash vs returned), adjust cash sales and returned milk, validate, and close the session once balanced, so that the day's route is finalized and reports can be generated.

**Why this priority**: Reconciliation is the critical control point — it verifies all dispatched milk is accounted for and is required before a session can be closed. This completes the daily workflow.

**Independent Test**: Can be fully tested by entering cash sales and returned milk against a dispatched session, watching the difference recalculate, validating, and closing only when balanced.

**Acceptance Scenarios**:

1. **Given** 5L loaded, 3L token-registered, 1L cash sale, 1L returned, **When** the Checker opens reconciliation, **Then** the route shows BALANCED (loaded = accounted).
2. **Given** a loaded session with unaccounted milk, **When** the Checker views reconciliation, **Then** the difference is shown and status is UNBALANCED.
3. **Given** an unbalanced session, **When** the Checker attempts to close, **Then** closure is blocked and the difference is shown.
4. **Given** a balanced session, **When** the Checker closes it, **Then** the session status becomes CLOSED and all inputs become read-only, with a read-only session summary available.
5. **Given** a closed session, **When** anyone attempts to edit it, **Then** the system rejects the edit.

---

### User Story 4 - Edit Previous Deliveries and Reopen Sessions (Priority: P2)

As an Owner, I want to reopen closed sessions and edit previous deliveries (with a reason and audit trail), so that mistakes (e.g., wrong status, token sheet errors) can be corrected and token sheets returned.

**Why this priority**: Real-world mistakes happen; without correction capability incorrect records persist and customers lose prepaid tokens unfairly. This is an Owner-only corrective workflow, hence P2.

**Independent Test**: Can be fully tested by reopening a closed session with a reason, editing a delivery (e.g., DELIVERED → NOT_DELIVERED, returning a token sheet), closing again, and viewing the edit history.

**Acceptance Scenarios**:

1. **Given** a closed session, **When** the Owner reopens it with a reason, **Then** the session becomes editable and the reopen is recorded.
2. **Given** a reopened session, **When** the Owner edits a delivery's status/token sheet, **Then** the change is recorded with the reason, token book sheet counts update, and the edit appears in the edit history.
3. **Given** a reopened session after edits, **When** the Owner closes it again, **Then** reconciliation is recalculated and the session returns to CLOSED.

---

### Edge Cases

- **Duplicate session**: Same route + date + shift already exists → creation blocked with a clear message.
- **Dispatch already recorded**: Dispatching twice → blocked; the Dispatch section is hidden once dispatched.
- **Session not yet dispatched**: Delivery registration and reconciliation sections are not usable until dispatch is recorded (session is STARTED).
- **Out-of-sequence token sheet**: Warning shown; registration proceeds only after acknowledgment; warning is recorded in the audit trail.
- **Token sheet from completed book**: Registration is rejected as an error (sheet cannot be used from a completed book).
- **Cash sale without amount**: Cash sale requires an amount > 0 before it can be saved.
- **Reconciliation with no returned milk**: Difference computed; session stays UNBALANCED and cannot close.
- **Closing an unbalanced session**: Closure prevented; the difference is displayed.
- **Editing a closed session**: Rejected everywhere except through the Owner reopen/edit flow.
- **Reopening without a reason**: The reason is required before a session can be reopened.
- **Empty checklist**: A session whose route has no active subscriptions still opens; checklist shows an empty state and the route can be dispatched/reconciled as long as loaded = accounted (0 or returned/cash).
- **Concurrent updates**: If a session was modified elsewhere (version mismatch), the user is informed and must refresh before saving.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): Frontend-only feature — no backend changes. Pages/API modules follow the established `types → api → hooks → pages` layering; existing backend routers/services/schemas are consumed as-is.
- **Role-Based Access Control** (Principle II): Session management, dispatch, registration, reconciliation, and close are available to OWNER, ADMIN, and CHECKER. Edit/reopen of previous sessions is OWNER-only. DELIVERY_PARTNER has no access to these pages. All form routes are protected by role guards; the backend enforces the same rules regardless of client guards.
- **Soft Deletes** (Principle IV): No new entities; existing backend behavior is reused (sessions are never hard-deleted).
- **Schema-Driven Contracts** (Principle V): Frontend TypeScript interfaces mirror the existing backend response/request schemas exactly; no new backend schemas are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display the delivery session list with route, date, shift, delivery partner, status, reconciliation status, and loaded milk totals.
- **FR-002**: The system MUST allow filtering the session list by date, route, and status.
- **FR-003**: Authorized users MUST be able to create a delivery session by selecting a route, date, shift (MORNING/EVENING), and delivery partner.
- **FR-004**: The system MUST reject creating a duplicate session for the same route + date + shift with a clear message.
- **FR-005**: Authorized users MUST be able to open a session detail page showing Dispatch, Checklist/Registration, Reconciliation, Close, and Summary sections in a single scrollable view, with sections enabled/disabled according to session status.
- **FR-006**: The system MUST allow recording dispatch (total milk loaded) for a PLANNED session and MUST prevent recording dispatch more than once per session.
- **FR-007**: The system MUST display the session checklist of expected customers (name, address, phone, milk type, quantity) based on active subscriptions, honoring active exceptions.
- **FR-008**: Authorized users MUST be able to set each checklist row's delivery status to DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, or CANCELLED.
- **FR-009**: For DELIVERED rows, the system MUST allow entering a token sheet number, validate it against the customer's token book, and register it.
- **FR-010**: The system MUST surface token validation warnings (e.g., out-of-sequence sheet, new book while old book unfinished) and require explicit acknowledgment before the registration proceeds.
- **FR-011**: For CASH_SALE rows, the system MUST require a cash amount and record it.
- **FR-012**: Authorized users MUST be able to add unplanned deliveries (existing customer or ad-hoc cash customer with milk type, quantity, and amount) and these MUST be included in reconciliation.
- **FR-013**: The system MUST display the reconciliation summary: loaded milk, token-registered milk, cash sales, returned milk, total accounted, difference, and balance status.
- **FR-014**: Authorized users MUST be able to add and remove cash sales and enter returned milk during reconciliation.
- **FR-015**: The system MUST allow validating the reconciliation and MUST show issues that prevent closing (e.g., unbalanced, unaccounted milk).
- **FR-016**: The system MUST allow closing a session ONLY when it is balanced, with a confirmation step; closing finalizes the session as read-only.
- **FR-017**: The system MUST display a read-only session summary after the session is closed (customer counts by status and milk totals).
- **FR-018**: For OWNER only, the system MUST allow reopening a closed session with a required reason and editing previous deliveries (status, token sheet, cash amount).
- **FR-019**: The system MUST record all edits with the reason and editor, and display the session edit history.
- **FR-020**: After edits on a reopened session, the system MUST recalculate reconciliation and allow the session to be closed again only when balanced.
- **FR-021**: The system MUST show loading states while session data loads, a friendly empty state when a list or checklist has no records, and error notifications for failed operations.
- **FR-022**: The system MUST restrict access: session/checklist/reconciliation screens for OWNER/ADMIN/CHECKER; edit/reopen screens for OWNER only; no DELIVERY_PARTNER access to any delivery management page.
- **FR-023**: The system MUST confirm destructive or finalizing actions (close session, reopen) before executing them.

### Key Entities *(include if feature involves data)*

- **Delivery Session**: A single route's delivery run for a date and shift. Key attributes: route, date, shift, delivery partner, status (PLANNED/STARTED/COMPLETED/CLOSED), total milk loaded, cash sales, returned milk, reconciliation status (PENDING/BALANCED/UNBALANCED), reopen count, version.
- **Daily Delivery**: A customer's delivery line within a session. Key attributes: customer, milk type, planned quantity, delivered quantity, delivery status (DELIVERED/PENDING_TOKEN/CASH_SALE/NOT_DELIVERED/CANCELLED), source (planned/unplanned), token sheet number.
- **Checklist**: The list of expected customers for a session derived from active subscriptions and exceptions, shown on the session detail page.
- **Token Book Issue**: The customer's active token book; token sheet registration references it and advances its current sheet, with warnings recorded for out-of-order sheets.
- **Reconciliation**: The per-session accounting view (loaded vs token-registered vs cash vs returned) that determines balance and whether the session can close.
- **Cash Sale**: A cash transaction captured during delivery (customer name, phone, milk type, quantity, amount, payment method).
- **Edit Record**: An audited change to a delivery after session close (delivery, old/new values, reason, editor, timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Checker can complete the full daily workflow (create → dispatch → register → reconcile → close) for a typical route in under 5 minutes.
- **SC-002**: 100% of sessions require a successful reconciliation showing BALANCED before a close action is accepted.
- **SC-003**: Token sheet registration completes with warnings acknowledged; out-of-sequence sheets never register silently without an acknowledgment.
- **SC-004**: 100% of Owner edits and reopens are recorded with a reason and appear in the session edit history.
- **SC-005**: A Checker can create a session and record dispatch in under 2 minutes on first use.
- **SC-006**: All three privileged roles (OWNER, ADMIN, CHECKER) can reach the session list via navigation; DELIVERY_PARTNER cannot access any delivery management page.

## Assumptions

- The backend already implements the full delivery workflow (sessions, dispatch, checklist, token registration/validation with warnings, unplanned deliveries, cash sales, reconciliation, close, reopen, edit history) — this feature is frontend-only and consumes existing endpoints unchanged.
- Session management, dispatch, registration, reconciliation, and close are available to OWNER, ADMIN, and CHECKER, matching the existing sidebar navigation; edit/reopen is OWNER-only (per the parent frontend spec US-048).
- DELIVERY_PARTNER has no access to these pages in this phase (matches current navigation); a dedicated partner app/flow is out of scope.
- The all-in-one scrollable session detail page layout is already decided (parent spec open question Q4, resolved).
- The list of expected customers (checklist) is generated by the backend; the frontend displays it as returned.
- Unplanned deliveries may reference an existing customer or a new walk-in cash customer; the backend contract defines which fields are required and the frontend mirrors them.
- Warning acknowledgment is mandatory in the UI before an out-of-order or edge-case token registration proceeds; the backend also validates.
- Duplicate-session prevention (route + date + shift) is enforced by the backend; the frontend surfaces the error.
- Existing UI patterns (DataTable, Badge, Select, Input, Button, ConfirmDialog, PageHeader, LoadingSpinner, EmptyState, role guards, react-query hooks) are reused; no new component library is introduced.
