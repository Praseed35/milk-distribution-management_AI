# Chapter 3 – Database Design

---

> **Note:** This document describes the complete planned database schema. As of July 2026, the following tables are implemented: users, customers, routes, milk_types, employees, subscriptions, delivery_exceptions. See the Implementation Status section in Project Overview for details.

---

# 1. Introduction

The database is the foundation of the Milk Distribution ERP. Every business operation performed within the ERP is stored in a structured relational database designed specifically for the workflow of a milk distribution company.

The database is designed using Third Normal Form (3NF) to eliminate redundancy while preserving complete business history.

Unlike generic ERP systems, this database models actual business operations such as customer subscriptions, token books, milk delivery, token collection, reconciliation, and payment management.

The primary objectives of the database are:

* Maintain data integrity.
* Preserve complete business history.
* Support daily reconciliation.
* Minimize redundant data.
* Provide scalability for future requirements.
* Improve reporting and business analytics.

---

# 2. Database Design Principles

The database follows the principles below.

---

## Principle 1 – Business Driven Design

Tables represent real business entities rather than simple CRUD objects.

Examples:

* Customer
* Route
* Token Identity
* Token Book Issue
* Daily Delivery
* Token Ledger

---

## Principle 2 – Database Normalization

Master information is stored only once.

Examples include:

* Routes
* Milk Types
* Customers
* Users

All transactional tables reference master data using foreign keys.

---

## Principle 3 – Historical Preservation

Business history should never be lost.

Master tables use soft delete through:

* is_active

Business transaction tables are never deleted.

Examples:

* Deliveries
* Token Ledger
* Payments

---

## Principle 4 – Auditability

Every important operation should be traceable.

Examples:

* Customer Created
* Subscription Changed
* Token Book Issued
* Token Registered
* Payment Collected
* Manual Adjustment

---

## Principle 5 – Scalability

The schema supports future additions without major redesign.

Future features include:

* Mobile Application
* QR Code Token Books
* Online Payments
* Multi-Branch Support
* Business Intelligence

---

# 3. Database Domains

The database is divided into independent business domains.

```text id="vnh0x7"
Authentication

↓

Master Data

↓

Delivery Planning

↓

Daily Operations

↓

Token Accounting

↓

Finance

↓

Reporting
```

Each domain is responsible for one area of the business.

---

# 4. Master Data Domain

Master data changes infrequently and forms the foundation of the ERP.

---

## Users

Purpose

Stores ERP users.

Fields

* id
* username
* password_hash
* role
* is_active
* created_at
* updated_at

---

## Routes

Purpose

Stores delivery routes.

Fields

* id
* route_code
* route_name
* description
* is_active
* created_at
* updated_at

Relationship

One Route

↓

Many Customers

---

## Customers

Purpose

Stores customer information.

Fields

* id
* customer_code
* customer_name
* primary_phone
* alternate_phone
* address
* route_id
* remarks
* is_active
* created_at
* updated_at

Relationship

Each customer belongs to one delivery route.

---

## Milk Types

Purpose

Stores all supported milk products.

Fields

* id
* milk_name
* volume_ml
* description
* is_active

Examples

| Milk Type | Volume |
| --------- | -----: |
| 250 ml    |    250 |
| 500 ml    |    500 |
| 1 L       |   1000 |
| 2 L       |   2000 |

Future milk products require only a new record.

---

# 5. Delivery Planning Domain

This domain determines what milk each customer should receive.

---

## Customer Subscription

Stores the customer's normal daily requirement.

Fields

* id
* customer_id
* milk_type_id
* morning_quantity
* evening_quantity
* effective_from
* effective_to
* is_active
* created_at

Example

| Customer | Milk Type | Morning | Evening |
| -------- | --------- | ------: | ------: |
| Hashim   | 1 L       |       1 |       0 |
| Hashim   | 500 ml    |       1 |       1 |

A customer may have multiple subscriptions.

