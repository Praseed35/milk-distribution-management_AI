# Chapter 6 – Shift Management and Delivery Scheduling

---

# 1. Introduction

Milk distribution businesses operate on fixed delivery shifts. Some customers require milk only in the morning, some only in the evening, while others require milk in both shifts.

The Milk Distribution ERP provides a flexible scheduling system that supports multiple delivery shifts, different milk quantities, multiple milk types, temporary delivery changes, and flexible token collection.

One of the core principles of the ERP is that **delivery timing and token collection are independent**. A customer may receive milk in one shift but submit the corresponding token sheet in another shift or even on a later day.

---

# 2. Delivery Shifts

Version 1 of the ERP supports two delivery shifts.

* Morning Shift
* Evening Shift

The timing of each shift is configurable by the business.

Example:

```text id="sh001"
Morning Shift

05:00 AM – 09:00 AM

-------------------------

Evening Shift

04:00 PM – 08:00 PM
```

The architecture also allows additional shifts in future without changing the database structure.

---

# 3. Customer Subscription

Every customer subscription is maintained separately for each shift.

A customer may subscribe to:

* Morning only
* Evening only
* Both shifts

Each shift can have different milk quantities.

Example

| Customer | Morning | Evening |
| -------- | ------: | ------: |
| Hashim   |     1 L |       0 |
| Kumar    |     1 L |     1 L |
| Ravi     |       0 |  500 ml |

This flexibility allows the ERP to generate accurate delivery schedules.

---

# 4. Multiple Milk Types

A customer may purchase multiple milk types simultaneously.

Example

| Milk Type | Morning | Evening |
| --------- | ------: | ------: |
| 1 Liter   |       1 |       1 |
| 500 ml    |       1 |       0 |

Total Morning Requirement

```text id="sh002"
1 Liter

+

500 ml

=

1.5 Liters
```

Each milk type is managed independently throughout delivery, token accounting, and reconciliation.

---

# 5. Delivery Schedule Generation

At the beginning of every day, the ERP automatically generates delivery schedules.

The system considers:

* Active customers
* Customer subscriptions
* Delivery exceptions
* Customer status
* Delivery shift

The generated schedule contains:

* Customer
* Route
* Milk Type
* Planned Quantity
* Shift
* Delivery Notes

This schedule becomes the official delivery plan for the day.

---

# 6. Delivery Exceptions

Customers frequently request temporary changes.

Examples include:

* No milk tomorrow
* Extra milk tomorrow
* Vacation
* Resume delivery
* Morning only
* Evening only
* Temporary quantity changes

Approved delivery exceptions override the normal subscription only for the specified dates.

After the exception period ends, the original subscription automatically becomes active again.

---

# 7. Shift Independence

Each shift operates independently.

Morning delivery does not affect evening delivery.

Example

Morning

```text id="sh003"
Delivered

1 Liter
```

Evening

```text id="sh004"
No Delivery
```

Both deliveries are processed separately.

Each shift has its own:

* Delivery Schedule
* Milk Dispatch
* Reconciliation
* Route Closing

---

# 8. Token Collection Independence

The ERP separates token collection from delivery timing.

Examples:

Morning milk → Morning token

Morning milk → Evening token

Morning milk → Next day's token

Evening milk → Morning token

Multiple pending tokens submitted together

All these situations are supported.

The ERP automatically updates the Token Ledger when pending tokens are received.

---

# 9. Same Token Book Across Shifts

A customer may use the same token book for both shifts.

Example

Morning

```text id="sh005"
Book 1205

Sheet 11
```

Evening

```text id="sh006"
Book 1205

Sheet 12
```

This is considered normal.

The ERP validates only the sheet sequence.

---

# 10. Multiple Token Books

Customers may own multiple token books.

Example

| Token Number | Milk Type |
| ------------ | --------- |
| 1205         | 1 Liter   |
| 1205         | 500 ml    |

Although both books use the same token number, they represent different Token Identities.

The ERP maintains independent balances for each milk type.

Example

1 Liter Book

Pending

```text id="sh007"
3 Sheets
```

500 ml Book

Pending

```text id="sh008"
4 Sheets
```

If the customer submits seven **500 ml** token sheets, only the **500 ml** pending balance is cleared.

The **1 Liter** pending balance remains unchanged.

Different milk types never settle each other's balances.

---

# 11. Pending Token Settlement

Customers may receive milk without immediately providing token sheets.

The ERP allows pending tokens to be submitted during any future shift or on any future day.

Example

Day 1

Milk Delivered

Token Not Received

↓

Pending Created

Day 3

Customer submits the missing token.

↓

Pending Cleared

The Token Ledger automatically updates the outstanding balance.

---

# 12. Advance Token Collection

Customers may provide extra token sheets beyond today's requirement.

Example

Today's Delivery

```text id="sh009"
1 Liter
```

Customer submits

```text id="sh010"
3 Token Sheets
```

Result

Today's delivery is settled.

The remaining two token sheets become **Advance Token Credit**.

Future deliveries automatically consume this available credit.

---

# 13. Unplanned Deliveries

Sometimes a customer who was not included in today's delivery schedule still receives milk.

Example

Yesterday

Customer requested

"No Milk Tomorrow."

Today's schedule excludes the customer.

During delivery, the customer changes the decision and requests milk.

The Delivery Partner supplies the milk.

During token registration, the Checker uses **Add Unplanned Delivery**.

The ERP allows searching by:

* Customer Name
* Customer Code
* Token Number
* Mobile Number

The delivery becomes part of today's reconciliation while the original schedule remains unchanged.

---

# 14. Daily Dispatch and Reconciliation

Each shift begins with milk dispatch.

Example

Morning Dispatch

```text id="sh011"
Loaded

110 Liters
```

Evening Dispatch

```text id="sh012"
Loaded

85 Liters
```

Each shift is reconciled independently.

Formula

```text id="sh013"
Loaded Milk

=

Token Milk Registered

+

Cash Sales

+

Returned Milk
```

Only balanced shifts can be closed.

---

# 15. Business Rules

The Shift Management module follows these rules.

* Customers may receive milk in one or both shifts.
* Different quantities may be supplied in different shifts.
* Customers may own multiple token books.
* The same token number may exist for different milk types.
* Token balances are maintained separately for each Token Identity.
* The same token book may be used across multiple shifts.
* Token collection is independent of delivery timing.
* Pending tokens may be settled during any future shift.
* Advance token credit remains available until consumed.
* Delivery exceptions temporarily override subscriptions.
* Unplanned deliveries are allowed for existing customers.
* Every shift is reconciled independently.

---

# 16. Future Enhancements

The scheduling architecture supports future expansion.

Possible enhancements include:

* Additional delivery shifts
* Weekly delivery patterns
* Holiday calendars
* Festival schedules
* Route optimization
* GPS tracking
* Delivery Partner mobile application
* Customer self-service scheduling

These features can be added without redesigning the existing scheduling system.

---

# 17. Conclusion

The Shift Management and Delivery Scheduling module provides the flexibility required for real-world milk distribution. By separating subscriptions, delivery planning, token collection, and reconciliation into independent processes, the ERP accurately reflects the daily operations of the business.

The system supports multiple shifts, multiple milk types, pending token settlement, advance token credits, unplanned deliveries, and independent reconciliation while maintaining complete business history and ensuring that every delivery is accurately recorded and accounted for.
