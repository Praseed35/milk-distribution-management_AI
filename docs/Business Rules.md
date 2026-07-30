# Chapter 7 – Business Rules

---

> **Note:** This document describes all planned business rules. As of July 2026, only the following rules are implemented: Customer rules, Route rules, basic Token Book rules. See the Implementation Status section in Project Overview for details.

---

# 1. Introduction

Business Rules define the operational logic that governs how the Milk Distribution ERP behaves. These rules ensure that every module follows the actual workflow of the milk distribution business while maintaining data consistency, operational flexibility, and financial accountability.

Unlike validation rules, which verify whether user input is correct, business rules describe **how the business operates** and **how the ERP should respond** to different situations.

---

# 2. General Business Principles

The ERP follows these core principles:

* Delivery and payment are independent.
* Delivery and token collection are independent.
* Token book payment is independent of token usage.
* Every business transaction must be traceable.
* Historical data must never be lost.
* Manual overrides are allowed only when authorized.
* Every delivery route must be reconciled before closure.

---

# 3. Customer Rules

The ERP enforces the following customer rules:

* Every customer must belong to exactly one route.
* Every customer must have a unique customer code.
* Primary phone numbers must be unique.
* A customer may have multiple subscriptions.
* A customer may subscribe to multiple milk types.
* A customer may receive milk in one or both shifts.
* Customers may be temporarily inactive without deleting their history.

---

# 4. Route Rules

* Every customer belongs to one delivery route.
* Only active routes can receive new customers.
* One route may contain many customers.
* A delivery route is generated daily.
* A route cannot be closed until reconciliation is balanced.

---

# 5. Subscription Rules

* Every subscription belongs to one customer.
* Morning and evening quantities are maintained separately.
* Multiple milk types are allowed.
* Delivery Exceptions temporarily override subscriptions.
* Expired exceptions automatically restore the original subscription.

---

# 6. Token Book Rules

The Token Management System follows these rules.

* One customer may own multiple token books.
* Multiple milk types may share the same token number.
* Each milk type creates a separate Token Identity.
* Pending balances are maintained separately for each Token Identity.
* Half-liter tokens cannot settle one-liter balances.
* One-liter tokens cannot settle half-liter balances.
* Every Token Book has only one active status at a time.
* Completed books cannot accept new token registrations.

---

# 7. Token Collection Rules

* Customers are not required to provide token sheets during delivery.
* Pending tokens may be submitted during any future shift.
* Pending tokens may be submitted on any future day.
* Customers may submit multiple pending token sheets together.
* Customers may submit advance token sheets.
* Advance token credits remain available until consumed.
* The Checker decides whether non-sequential token sheets should be accepted.
* **Token sheets may be returned if delivery is corrected from DELIVERED to NOT_DELIVERED.**
* **Returned token sheets become available for reuse in future deliveries.**
* **Token sheet return decrements the `current_sheet` count on the token book issue.**
* **Non-sequential token sheets are allowed (system shows WARNING).**
* **Customers may provide sheets out of order (system shows WARNING).**
* **Multiple token books can be ACTIVE simultaneously.**
* **New book can be used before old book is finished (system shows WARNING).**

---

# 8. Token Sheet Warning Rules

The ERP includes a warning system for token sheet edge cases:

### Non-sequential Sheet Warnings

* When a sheet number skips ahead, system shows WARNING.
* When a sheet is provided out of order, system shows WARNING.
* Checker must acknowledge warning before proceeding.
* All warnings are logged for audit purposes.
* Checker has final decision on whether to accept.

### New Book Usage Warnings

* When new book is used before old book finishes, system shows WARNING.
* Warning shows remaining sheets in old book.
* Checker must acknowledge warning before proceeding.
* Both books remain ACTIVE until explicitly completed.
* System tracks which book each sheet came from.

### Warning Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| INFO | Informational only | No action needed |
| WARNING | Requires acknowledgment | Checker must acknowledge |
| ERROR | Cannot proceed | Registration blocked |

---

# 9. Delivery Rules

The ERP supports the following delivery situations:

