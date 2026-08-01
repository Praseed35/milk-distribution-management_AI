# Feature Specification: Payment Management Pages

**Feature Branch**: `008-payment-management-pages`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "phase 6 payment management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Customer Payments (Priority: P1)

As an Owner/Admin, I want to record customer payments (cash, UPI, card, cheque, or bank transfer) either as an advance or against a bill, so that accounts receivable is updated and the customer's outstanding balance reduces.

**Why this priority**: Recording payments is the most frequent financial action and directly feeds outstanding balances and bill status (P0 in the parent spec, US-050). Everything else in this phase either depends on it (outstanding view) or pairs with it (bill payment).

**Independent Test**: Can be fully tested by opening the Payments page, recording an ADVANCE payment for a customer with amount, mode, and reference, seeing it appear in the history, then recording a BILL_PAYMENT against an unpaid bill and watching the bill's paid amount and status update.

**Acceptance Scenarios**:

1. **Given** an active customer, **When** an Owner records an ADVANCE payment with a positive amount and a payment mode, **Then** the payment appears in the history with the system-assigned date, customer name, amount, mode, and type ADVANCE.
2. **Given** an unpaid, non-cancelled bill, **When** an Owner records a BILL_PAYMENT for that bill, **Then** the bill's paid amount increases, its balance decreases, and its status updates to PAID (balance fully cleared) or PARTIAL (partially paid).
3. **Given** the BILL_PAYMENT payment type selected, **When** the Owner tries to save without choosing a bill, **Then** saving is blocked with a clear message.
4. **Given** a bill that is already PAID or CANCELLED, **When** the Owner tries to pay it, **Then** the payment is rejected with a clear message and nothing is recorded.
5. **Given** a recorded ADVANCE payment, **When** the Owner views the payment history, **Then** the ADVANCE payment is shown as not linked to any bill.

---

### User Story 2 - Generate Customer Bills (Priority: P1)

As an Owner/Admin, I want to generate bills for one or more customers over a date range, so that periodic billing is automated from recorded deliveries.

**Why this priority**: Bill generation is the other core P0 flow (US-051) — it turns delivered quantities into payable amounts and creates the bills that BILL_PAYMENTs settle.

**Independent Test**: Can be fully tested by selecting a customer and a date range that covers delivered deliveries, generating the bill, seeing it in the Bills list with line items per milk type and the correct total, then re-running generation for a customer/period with no deliveries and confirming no bill is created with a clear explanation.

**Acceptance Scenarios**:

1. **Given** a customer with DELIVERED and/or CASH_SALE deliveries within a date range, **When** an Owner generates a bill for that customer and period, **Then** a bill is created with line items grouped by milk type (quantity, unit price, amount), a total, status PENDING, and zero paid.
2. **Given** multiple selected customers with deliveries in the period, **When** the Owner generates bills, **Then** one bill is created per customer and the results are shown together.
3. **Given** a customer with no deliveries in the selected period, **When** the Owner includes them in generation, **Then** no bill is created for them and the page explains why.
4. **Given** the Bills list, **When** the Owner filters by customer, status, or date range, **Then** only matching bills are shown.
5. **Given** a generated bill, **When** the Owner opens its detail, **Then** the line items, totals, due date, remarks, and the payments applied to it are shown.

---

### User Story 3 - View Outstanding Balances (Priority: P1)

As an Owner/Admin, I want to see each customer's outstanding balance (total billed, total paid, current balance, last bill date, last payment date), so that I can follow up on collections.

**Why this priority**: This is the receivables view (US-052) that turns payment and bill data into actionable collection information; it is the business-facing output of this phase.

**Independent Test**: Can be fully tested by recording a payment that settles part of a bill, opening the Outstanding page, and seeing that customer's balance equal billed minus paid with correct last bill/payment dates.

**Acceptance Scenarios**:

1. **Given** customers with active bills, **When** an Owner opens the Outstanding page, **Then** each customer's total billed, total paid, balance, last bill date, and last payment date are displayed.
2. **Given** a customer with no bills or payments, **When** the Owner views outstanding, **Then** the customer shows a zero balance.
3. **Given** a newly recorded payment, **When** the Owner refreshes the Outstanding page, **Then** the affected customer's balance reflects the payment immediately.
4. **Given** the Outstanding page, **When** the Owner narrows to a single customer, **Then** only that customer's summary is shown.

---

### User Story 4 - Payment History and Filters (Priority: P2)

As an Owner/Admin, I want to view payment history filtered by customer, payment mode, payment type, and date range, so that financial tracking and audit are easy.

**Why this priority**: This is the read-only audit view (US-053). It supports P1 flows by letting users verify that recorded payments are correct, so it is P2 rather than P0.

**Independent Test**: Can be fully tested by recording payments of different types and modes, then filtering the history by each dimension and confirming the visible rows match.

**Acceptance Scenarios**:

