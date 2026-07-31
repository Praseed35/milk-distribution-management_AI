# Feature Specification: Subscription & Exceptions Pages

**Feature Branch**: `005-subscription-exceptions`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "implement phase 3" — Phase 3 (Subscription & Exception Pages) of the React frontend feature specified in `specs/004-react-frontend/spec.md`. This scoped spec covers the standalone deliverable for US-020, US-021, US-022 of the parent feature.

## User Scenarios & Testing

### User Story 1 - Create and manage customer subscriptions (Priority: P1)

An Owner or Admin opens the Subscriptions page, sees every customer's subscription with its route and milk type, and can create, edit, or deactivate subscriptions. When creating a subscription, they pick the customer, the milk type, and the morning/evening quantities, and the system records it as an active subscription so daily delivery planning can use it.

**Why this priority**: Subscription data drives daily delivery planning. Without the ability to record what each customer receives, deliveries cannot be planned or reconciled. This is the core value of the phase.

**Independent Test**: Log in as an Owner, open the Subscriptions page, create a subscription for an existing customer with morning quantity 2 and evening quantity 1, verify it appears in the list as Active, then edit the quantity and deactivate it. This delivers the full subscription lifecycle without any other phase.

**Acceptance Scenarios**:

1. **Given** I am an Owner on the Subscriptions page, **When** I create a subscription for a customer with a milk type and morning/evening quantities, **Then** the subscription appears in the list with customer, route, milk type, quantities, and an Active status badge.
2. **Given** an existing subscription is displayed, **When** I edit its morning or evening quantity, **Then** the updated quantities appear in the list immediately.
3. **Given** an existing subscription is displayed, **When** I choose to deactivate it and confirm, **Then** the subscription is marked inactive and no longer eligible for planning.
4. **Given** the subscriptions list contains records, **When** I filter by a customer, **Then** only that customer's subscriptions are shown.

---

### User Story 2 - Create and manage delivery exceptions (Priority: P1)

An Owner or Admin opens the Exceptions page and sees all delivery exceptions with the customer, route, exception type, and date range. They can create an exception (vacation, no milk, holiday) for a specific subscription, edit it, and deactivate it, so temporary changes are reflected in deliveries.

**Why this priority**: Exceptions are the mechanism for temporary changes to standing subscriptions (vacations, holidays, no-milk days). Without them, delivery planning would wrongly assume every subscription delivers every day. It is equally core to the phase.

**Independent Test**: Log in as an Owner, open the Exceptions page, create a VACATION exception for a subscription covering a date range, verify it appears in the list, edit the end date, and deactivate it.

**Acceptance Scenarios**:

1. **Given** I am an Owner on the Exceptions page, **When** I create an exception for a subscription with a type and date range, **Then** the exception appears in the list with customer, route, type, date range, and status.
2. **Given** an existing exception is displayed, **When** I edit its date range or reason, **Then** the updated values appear in the list immediately.
3. **Given** an exception that overlaps another exception for the same subscription, **When** I try to create it, **Then** the system rejects it with a clear message and no record is created.
4. **Given** an existing exception, **When** I deactivate it and confirm, **Then** it is marked inactive.

---

### User Story 3 - Read-only access for Checker (Priority: P2)

A Checker opens the Subscriptions and Exceptions pages to reference them during daily operations, but sees no create, edit, or delete options and cannot reach the create/edit screens.

**Why this priority**: Checkers need reference visibility to verify deliveries, but are not permitted to modify master data. This is a lower priority than the create/edit flows but still required for the role to work.

**Independent Test**: Log in as a Checker, open both pages, verify all records render but no create/edit/delete actions are visible, and verify that manually navigating to a create screen is blocked.

**Acceptance Scenarios**:

1. **Given** I am a Checker on the Subscriptions page, **When** the page loads, **Then** I see the full list but no create, edit, or delete buttons.
2. **Given** I am a Checker on the Exceptions page, **When** the page loads, **Then** I see the full list but no create, edit, or delete buttons.
3. **Given** I am a Checker and I attempt to open a create/edit screen directly by address, **Then** I am shown a "not authorized" page and the screen does not render.

---

### Edge Cases

