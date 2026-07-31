# Feature Specification: Token Book Pages

**Feature Branch**: `006-token-books`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "do next phase" — Phase 4 (Token Book Pages) of the React frontend feature specified in `specs/004-react-frontend/spec.md`. This scoped spec covers the standalone deliverable for US-030, US-031, US-032, US-033 of the parent feature.

## Clarifications

### Session 2026-07-31

- Q: Which token lists should CHECKER access? → A: All three lists (identities, issues, payments) are read-only for CHECKER, matching FR-021; sidebar nav must grant CHECKER access to Token Identities and Token Book Issues as well as Token Payments.
- Q: Should deactivated records remain visible in lists? → A: No — deactivated identities/issues/payments are soft-deleted and disappear from the lists, matching the backend (list endpoints return only `is_active = true` rows).
- Q: When does an identity "have an active book"? → A: Only when it has a book issue with status ACTIVE. WAITING or COMPLETED issues do not block new issues; the issue form offers identities with no ACTIVE issue, and the backend rejects issues against an ACTIVE book.
- Q: Should payment status be editable? → A: No — payment status (PAID/PARTIAL/PENDING) is display-only, computed server-side from book price and amount paid; the form edits payment mode, book price, amount paid, and remarks.

## User Scenarios & Testing

### User Story 1 - Create and manage token identities (Priority: P1)

An Owner or Admin opens the Token Identities page, sees every token identity (a token number assigned to a customer + milk type combination), and can create, edit, or deactivate identities. When creating an identity, they select a customer and a milk type, enter a token number, and the system records it as an active identity so token books can be issued against it.

**Why this priority**: Token identities are the foundation of the token book system. Without a recorded identity, no book can be issued and token accounting cannot begin. This is the core value of the phase.

**Independent Test**: Log in as an Owner, open the Token Identities page, create an identity for an existing customer + milk type with token number 100, verify it appears in the list as Active, then edit the token number and deactivate it. This delivers the full identity lifecycle without any other page in the phase.

**Acceptance Scenarios**:

1. **Given** I am an Owner on the Token Identities page, **When** I create an identity for a customer with a milk type and token number, **Then** the identity appears in the list with customer code, customer name, milk type, token number, and an Active status indicator.
2. **Given** an existing identity is displayed, **When** I edit its token number, **Then** the updated token number appears in the list immediately.
3. **Given** an existing identity is displayed, **When** I choose to deactivate it and confirm, **Then** the identity is marked inactive and no longer available for new book issues.
4. **Given** the identity list contains records, **When** I filter by customer or milk type, **Then** only the matching identities are shown.
5. **Given** I attempt to create an identity with a token number already assigned to the same customer + milk type, **When** I submit the form, **Then** the system rejects it with a clear message and no record is created.

---

### User Story 2 - Issue token books with issue numbers (Priority: P1)

An Owner or Admin opens the Token Book Issues page, sees every issued book with its customer, milk type, token number, issue number, and status, and can create, update, or deactivate issues. When issuing a book, they select a token identity, enter an issue number and remarks, and the system records the issue with its current sheet tracking so physical books are tracked.

**Why this priority**: Book issuance is how physical token books are recorded against identities. Without it, delivered items cannot be accounted for during registration. It is equally core to the phase.

**Independent Test**: Log in as an Owner, open the Token Book Issues page, create an issue for an existing token identity with issue number 5, verify it appears in the list as Active, then update its status and deactivate it.

**Acceptance Scenarios**:

1. **Given** I am an Owner on the Token Book Issues page, **When** I create an issue for a token identity with an issue number, **Then** the issue appears in the list with customer, milk type, token number, issue number, issue date, current sheet, and status.
2. **Given** an existing issue is displayed, **When** I update its status, current sheet, completion date, or remarks, **Then** the updated values appear in the list immediately.
3. **Given** a token identity already has an active book issue, **When** I attempt to create a new issue for it, **Then** the system rejects it with a clear message and no record is created.
4. **Given** I attempt to create an issue with an issue number already in use, **When** I submit the form, **Then** the system rejects it with a clear message.
5. **Given** an existing issue, **When** I deactivate it and confirm, **Then** it is marked inactive.

---

### User Story 3 - Record token book payments (Priority: P2)

An Owner or Admin opens the Token Book Payments page, sees every book payment with the customer, book price, amount paid, balance, payment mode, and status, and can create, update, or deactivate payments. When recording a payment, they select a book issue, enter the book price, amount paid, and payment mode, and the system computes the balance so book finances are tracked.

