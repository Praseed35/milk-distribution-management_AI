# Chapter 5 – Delivery and Reconciliation Workflow

---

# 1. Introduction

The Delivery and Reconciliation Workflow is the core business process of the Milk Distribution ERP. It manages the complete operational cycle from generating the daily delivery schedule until the route is successfully reconciled and closed.

Unlike traditional delivery systems, this ERP separates **delivery**, **token collection**, **payment**, and **reconciliation** into independent processes. This provides flexibility while ensuring that every liter of dispatched milk is fully accounted for.

---

# 2. Daily Delivery Generation

At the beginning of each day, the ERP automatically generates the delivery schedule based on:

* Customer subscriptions
* Approved delivery exceptions
* Customer status
* Delivery shift (Morning/Evening)

Each route receives its own customer delivery list.

---

# 3. Milk Dispatch

Before the route begins, milk is issued to the Delivery Partner.

The dispatch record contains:

* Route
* Delivery Partner
* Dispatch Date
* Total Milk Loaded (Liters)

Example:

```text id="wf001"
Route 1

Milk Loaded : 110 Liters
```

This dispatched quantity becomes the reference for end-of-day reconciliation.

---

# 4. Delivery Partner Operations

The Delivery Partner performs only physical operations.

Responsibilities include:

* Deliver milk
* Collect token sheets
* Collect cash
* Receive customer requests
* Return remaining milk

The Delivery Partner does **not** register token sheets or perform reconciliation within the ERP.

---

# 5. Customer Delivery Scenarios

The ERP supports different real-world situations.

### Normal Delivery

The customer receives milk and provides the appropriate token sheet.

---

### Pending Token

The customer receives milk but does not provide a token sheet.

The pending token may be submitted during any future shift or on any future day.

Milk delivery continues normally.

---

### Cash Sale

Milk is sold without using a token book.

Cash is collected by the Delivery Partner and later entered into the ERP by the Checker.

---

### Extra Milk

A customer may request additional milk during delivery.

If supplied, the actual delivered quantity is recorded accordingly.

---

### Unplanned Delivery

Sometimes a customer is not included in today's delivery list but still receives milk.

Example:

Yesterday the customer requested "No Milk Tomorrow."

Today's delivery schedule excludes the customer.

During delivery, the customer changes the decision and requests milk.

The Delivery Partner supplies the milk.

During registration, the Checker adds this customer using the **Add Unplanned Delivery** option.

The original delivery schedule remains unchanged for audit purposes.

---

# 6. Return to Office

After completing the route, the Delivery Partner returns with:

* Collected token sheets
* Cash collected
* Remaining milk
* Customer requests (if any)

The physical delivery process ends here.

All remaining work is handled by the Checker.

---

# 7. Checker Registration

The Checker opens today's delivery route.

The ERP displays every customer who was scheduled for delivery.

For each customer, the Checker selects one registration method.

### Token Sheet

Milk delivered.

Token received.

The Checker enters the sheet number.

---

### Pending Token

Milk delivered.

Token not received.

The ERP records a pending token entry.

---

### Cash Sale

Milk delivered.

Customer paid using cash.

---

### Not Delivered

Milk was scheduled but not delivered.

Examples include:

* Customer unavailable
* Customer refused milk
* Delivery skipped

---

### Add Unplanned Delivery

If milk was delivered to a customer who was not included in today's schedule, the Checker may manually add the customer.

The ERP allows searching by:

* Customer Name
* Customer Code
* Token Number
* Mobile Number

After selecting the customer, the Checker records:

* Milk Type
* Quantity
* Shift
* Registration Method
* Reason

The delivery is marked as **Unplanned** and included in reconciliation.

---

# 8. Automatic Validation

Whenever a token sheet is registered, the ERP automatically validates:

* Customer
* Token Number
* Milk Type
* Active Token Book
* Sheet Sequence
* Duplicate Sheet
* Previous Book Completion

If any irregularity is found, the ERP displays a warning.

The Checker may review the warning and continue if appropriate.

This allows the system to support real business situations while maintaining complete records.

---

# 9. Daily Reconciliation

After all customer registrations are complete, the Checker enters:

* Total Cash Sales (Liters)
* Total Returned Milk (Liters)

The ERP automatically calculates the total milk represented by all registered token sheets.