---

## Delivery Exception

Stores temporary modifications.

Examples

* Vacation
* Extra milk
* No milk
* Morning only
* Evening only

Fields

* id
* customer_id
* milk_type_id
* start_date
* end_date
* morning_quantity
* evening_quantity
* reason
* remarks
* created_by

Delivery exceptions temporarily override subscriptions.

---

# 6. Daily Operations Domain

This domain records daily business activities.

---

## Milk Dispatch

Represents milk issued to a delivery partner before starting the route.

Fields

* id
* route_id
* delivery_partner_id
* dispatch_date
* total_milk_loaded_liters
* created_by
* created_at

This record is the starting point for daily reconciliation.

---

## Daily Delivery

### Purpose

The **Daily Delivery** table records every milk delivery performed on a particular day.

Most deliveries are automatically generated from customer subscriptions and approved delivery exceptions.

However, real-world operations sometimes require deliveries that were not originally planned. The ERP allows these deliveries to be recorded while preserving the original delivery schedule.

The Daily Delivery table therefore represents **what was actually delivered**, regardless of the original plan.

---

### Delivery Types

The ERP supports two delivery sources.

#### Planned Delivery

Automatically generated from:

* Customer Subscription
* Approved Delivery Exceptions

Examples:

* Regular daily delivery
* Approved extra milk
* Vacation schedule
* Temporary quantity change

---

#### Unplanned Delivery

Manually added during today's token registration.

Examples:

* Customer cancelled yesterday but requested milk during delivery.
* Customer unexpectedly requested additional milk.
* Emergency delivery approved by the office.
* Delivery partner supplied milk outside the original schedule.

The original delivery schedule is preserved for audit purposes.

---

### Fields

* id
* customer_id
* delivery_date
* shift
* milk_type_id
* planned_quantity
* delivered_quantity
* delivery_status
* delivery_source
* added_by
* added_reason
* remarks
* created_at
* updated_at

---

### Field Description

#### planned_quantity

The quantity originally planned by the ERP.

Example

Customer Subscription

Morning

```text
1 Liter
```

planned_quantity

```text
1
```

---

#### delivered_quantity

The quantity actually delivered.

Examples

Normal Delivery

```text
planned_quantity = 1

delivered_quantity = 1
```

Extra Delivery

```text
planned_quantity = 1

delivered_quantity = 2
```

Customer Not Delivered

```text
planned_quantity = 1

delivered_quantity = 0
```

Unplanned Delivery

```text
planned_quantity = 0

delivered_quantity = 1
```

---

### Delivery Status

The ERP records the final outcome of each delivery.

Supported values:

* Delivered
* Pending Token
* Cash Sale
* Not Delivered
* Cancelled

Meaning:

**Delivered**

Milk delivered and token received.

---

**Pending Token**

Milk delivered.

Token not received.

Customer will provide the token later.

---

**Cash Sale**

Milk sold without using a token book.

---

**Not Delivered**

Milk was planned but not delivered.

Examples:

* Customer unavailable
* Delivery skipped
* Customer refused delivery

---

**Cancelled**

Delivery cancelled before dispatch due to an approved Delivery Exception.

---

### Delivery Source

Every delivery is classified as:

* Planned
* Unplanned

**Planned**

Generated automatically by the ERP.

**Unplanned**

Added manually by the Checker because milk was delivered outside the generated schedule.

---

### Unplanned Delivery Registration

During token registration, the Checker may discover that milk was delivered to an existing customer who does not appear in today's delivery list.

Example:

Yesterday the customer requested:

> "No milk tomorrow."

The ERP therefore excluded the customer from today's delivery schedule.

During delivery, the customer changed the decision and requested milk.

The delivery partner supplied the milk.

The Checker clicks **Add Unplanned Delivery**.

The ERP allows searching by:

* Customer Name
* Customer Code
* Token Number
* Mobile Number