1. **Given** recorded payments, **When** the Owner filters by customer, payment mode, payment type, or date range, **Then** only matching payments are shown.
2. **Given** a payment record, **When** the Owner inspects it, **Then** customer, date, amount, mode, type, reference number, and linked bill are displayed.
3. **Given** the payment history, **When** the Owner attempts to edit or delete a payment, **Then** no edit or delete control is available (payment history is immutable).

---

### User Story 5 - Manage Bill Status (Priority: P2)

As an Owner/Admin, I want to view a bill's detail and update its status (e.g., mark a bill OVERDUE or CANCELLED), so that billing state can be managed when payments are not the cause of the change.

**Why this priority**: The backend supports explicit bill status changes; exposing them lets owners cancel erroneous bills and flag overdue accounts. Lower priority than the core collect/generate flows.

**Independent Test**: Can be fully tested by cancelling an erroneous bill from its detail page with a confirmation step and confirming it no longer appears as billable outstanding, then marking another bill OVERDUE.

**Acceptance Scenarios**:

1. **Given** a bill detail page, **When** an Owner changes its status to one of PENDING, PARTIAL, PAID, OVERDUE, or CANCELLED, **Then** the change is saved and the list reflects the new status.
2. **Given** a bill that has payments applied, **When** the Owner attempts to cancel it, **Then** a confirmation warns that applied payments will remain recorded, and cancellation only proceeds after acknowledgment.
3. **Given** a CANCELLED bill, **When** the Owner views the Outstanding page, **Then** the cancelled bill no longer contributes to the customer's total billed.

---

### Edge Cases

- **Inactive or missing customer**: Recording a payment for an inactive/nonexistent customer is rejected with a clear message.
- **Non-positive amount**: Amount must be greater than zero; the form blocks invalid amounts.
- **Overpayment on a bill**: If the payment amount exceeds the remaining bill balance, the bill becomes PAID; the customer's displayed balance is never negative.
- **ADVANCE vs bill linkage**: ADVANCE payments are never linked to a bill; the bill selector is hidden for ADVANCE and required for BILL_PAYMENT.
- **Bill generation with no deliveries**: A customer with no DELIVERED/CASH_SALE deliveries in the period gets no bill and a per-customer explanation; other selected customers still get theirs.
- **Repeated generation for the same period**: Generating the same customer/period again creates another bill (backend allows it); the page warns before re-generating a period that already has a bill.
- **Empty selection**: Bill generation is disabled until at least one customer is selected.
- **Empty filters**: Payment and bill lists show all active records when no filters are applied.
- **Customer with no financial activity**: Outstanding shows a zero balance rather than omitting the customer.
- **Unauthorized access**: CHECKER and DELIVERY_PARTNER must not reach any payment page; navigation hides Finance and direct URL access shows the access-denied view.
- **Loading and failure states**: Lists show a loading state while fetching and a friendly empty state when there are no records; failed operations surface an error message without losing entered data.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): Frontend-only feature — no backend changes. Pages/API modules follow the established `types → api → hooks → pages` layering; existing backend routers/services/schemas are consumed as-is.
- **Role-Based Access Control** (Principle II): Payment pages are restricted to OWNER and ADMIN via navigation and route guards, matching the existing Finance menu. **Known pre-existing gap**: the backend `/payments/*` router currently does not attach an authentication dependency (observed 2026-08-01; most routers share this gap — only `reports` and `auth` routers use `get_current_user`). In this phase the client-side guards are the only enforcement; fixing backend-wide RBAC is tracked separately and is out of scope here.
- **Soft Deletes** (Principle IV): No new entities; the backend soft-deletes bills/payments and the frontend only displays active records as returned by the API.
- **Schema-Driven Contracts** (Principle V): Frontend TypeScript interfaces mirror the existing backend response/request schemas exactly; no new backend schemas are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display a payment history list with customer (code + name), payment date, amount, payment mode, payment type, reference number, and linked bill, in reverse chronological order.
- **FR-002**: The system MUST allow filtering the payment list by customer, payment mode (CASH, UPI, CARD, CHEQUE, BANK_TRANSFER), payment type (ADVANCE, BILL_PAYMENT), and date range (from/to).
- **FR-003**: Authorized users MUST be able to record a payment by selecting a customer, entering a positive amount, choosing a payment mode, choosing a payment type, and optionally entering a reference number and remarks.
- **FR-004**: For BILL_PAYMENT, the system MUST require selecting an unpaid, non-cancelled bill of the chosen customer and MUST show the bill's current balance while recording.
- **FR-005**: The system MUST reject a BILL_PAYMENT against a bill that is already PAID or CANCELLED with a clear message.
- **FR-006**: ADVANCE payments MUST NOT be linked to a bill; the bill selector MUST be hidden for ADVANCE.
- **FR-007**: After a BILL_PAYMENT is recorded, the system MUST reflect the updated bill paid amount, balance, and status (PENDING → PARTIAL → PAID) as returned by the backend.
- **FR-008**: The system MUST NOT offer edit or delete controls for recorded payments (payment history is immutable per business rules).
- **FR-009**: The system MUST display a bill list with customer, bill date, billing period, total, paid, balance, status, and due date, and MUST allow filtering by customer, status, and date range.
- **FR-010**: Authorized users MUST be able to generate a bill by selecting one or more customers and a date range (period start and end), with optional due date and remarks.
- **FR-011**: Bill generation MUST create one bill per selected customer that has DELIVERED or CASH_SALE deliveries in the period, grouped into line items by milk type with quantity, unit price, and amount.
- **FR-012**: For a selected customer with no qualifying deliveries in the period, the system MUST not create a bill and MUST explain the reason without blocking other selected customers.
- **FR-013**: Before re-generating a period that already contains a bill for the same customer, the system MUST warn the user that a duplicate bill may be created.
- **FR-014**: The system MUST display a bill detail view with line items, subtotals, due date, remarks, and the payments applied to the bill.
- **FR-015**: Authorized users MUST be able to update a bill's status to PENDING, PARTIAL, PAID, OVERDUE, or CANCELLED from the bill detail, with a confirmation step for status changes.
- **FR-016**: Before cancelling a bill that has payments applied, the system MUST warn that the applied payments remain recorded and require acknowledgment.
- **FR-017**: The system MUST display an outstanding balances view showing each customer's total billed, total paid, current balance, last bill date, and last payment date, and MUST allow narrowing to a single customer.
- **FR-018**: The outstanding balance MUST equal total billed (active, non-cancelled bills) minus total paid (active payments) for each customer.
- **FR-019**: The system MUST restrict access to all payment pages to OWNER and ADMIN: the Finance menu must not appear for CHECKER or DELIVERY_PARTNER, and direct URL access by those roles MUST show the access-denied view.
- **FR-020**: The system MUST show loading states while data loads, a friendly empty state when a list has no records, and error notifications for failed operations.