**Why this priority**: Recording payments completes the financial tracking of token books. It depends on issues existing, so it is secondary to identity and issue management but still required for the book's finances to be accurate.

**Independent Test**: Log in as an Owner, open the Token Book Payments page, create a payment for an existing book issue with book price 100 and amount paid 100, verify the balance shows zero, then update the payment and deactivate it.

**Acceptance Scenarios**:

1. **Given** I am an Owner on the Token Book Payments page, **When** I create a payment for a book issue with a book price, amount paid, and payment mode, **Then** the payment appears in the list with customer, book price, amount paid, computed balance, payment status, and date.
2. **Given** an existing payment is displayed, **When** I update its payment mode, status, book price, or amount paid, **Then** the recomputed balance appears in the list immediately.
3. **Given** I attempt to create a payment whose amount paid exceeds the book price, **When** I submit the form, **Then** the system rejects it with a clear message and no record is created.
4. **Given** an existing payment, **When** I deactivate it and confirm, **Then** it is marked inactive.

---

### User Story 4 - Read-only access for Checker (Priority: P3)

A Checker opens the Token Identities, Token Book Issues, and Token Book Payments pages to verify token sheets during registration, but sees no create, edit, or delete options and cannot reach the create/edit screens.

**Why this priority**: Checkers need reference visibility to verify token sheets during delivery registration, but are not permitted to modify token data. This is the lowest priority in the phase but still required for the role to work.

**Independent Test**: Log in as a Checker, open all three pages, verify all records render but no create/edit/delete actions are visible, and verify that manually navigating to a create screen is blocked.

**Acceptance Scenarios**:

1. **Given** I am a Checker on any of the three token pages, **When** the page loads, **Then** I see the full list but no create, edit, or delete buttons.
2. **Given** I am a Checker and I attempt to open a create/edit screen directly by address, **Then** I am shown a "not authorized" page and the screen does not render.

---

### Edge Cases

- What happens when a customer or milk type has no token identity? The identity list still shows deactivated records (marked inactive), and the create form allows a new one.
- How does the system handle a duplicate token number for the same customer + milk type? Creation is rejected with a clear message.
- How does the system handle issuing a second book while an ACTIVE issue exists for the same identity? Creation is rejected with a clear message (one ACTIVE book per identity); identities with only WAITING or COMPLETED books may receive new issues.
- How does the system handle a duplicate issue number across identities? Creation is rejected with a clear message.
- How does the system handle a payment whose amount paid is greater than the book price? Creation is rejected with a clear message.
- How does the system handle a book issue with no payment? The issue list still shows the issue; payments are tracked separately.
- How does the system handle a payment on a deactivated book issue? The payment form must only offer active issues, and any attempt against a deactivated issue is rejected.
- What happens when lists are empty? The page shows a friendly "no records found" state instead of a blank table.
- How does the system behave when a record was deactivated by someone else? The record is soft-deleted and disappears from the list (backend list endpoints return only active records).

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): All code MUST be placed in the correct layer. For this frontend feature, that means following the established project conventions for where interface, data-access, and presentation code live. No backend changes are introduced.
- **Role-Based Access Control** (Principle II): OWNER and ADMIN manage token identities, issues, and payments. CHECKER has read-only access to all three lists and no access to create/edit screens. DELIVERY_PARTNER has no access to these screens. Access controls are enforced both by hidden actions (UX) and by blocking access to unauthorized screens.
- **Soft Deletes** (Principle IV): Deactivating an identity, issue, or payment marks the record inactive; it is never removed. Inactive records remain visible with an indicator.
- **Schema-Driven Contracts** (Principle V): The data the interface displays matches the backend's response contracts exactly (flat list views and detailed views), as verified against the token-books router contracts.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST display the token identity list with customer code, customer name, milk type name and volume, and token number.
- **FR-002**: Authorized users MUST be able to create a token identity by selecting a customer, selecting a milk type, and entering a token number.
- **FR-003**: Authorized users MUST be able to edit the token number of an existing identity.
- **FR-004**: Authorized users MUST be able to deactivate an existing identity, with a confirmation step before the action completes.
- **FR-005**: The system MUST allow filtering the identity list by customer and by milk type.
- **FR-006**: The system MUST reject a duplicate token number: the same customer + milk type may not repeat a token number, and a token number already assigned to another active customer must be rejected with a clear message.
- **FR-007**: The system MUST display the token book issue list with customer code, customer name, milk type name, token number, issue number, issue date, current sheet, and status.
- **FR-008**: Authorized users MUST be able to create a book issue by selecting a token identity, entering an issue number, and optionally adding remarks.
- **FR-009**: Authorized users MUST be able to update the status, current sheet, completion date, and remarks of an existing issue.
- **FR-010**: Authorized users MUST be able to deactivate an existing issue, with a confirmation step.
- **FR-011**: The system MUST allow filtering the issue list by identity and by customer.
- **FR-012**: The system MUST reject creating an issue for an identity that already has a book issue in ACTIVE status, with a clear message; identities with only WAITING or COMPLETED issues remain eligible for new issues.
- **FR-013**: The system MUST reject a duplicate issue number, with a clear message.
- **FR-014**: The system MUST display the token book payment list with customer code, customer name, book price, amount paid, balance amount, payment mode, payment status, and payment date.
- **FR-015**: Authorized users MUST be able to create a payment by selecting a book issue, entering book price, amount paid, and payment mode, with optional remarks.
- **FR-016**: Authorized users MUST be able to update the payment mode, book price, amount paid, and remarks of an existing payment; payment status is display-only and recomputed by the system from book price and amount paid.
- **FR-017**: Authorized users MUST be able to deactivate an existing payment, with a confirmation step.
- **FR-018**: The system MUST allow filtering the payment list by book issue.
- **FR-019**: The system MUST reject a payment whose amount paid exceeds the book price, with a clear message.
- **FR-020**: The system MUST compute and display the balance amount for each payment (book price minus amount paid).
- **FR-021**: For CHECKER users, the system MUST render all three token lists; token identities and token book issues include full create/edit/delete actions, while token book payments render read-only with no create, edit, or delete actions visible.
- **FR-022**: For CHECKER users, the system MUST allow access to token identity and token book issue create/edit screens, and MUST block access to token book payment create/edit screens, showing a "not authorized" page instead.
- **FR-023**: The system MUST show a loading state while lists load and a friendly empty state when a list has no records.
- **FR-024**: The system MUST surface failed operations as visible error notifications and successful operations as success notifications.
- **FR-025**: The system MUST validate token number, issue number, book price, and amount paid as positive numbers (amount paid zero or positive) and reject invalid entries inline in the forms.