After selecting the customer, the Checker records:

* Milk Type
* Delivered Quantity
* Shift
* Registration Type
* Reason

The delivery is immediately included in today's reconciliation while the original delivery schedule remains unchanged.

---

### Business Rules

* Every delivery belongs to exactly one customer.
* Every delivery belongs to one milk type.
* Every delivery belongs to one shift.
* Planned deliveries are generated automatically.
* Unplanned deliveries can only be added by the Checker or Owner.
* Only existing customers may be added as Unplanned Deliveries.
* Every Unplanned Delivery requires a reason.
* Planned and Unplanned deliveries participate equally in reconciliation.
* The original delivery schedule is never modified after generation.

---

### Examples

#### Example 1 – Normal Delivery

| Field              | Value     |
| ------------------ | --------- |
| planned_quantity   | 1         |
| delivered_quantity | 1         |
| delivery_status    | Delivered |
| delivery_source    | Planned   |

---

#### Example 2 – Pending Token

| Field              | Value         |
| ------------------ | ------------- |
| planned_quantity   | 1             |
| delivered_quantity | 1             |
| delivery_status    | Pending Token |
| delivery_source    | Planned       |

---

#### Example 3 – Cash Sale

| Field              | Value     |
| ------------------ | --------- |
| planned_quantity   | 0         |
| delivered_quantity | 1         |
| delivery_status    | Cash Sale |
| delivery_source    | Unplanned |

---

#### Example 4 – Customer Changed Decision

Yesterday:

Customer requested **No Milk**.

Today's schedule:

```text
planned_quantity = 0
```

During delivery:

Customer requested milk.

The delivery partner supplied 1 liter.

| Field              | Value     |
| ------------------ | --------- |
| planned_quantity   | 0         |
| delivered_quantity | 1         |
| delivery_status    | Delivered |
| delivery_source    | Unplanned |

---

#### Example 5 – Customer Not Delivered

| Field              | Value         |
| ------------------ | ------------- |
| planned_quantity   | 1             |
| delivered_quantity | 0             |
| delivery_status    | Not Delivered |
| delivery_source    | Planned       |


## Customer Requests

Stores requests received from customers.

Examples

* Extra milk tomorrow
* Stop milk
* Resume milk
* Vacation
* Address change

Fields

* id
* customer_id
* request_type
* request_date
* remarks
* approved_by
* status

---

## Daily Route Closing

Stores the final reconciliation result.

Fields

* id
* dispatch_id
* total_token_liters
* cash_sale_liters
* returned_milk_liters
* difference_liters
* reconciliation_status
* closed_by
* closed_at

Status

* Balanced
* Difference Found
* Reopened

---

# 7. Token Accounting Domain

The Token Accounting Domain manages payment using token books.

Delivery and payment are completely independent.

---

## Token Identity

A Token Identity uniquely identifies a customer's token book type.

A Token Identity consists of:

* Customer
* Milk Type
* Token Number

Example

| Customer | Milk Type | Token Number |
| -------- | --------- | -----------: |
| Hashim   | 1 L       |         1205 |
| Hashim   | 500 ml    |         1205 |

Although the token number is the same, these are different Token Identities.

Fields

* id
* customer_id
* milk_type_id
* token_number
* is_active
* created_at

Unique Constraint

(customer_id, milk_type_id, token_number)

---

## Token Book Issue

Represents every physical token book issued.

Fields

* id
* token_identity_id
* issue_number
* issue_date
* completion_date
* current_sheet
* status
* remarks

Status

* Waiting
* Active
* Completed

The same Token Identity may have many book issues over time.

---

## Token Book Payment

Represents payment for a physical token book.

Fields

* id
* token_book_issue_id
* payment_mode
* payment_status
* book_price
* amount_paid
* balance_amount
* payment_date
* collected_by
* remarks

Payment Modes

* Prepaid
* Postpaid

Payment Status

* Pending
* Partial
* Paid