### Key Entities *(include if feature involves data)*

- **Customer Payment**: A recorded collection from a customer. Key attributes: customer, system-assigned payment date, amount, payment mode (CASH/UPI/CARD/CHEQUE/BANK_TRANSFER), payment type (ADVANCE/BILL_PAYMENT), reference number, optional linked bill, remarks. Immutable after recording.
- **Customer Bill**: A periodic statement generated from delivered quantities. Key attributes: customer, bill date, billing period, total amount, paid amount, balance, status (PENDING/PARTIAL/PAID/OVERDUE/CANCELLED), due date, remarks, line items.
- **Bill Line Item**: A bill's per-milk-type row (quantity, unit price, amount), summed into the bill total.
- **Outstanding Balance**: A derived view per customer (total billed − total paid, plus last bill date and last payment date) used for collections follow-up.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An Owner can record a customer payment in under 1 minute on first use.
- **SC-002**: 100% of BILL_PAYMENT recordings immediately reflect the correct updated bill paid amount, balance, and status in the UI.
- **SC-003**: 100% of bill generation attempts for a customer with no deliveries in the period create no bill and display a clear explanation.
- **SC-004**: An Owner can generate bills for a customer and verify them in the bill list in under 3 minutes.
- **SC-005**: For every customer, the outstanding balance displayed equals total billed minus total paid at all times.
- **SC-006**: CHECKER and DELIVERY_PARTNER cannot reach any payment page through navigation or direct URL.
- **SC-007**: No recorded payment can be edited or deleted from the interface (payment history remains immutable).

## Assumptions

- This feature is frontend-only and consumes the existing backend `/payments/*` endpoints unchanged (payment create/list/by-customer, bill generate/list/by-customer/status, outstanding by customer).
- Access is restricted to OWNER and ADMIN, matching the existing Finance menu in `frontend/src/config/permissions.ts`; CHECKER and DELIVERY_PARTNER have no access.
- The payment date is assigned by the system (server timestamp) and is not user-editable; date filters apply to the payment date.
- Payment history is immutable per documented business rules, so the UI intentionally omits edit/delete for payments even though the backend exposes update/delete endpoints.
- Bill generation calls the backend once per selected customer (the backend generates one bill per request); multi-customer selection is handled by the page looping over the selected customers.
- The outstanding view is built from the per-customer outstanding endpoint; the page iterates the active customer set (small in this deployment).
- The seed data contains no sessions, deliveries, bills, or payments; the E2E spec for this phase first creates a delivery session with DELIVERED deliveries through the existing Delivery pages, then generates a bill and records payments.
- **Known pre-existing backend gap (out of scope)**: `app/routers/payments.py` does not enforce authentication/RBAC (observed 2026-08-01; the gap spans most routers, not just payments). Client-side role guards are the only enforcement in this phase. Securing the backend is a separate tracked item.
- Existing UI patterns (DataTable, Badge, Select, Input, Button, ConfirmDialog, PageHeader, LoadingSpinner, EmptyState, role guards, react-query hooks, `noValidate` forms) are reused; no new component library is introduced.