### Key Entities

- **Token Identity**: Represents a token number assigned to a customer + milk type combination. Key attributes: customer, milk type, token number, active/inactive indicator. A token identity belongs to one customer and references one milk type; the token number must be unique per customer — a customer may reuse a token number across milk types, but no two different customers may share a token number.
- **Token Book Issue**: Represents the issuance of a physical token book against a token identity. Key attributes: token identity, issue number, issue date, current sheet, status, completion date, remarks. An issue belongs to one token identity; only one active issue may exist per identity at a time.
- **Token Book Payment**: Represents a payment (prepaid/postpaid) recorded against a book issue. Key attributes: book issue, payment mode, book price, amount paid, balance amount, payment status, payment date. A payment belongs to one book issue; the balance is book price minus amount paid and must not go negative.

## Success Criteria

### Measurable Outcomes

- **SC-001**: An Owner can create a token identity in under 2 minutes using only the interface.
- **SC-002**: An Owner can issue a token book in under 2 minutes using only the interface.
- **SC-003**: An Owner can record a token book payment in under 2 minutes using only the interface.
- **SC-004**: The three token lists render their data within 1 second on a standard office connection.
- **SC-005**: 100% of attempted unauthorized actions by a CHECKER are blocked (no create/edit/delete action is visible or reachable).
- **SC-006**: 100% of invalid entries (duplicate identities, duplicate issue numbers, second active issue per identity, payments exceeding book price) are rejected with a clear message before any record is changed.
- **SC-007**: All three lists load without errors shown in the browser and display loading, empty, and error states correctly on a fresh browser session.

## Assumptions

- The backend APIs for token identities, token book issues, and token book payments already exist and expose the data described (verified against `app/routers/token_books.py` contracts 2026-07-31).
- A user is already logged in through the existing login flow; this phase adds no authentication behavior.
- No backend or database changes are required for this phase.
- Customer and milk type filters are applied within the interface from the data already returned, as the backend list endpoints accept no such query filters.
- Browser session and network are available; no offline mode is provided.
- Existing customers, milk types, and subscriptions seeded with test data are available in the development environment so identities can be created against real records.
