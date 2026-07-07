# Chapter 7 – Business Rules

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

---

# 8. Delivery Rules

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

# 9. Reconciliation Rules

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

---

# 10. Payment Rules

* Token Book payment is independent of delivery.
* Token Book payment is independent of token collection.
* Both Prepaid and Postpaid books are supported.
* Partial payments are allowed.
* Outstanding balances are updated automatically.
* Every payment is permanently recorded.

---

# 11. Reporting Rules

* Reports are generated only from recorded transactions.
* Closed routes become historical records.
* Historical reports cannot be modified.
* Business analytics use finalized transactional data.

---

# 12. Audit Rules

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

Audit records cannot be deleted through normal business operations.

---

# 13. Administrative Rules

The Owner has complete administrative control.

Examples:

* Reopen closed routes.
* Issue token books.
* Manage users.
* Configure milk types.
* View all reports.

The Checker performs daily operational work.

The Delivery Partner performs only physical delivery activities.

---

# 14. Future Business Rules

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

# 15. Conclusion

The Business Rules defined in this chapter establish the operational foundation of the Milk Distribution ERP. By separating delivery, token accounting, payments, reconciliation, and reporting into independent but connected business processes, the ERP accurately models real-world milk distribution while maintaining flexibility, consistency, and complete business traceability.