* Normal delivery
* Pending token delivery
* Cash sale
* Extra milk delivery
* Not delivered
* Unplanned delivery

The original delivery schedule is never modified after generation.

Unplanned deliveries are recorded separately while remaining part of daily reconciliation.

---

# 10. Session Editing Rules

The ERP supports editing previous delivery sessions for error correction:

* **Only the Owner** can reopen closed sessions and edit previous deliveries.
* **Checker** can edit sessions that are still in `COMPLETED` status (same day, before closing).
* **Delivery Partner** cannot edit any records.
* All edits must include a **reason** (mandatory field).
* All edits are **permanently logged** in the `session_edits` table.
* Original delivery records are **never deleted** (soft update with audit trail).
* **Token sheets can be returned** when delivery status changes from DELIVERED to NOT_DELIVERED.
* **Token sheet return** decrements `current_sheet` on the token book issue.
* **Returned sheets** become available for reuse in future deliveries.
* After editing, reconciliation is **automatically recalculated**.
* Sessions must be **re-balanced** before being closed again.
* **Audit trail** tracks all edits including old values, new values, and reasons.

### Token Sheet Return Process

1. Owner reopens closed session.
2. Owner edits delivery record: changes status from DELIVERED to NOT_DELIVERED.
3. Owner selects "Return Token Sheet" option.
4. System removes token registration for that delivery.
5. System decrements `current_sheet` on token book issue by 1.
6. Customer can now reuse that same sheet in future deliveries.
7. Session is re-balanced and closed again.

---

# 11. Reconciliation Rules

Every delivery route must satisfy the following equation:

```text id="br001"
Loaded Milk

=

Token Milk Registered

+

Cash Sales

+

Returned Milk
```

Business Rules:

* Reconciliation is performed after token registration.
* The ERP calculates Token Milk automatically.
* The Checker enters only:

  * Cash Sales (Liters)
  * Returned Milk (Liters)
* Routes remain editable until balanced.
* Only balanced routes can be closed.
* **After editing previous sessions, reconciliation is automatically recalculated.**
* **Sessions must be re-balanced before being closed again.**

---

# 12. Payment Rules

* Token Book payment is independent of delivery.
* Token Book payment is independent of token collection.
* Both Prepaid and Postpaid books are supported.
* Partial payments are allowed.
* Outstanding balances are updated automatically.
* Every payment is permanently recorded.

---

# 13. Reporting Rules

* Reports are generated only from recorded transactions.
* Closed routes become historical records.
* Historical reports cannot be modified.
* Business analytics use finalized transactional data.

---

# 14. Audit Rules

The ERP records every important business operation.

Examples include:

* Customer Created
* Subscription Modified
* Token Book Issued
* Token Registered
* Pending Created
* Pending Cleared
* Cash Sale Recorded
* Unplanned Delivery Added
* Route Closed
* Route Reopened
* **Session Edited (with old/new values)**
* **Token Sheet Returned**
* **Delivery Status Changed**
* **Non-sequential Sheet Warning**
* **New Book Usage Warning**

Audit records cannot be deleted through normal business operations.

---

# 15. Administrative Rules

The Owner has complete administrative control.

Examples:

* Reopen closed routes.
* **Edit previous delivery sessions.**
* **Return token sheets to customers.**
* Issue token books.
* Manage users.
* Configure milk types.
* View all reports.
* View session edit history.
* **View token sheet warnings.**

The Checker performs daily operational work.

The Delivery Partner performs only physical delivery activities.

---

# 16. Future Business Rules

The ERP architecture supports future business requirements such as:

* Multiple branches
* Multiple companies
* Digital token books
* QR code token verification
* Online payments
* Customer mobile applications
* AI-assisted business recommendations

These features can be added without changing the existing business rule framework.

---

# 17. Conclusion

The Business Rules defined in this chapter establish the operational foundation of the Milk Distribution ERP. By separating delivery, token accounting, payments, reconciliation, and reporting into independent but connected business processes, the ERP accurately models real-world milk distribution while maintaining flexibility, consistency, and complete business traceability.