The reconciliation formula is:

```text id="wf002"
Loaded Milk

=

Token Milk Registered

+

Cash Sales

+

Returned Milk
```

Example:

```text id="wf003"
Loaded Milk          : 110 L

Token Registered     : 95 L

Cash Sales           : 8 L

Returned Milk        : 7 L

----------------------------

Total                : 110 L

Status               : Balanced
```

If the quantities match, the route is balanced.

---

# 10. Correction Mode

If reconciliation fails, the ERP displays the difference.

Example:

```text id="wf004"
Loaded Milk          : 110 L

Token Registered     : 94 L

Cash Sales           : 8 L

Returned Milk        : 7 L

Difference           : 1 L
```

The Checker then verifies the register with the Delivery Partner.

Possible questions include:

* Was any token sheet forgotten?
* Was a customer missed?
* Was cash collected but not recorded?
* Was additional milk delivered?
* Was returned milk entered incorrectly?

The Checker may edit:

* Token registrations
* Pending entries
* Cash sales
* Returned milk
* Unplanned deliveries

The ERP recalculates the reconciliation after every correction.

---

# 11. Route Closing

A delivery route can be closed only when:

* Every customer has been processed.
* Reconciliation is balanced.
* Cash sales are entered.
* Returned milk is entered.

After closing:

* The Token Ledger is updated.
* Daily reports are generated.
* The route becomes read-only.

Only the Owner can reopen a closed route.

---

# 12. Editing Previous Sessions

The Owner can edit previous delivery sessions for error correction.

### Common Scenario

A customer says "no milk today" but the delivery partner forgets and delivers milk anyway. The next day, the customer complains and wants their token sheet back.

### Token Sheet Return Process

1. **Owner reopens** the closed session from the previous day.
2. **Owner finds** the customer's delivery record.
3. **Owner changes** delivery status from `DELIVERED` to `NOT_DELIVERED`.
4. **Owner selects** "Return Token Sheet" option.
5. **System removes** the token registration for that delivery.
6. **System decrements** `current_sheet` on the token book issue by 1.
7. **Customer can now reuse** that same sheet in future deliveries.
8. **Session is re-balanced** and closed again.

### Business Rules for Editing

* Only the Owner can reopen closed sessions.
* All edits must include a reason (mandatory).
* All edits are permanently logged in the `session_edits` table.
* Original delivery records are never deleted.
* Reconciliation is automatically recalculated after edits.
* Sessions must be re-balanced before being closed again.

### Token Sheet Return Mechanics

When a token sheet is returned:
- The `current_sheet` count on the `token_book_issue` is decremented by 1
- This effectively "returns" the sheet to the customer
- The customer can use the same sheet number in future deliveries
- The sheet becomes available for reuse

---

# 13. Business Rules

The Delivery and Reconciliation Workflow follows these rules:

* Delivery and token collection are independent.
* Pending tokens may be submitted during any future shift or date.
* Token balances are maintained separately for each Token Identity.
* Customers may use the same token book across different shifts.
* Different milk types are reconciled independently.
* Token book payment is independent of daily token collection.
* Unplanned deliveries are permitted for existing customers.
* The original delivery schedule is never modified after generation.
* Only balanced routes may be closed.
* **Owner can edit previous sessions for error correction.**
* **Token sheets can be returned when delivery is corrected.**
* **All edits are permanently logged for audit purposes.**

---

# 14. Reports Generated

After successful route closure, the ERP generates:

* Delivery Report
* Route Summary
* Token Collection Report
* Pending Token Report
* Cash Sales Report
* Returned Milk Report
* Daily Reconciliation Report
* **Session Edit History** (if any edits were made)

These reports provide a complete operational record for the day.

---

# 15. Conclusion

The Delivery and Reconciliation Workflow reflects the real operational practices of a milk distribution business. By separating delivery, token collection, payment, and reconciliation into independent but connected processes, the ERP minimizes manual work while ensuring complete accountability.

The workflow supports pending tokens, unplanned deliveries, cash sales, customer requests, automatic reconciliation, and **editing previous sessions with token sheet returns**, allowing the business to operate flexibly without losing accuracy or auditability. Every liter of dispatched milk is accounted for before a route is closed, providing a reliable foundation for token accounting, financial management, and business reporting.