- What happens when a customer has no active subscription? The subscription list still shows that customer's deactivated records (marked inactive), and the create form allows a new one.
- How does the system handle overlapping exception dates for the same subscription? Creation is rejected with a clear message.
- How does the system handle an exception with no end date? It is treated as a single-day/indefinite exception per the values entered; the date range must still be coherent (start date not after end date).
- What happens when an exception is created for a deactivated subscription? The system rejects it with a clear message.
- What happens when lists are empty? The page shows a friendly "no records found" state instead of a blank table.
- What happens when a subscription has zero morning and zero evening quantity? It is accepted (quantities may be zero) but the form communicates the quantities being recorded.
- How does the system behave when a subscription or exception record was deactivated by someone else? The list reflects the inactive status with a visual indicator.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): All code MUST be placed in the correct layer. For this frontend feature, that means following the established project conventions for where interface, data-access, and presentation code live. No backend changes are introduced.
- **Role-Based Access Control** (Principle II): OWNER and ADMIN manage subscriptions and exceptions. CHECKER has read-only access to both lists and no access to create/edit screens. DELIVERY_PARTNER has no access to these screens. Access controls are enforced both by hidden actions (UX) and by blocking access to unauthorized screens.
- **Soft Deletes** (Principle IV): Deactivating a subscription or exception marks the record inactive; it is never removed. Inactive records remain visible with an indicator.
- **Schema-Driven Contracts** (Principle V): The data the interface displays matches the backend's response contracts exactly (flat list views and detailed views), as verified in the parent feature's plan artifacts.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST display the subscription list with customer code, customer name, route, milk type name and volume, morning quantity, evening quantity, status, and active/inactive indicator.
- **FR-002**: Authorized users MUST be able to create a subscription by selecting a customer, selecting a milk type, and entering morning/evening quantities.
- **FR-003**: The system MUST accept a status for a new subscription, defaulting to Active.
- **FR-004**: Authorized users MUST be able to edit the morning quantity, evening quantity, status, and remarks of an existing subscription.
- **FR-005**: Authorized users MUST be able to deactivate an existing subscription, with a confirmation step before the action completes.
- **FR-006**: The system MUST allow filtering the subscription list by customer.
- **FR-007**: The system MUST display the exception list with customer code, customer name, route, exception type, start date, end date, status, and active/inactive indicator.
- **FR-008**: Authorized users MUST be able to create an exception by selecting a subscription, choosing an exception type (vacation, no milk, holiday), and entering a start date with an optional end date and reason.
- **FR-009**: Authorized users MUST be able to edit the type, dates, reason, and status of an existing exception.
- **FR-010**: Authorized users MUST be able to deactivate an existing exception, with a confirmation step.
- **FR-011**: The system MUST allow filtering the exception list by subscription.
- **FR-012**: The system MUST validate quantities as zero or positive and reject negative values inline in the form.
- **FR-013**: The system MUST reject an exception whose start date is after its end date, with a clear inline message.
- **FR-014**: The system MUST reject a new exception whose date range overlaps an existing active exception for the same subscription, with a clear message.
- **FR-015**: The system MUST reject an exception created for a deactivated subscription, with a clear message.
- **FR-016**: For CHECKER users, the system MUST render both lists read-only with no create, edit, or delete actions visible.
- **FR-017**: For CHECKER users, the system MUST block access to create/edit screens, showing a "not authorized" page instead.
- **FR-018**: The system MUST show a loading state while lists load and a friendly empty state when a list has no records.
- **FR-019**: The system MUST surface failed operations as visible error notifications and successful operations as success notifications.

### Key Entities

- **Subscription**: Represents a customer's standing order for a specific milk type. Key attributes: customer, milk type, morning quantity, evening quantity, status (Active/Inactive), remarks. A subscription belongs to one customer and references one milk type.
- **Delivery Exception**: Represents a temporary change to a subscription (vacation, no milk, holiday) over a date range. Key attributes: subscription, exception type, start date, end date, reason, status. A delivery exception belongs to one subscription.

## Success Criteria

### Measurable Outcomes

- **SC-001**: An Owner can create a subscription in under 2 minutes using only the interface.
- **SC-002**: An Owner can create an exception in under 2 minutes using only the interface.
- **SC-003**: The subscription and exception lists render their data within 1 second on a standard office connection.
- **SC-004**: 100% of attempted unauthorized actions by a CHECKER are blocked (no create/edit/delete action is visible or reachable).
- **SC-005**: 100% of invalid entries (negative quantities, reversed date ranges, overlapping exceptions, exceptions on inactive subscriptions) are rejected with a clear message before any record is changed.
- **SC-006**: Both lists load without errors shown in the browser and display loading, empty, and error states correctly on a fresh browser session.

## Assumptions

- The backend APIs for subscriptions and delivery exceptions already exist and expose the data described (parent feature `004-react-frontend`, plan artifacts verified 2026-07-31).
- A user is already logged in through the existing login flow; this phase adds no authentication behavior.
- No backend or database changes are required for this phase.
- Route-level filtering is done within the interface from the data already returned, as the backend does not accept such filters (documented backend gap).
- Browser session and network are available; no offline mode is provided.
- Existing subscriptions and exceptions seeded with test data are available in the development environment.