The Owner decides the payment mode when issuing the book.

---

## Token Register

The Token Register stores today's checker entries.

For every customer expected on today's route, the checker chooses one of the following:

* Sheet Number
* Pending
* Cash Sale
* Not Delivered

Fields

* id
* route_closing_id
* customer_id
* token_identity_id
* sheet_number
* entry_type
* remarks
* checker_id
* created_at

Entry Types

* Token Registered
* Pending
* Cash Sale
* Not Delivered

The Token Register represents the checker's daily working register.

---

## Token Ledger

The Token Ledger stores permanent token transactions.

Fields

* id
* token_identity_id
* transaction_date
* transaction_type
* quantity
* sheet_number
* remarks

Transaction Types

* Token Received
* Pending Created
* Pending Cleared
* Manual Adjustment

The Token Ledger maintains the lifetime balance of every Token Identity.

Current Balance

Negative

Customer owes token sheets.

Current Balance

Positive

Customer has advance token credit.

Balance is maintained independently for every Token Identity.

Half-liter tokens cannot settle one-liter balances.

---

## Warning Log

Stores all warning situations.

Examples

* Non-sequential sheet
* New book before previous completion
* Manual override
* Duplicate sheet

Fields

* id
* token_register_id
* warning_type
* checker_decision
* remarks
* verified_at

---

# 8. Finance Domain

Finance manages monetary transactions.

Tables

* Token Book Payment
* Cash Sales
* Outstanding Payments

Future

* Online Payments
* Customer Wallet
* Receipts

---

# 9. Reporting Domain

Reports are generated from transactional tables.

Examples

* Customer Report
* Route Report
* Delivery Report
* Token Report
* Outstanding Payment Report
* Cash Collection Report
* Daily Reconciliation Report

---

# 10. Entity Relationship Overview

```text id="mjlwmj"
Users

│

├──────────────┐
│              │
▼              ▼

Routes     Milk Types
│              │
│              │
▼              │

Customers──────┘
│
├───────────────┐
│               │
▼               ▼

Customer Subscription
Delivery Exception
│
▼

Daily Delivery
│
▼

Customer Requests

────────────────────────────

Customers
│
▼

Token Identity
│
▼

Token Book Issue
│
├────────► Token Book Payment
│
├────────► Token Register
│
└────────► Token Ledger

────────────────────────────

Milk Dispatch
│
▼

Daily Route Closing
```

---

# 11. Reconciliation Process

The ERP performs reconciliation after the checker finishes registering today's route.

The checker enters:

* Token Register entries
* Cash Sale liters
* Returned Milk liters

The ERP automatically calculates:

```text id="rf60jp"
Loaded Milk

=

Token Milk Registered

+

Cash Sale Liters

+

Returned Milk Liters
```

If equal

```text id="icx6li"
Balanced
```

Otherwise

```text id="q9ggc8"
Difference Found
```

The checker may edit the register until the route becomes balanced.

Only balanced routes can be closed.

---

# 12. Database Constraints

The database enforces:

* Unique Customer Code
* Unique Route Code
* Unique Primary Phone
* Unique Milk Type
* Unique Token Identity
* Foreign Key Integrity
* Soft Delete for Master Data

---

# 13. Database Growth Strategy

The schema supports future expansion.

Future enhancements include:

* QR Code Token Books
* Barcode Scanning
* Mobile Applications
* GPS Tracking
* WhatsApp Integration
* Online Payments
* Multi-Branch Management
* Multi-Company Deployment

---

# 14. Conclusion

The database design reflects the actual operational workflow of a milk distribution business. By separating master data, delivery planning, daily operations, token accounting, finance, and reporting into independent domains, the ERP provides a scalable and maintainable foundation. The introduction of Token Identity, Token Book Issue, Token Register, Token Ledger, and Daily Route Closing allows the system to support flexible business scenarios while preserving complete operational and financial history.
