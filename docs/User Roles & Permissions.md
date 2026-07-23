# Chapter 4 – User Roles and Responsibilities

---

# 1. Introduction

The Milk Distribution ERP uses **Role-Based Access Control (RBAC)** to ensure that every employee has access only to the functions required for their responsibilities.

The ERP is designed around the actual workflow followed by milk distribution companies. Each role performs a specific set of business activities, reducing unnecessary data entry while improving accountability, security, and operational efficiency.

The primary objective is to allow each employee to focus on their work while the ERP coordinates the complete business process.

Version 1 of the ERP supports four user roles:

* Owner
* Checker
* Delivery Partner
* Customer (Future Version)

Every operation performed by any user is recorded for auditing purposes.

---

# 2. User Role Hierarchy

```text
                     Owner
                       │
        ┌──────────────┴──────────────┐
        │                             │
     Checker                  Delivery Partner
                       │
                       ▼
             Customer (Future Version)
```

The Owner has complete administrative access.

The Checker performs all office-based daily operations.

The Delivery Partner performs physical delivery and collection activities.

Customers will receive limited self-service access in future versions.

---

# 3. Owner

## Overview

The Owner is responsible for managing the entire milk distribution business.

The Owner controls:

* Business configuration
* Employee management
* Customer management
* Route management
* Delivery planning
* Token management
* Payment management
* Business reports
* System monitoring

The Owner has unrestricted access to every module of the ERP.

---

## Customer Management

Responsibilities include:

* Create customers
* Update customer information
* Activate customers
* Deactivate customers
* View customer history
* View delivery history
* View payment history

---

## Route Management

Responsibilities include:

* Create delivery routes
* Update route information
* Activate routes
* Deactivate routes
* Assign customers to routes

---

## Milk Type Management

The Owner manages all milk products.

Examples include:

* 250 ml
* 500 ml
* 1 Liter
* 2 Liter

Future milk products can be added without changing the software architecture.

---

## Subscription Management

The Owner manages customer subscriptions.

Responsibilities include:

* Create subscriptions
* Modify quantities
* Morning and evening scheduling
* Pause subscriptions
* Resume subscriptions
* Cancel subscriptions

---

## Delivery Exception Management

The Owner manages temporary delivery changes.

Examples include:

* Extra milk
* No milk
* Vacation
* Resume delivery
* Temporary quantity changes
* Shift-specific changes

These exceptions are automatically considered during daily delivery generation.

---

## Token Management

The Owner is responsible for:

* Creating Token Identities
* Issuing Token Books
* Reissuing Token Books
* Replacing damaged books
* Closing completed books
* Managing Token Book Payments

Both **Prepaid** and **Postpaid** token book payments are supported.

The payment mode is decided individually for each Token Book Issue.

---

## Financial Management

Responsibilities include:

* Record token book payments
* View outstanding payments
* Manage customer balances
* Monitor cash collections
* Financial reporting

---

## Reporting & Analytics

The Owner has access to all reports.

Examples:

* Customer Reports
* Route Reports
* Delivery Reports
* Token Reports
* Payment Reports
* Outstanding Reports
* Daily Reconciliation Reports
* Business Analytics

---

# 4. Checker

## Overview

The Checker performs all office-based operational activities after the Delivery Partner returns from the delivery route.

The Checker is responsible for:

* Registering today's deliveries
* Registering token sheets
* Recording pending deliveries
* Recording cash sales
* Recording returned milk
* Registering unplanned deliveries
* Performing reconciliation
* Correcting reconciliation differences
* Closing routes

The Checker performs the majority of daily ERP data entry.

---

## Daily Workflow

After the Delivery Partner returns, the Checker receives:

* Collected token sheets
* Cash collected
* Remaining milk
* Customer requests (if any)

The Checker then completes the day's processing using the ERP.

---

## Delivery Registration

The ERP displays all customers included in today's generated delivery schedule.

For each customer, the Checker chooses one of the following registration methods.

---

### Option 1 – Token Sheet

Milk delivered.

Customer provided a token sheet.

The Checker enters:

* Sheet Number

The ERP automatically validates:

* Token Number
* Milk Type
* Active Token Book
* Duplicate Sheet
* Sheet Sequence

---

### Option 2 – Pending Token

Milk delivered.

Customer did not provide a token sheet.

The ERP records the delivery as pending.

The customer may settle the pending token during any future shift or on any future day.

---

### Option 3 – Cash Sale

Milk delivered.

Customer paid using cash instead of a token.

The ERP records the quantity as a cash sale.

---

### Option 4 – Not Delivered

Milk was scheduled but not delivered.

Examples:

* Customer unavailable
* Customer refused milk
* Delivery skipped
* Operational issue

---

## Unplanned Delivery

Sometimes a customer is not included in today's delivery schedule but still receives milk.

Example:

Yesterday the customer requested:

> "No milk tomorrow."

Today's delivery list therefore excludes that customer.

However, during delivery, the customer changes the decision and requests milk.

The Delivery Partner supplies the milk.

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
* Registration Method
* Reason

The ERP marks the delivery as **Unplanned** while preserving the original delivery schedule.

---

## Automatic Validation

During token registration, the ERP automatically verifies:

* Active Customer
* Active Token Identity
* Correct Milk Type
* Active Token Book
* Duplicate Sheet
* Non-sequential Sheet
* Previous Book Completion

Warnings are displayed immediately.

The Checker decides whether to continue.

---

## Warning Examples

Examples include:

* Duplicate token sheet
* Non-sequential sheet
* New book started before previous completion
* Invalid token book
* Manual override

Warnings do not prevent registration.

The ERP records every warning together with the Checker's decision.

---

## Daily Reconciliation

After all customer registrations are completed, the Checker enters only:

* Total Cash Sales (Liters)
* Total Returned Milk (Liters)

The ERP automatically calculates:

* Total Token Milk Registered

The ERP then performs reconciliation.

```text
Loaded Milk

=

Token Milk Registered

+

Cash Sales

+

Returned Milk
```

---

## Correction Mode

If reconciliation fails, the ERP displays the difference.

Example

```text
Loaded Milk           : 110 L

Token Registered      : 94 L

Cash Sales            : 8 L

Returned Milk         : 7 L

--------------------------------

Difference            : 1 L
```

The Checker can:

* Edit Token Registrations
* Change Pending to Token Sheet
* Correct Sheet Numbers
* Correct Cash Sales
* Correct Returned Milk
* Add Unplanned Deliveries

The route remains editable until reconciliation becomes balanced.

---

## Route Closing

A route can be closed only when:

* Every delivery is registered.
* Reconciliation is balanced.
* Cash Sales are entered.
* Returned Milk is entered.

After closing:

* Token Ledger is finalized.
* Daily reports are generated.
* Route becomes read-only.

Only the Owner may reopen a closed route.

---

## Checker Permissions

✔ View Customers

✔ View Routes

✔ View Subscriptions

✔ Register Deliveries

✔ Register Token Sheets

✔ Register Pending Tokens

✔ Register Cash Sales

✔ Register Returned Milk

✔ Add Unplanned Deliveries

✔ Perform Reconciliation

✔ Close Routes

✘ Create Customers

✘ Issue Token Books

✘ Delete Customers

---

# 5. Delivery Partner

## Overview

The Delivery Partner performs only physical delivery operations.

The Delivery Partner does not perform token registration or reconciliation inside the ERP.

This minimizes mobile data entry and allows the Checker to complete all office-based processing.

---

## Responsibilities

The Delivery Partner is responsible for:

* Collecting dispatched milk
* Delivering milk
* Collecting token sheets
* Collecting cash
* Receiving customer requests
* Returning remaining milk to the office

Customer requests may include:

* Extra milk
* No milk
* Vacation
* Resume delivery
* Temporary quantity changes

These requests are communicated to the office for approval and processing.

---

## Delivery Partner Permissions

✔ View Assigned Route

✔ View Today's Delivery List

✔ View Customer Details

✔ View Delivery Notes

✘ Register Token Sheets

✘ Perform Reconciliation

✘ Modify Customer Records

✘ Issue Token Books

---

# 6. Customer (Future Version)

Future versions of the ERP will provide customer access through a web portal or mobile application.

Customers will be able to:

* View subscriptions
* View delivery history
* View token books
* View payment history
* View outstanding balances
* Request delivery changes
* Request vacation
* Resume subscriptions
* Make online payments

All operational requests require approval before affecting the delivery schedule.

---

# 7. Permission Matrix

| Module                     | Owner | Checker | Delivery Partner |  Customer |
| -------------------------- | :---: | :-----: | :--------------: | :-------: |
| User Management            |   ✔   |    ✘    |         ✘        |     ✘     |
| Route Management           |   ✔   |   View  |       View       |     ✘     |
| Customer Management        |   ✔   |   View  |   View Assigned  | View Self |
| Milk Types                 |   ✔   |   View  |       View       |    View   |
| Subscriptions              |   ✔   |   View  |       View       |    View   |
| Delivery Exceptions        |   ✔   |   View  |      Request     |  Request  |
| Milk Dispatch              |   ✔   |   View  |       View       |     ✘     |
| Daily Deliveries           |   ✔   |    ✔    |       View       |    View   |
| Token Registration         |   ✔   |    ✔    |         ✘        |     ✘     |
| Pending Token Registration |   ✔   |    ✔    |         ✘        |     ✘     |
| Cash Sale Registration     |   ✔   |    ✔    |   Collect Only   |     ✘     |
| Returned Milk Entry        |   ✔   |    ✔    |    Return Only   |     ✘     |
| Unplanned Delivery         |   ✔   |    ✔    |         ✘        |     ✘     |
| Route Reconciliation       |  View |    ✔    |         ✘        |     ✘     |
| Route Closing              |   ✔   |    ✔    |         ✘        |     ✘     |
| Token Ledger               |   ✔   |   View  |         ✘        |  View Own |
| Token Book Payment         |   ✔   |    ✔    |       View       |  View Own |
| Reports & Analytics        |   ✔   | Limited |      Limited     |     ✘     |

# 8. Authentication

Every ERP user must authenticate before accessing the system.

The system uses **JSON Web Token (JWT)** authentication to secure API access.

Authentication workflow:

```text
User Login
      │
      ▼
Username & Password
      │
      ▼
Credential Verification
      │
      ▼
JWT Access Token
      │
      ▼
Protected APIs
```

Every protected API validates the JWT before processing the request.

If authentication fails, the request is rejected.

---

## Login Process

Every user logs in using:

* Username
* Password

After successful authentication, the ERP issues:

* Access Token
* Refresh Token

The Access Token is used for API requests.

The Refresh Token is used to obtain a new Access Token without logging in again.

---

## Session Management

The ERP automatically manages user sessions.

Features include:

* Secure login
* Token expiration
* Token refresh
* Logout
* Session validation

This prevents unauthorized access to the ERP.

---

# 9. Authorization

After successful authentication, the ERP determines the user's role and grants permissions accordingly.

Authorization is based on **Role-Based Access Control (RBAC)**.

Supported roles:

* Owner
* Checker
* Delivery Partner
* Customer (Future)

Every API verifies whether the logged-in user has permission to perform the requested operation.

Unauthorized requests are rejected.

---

## Authorization Rules

Examples:

Owner

* Full access

Checker

* Office operations only

Delivery Partner

* Delivery information only

Customer

* Personal information only

Each user can access only the modules required for their work.

---

## HTTP Response Codes

Examples

**401 Unauthorized**

User is not authenticated.

Examples:

* Invalid token
* Expired token
* Missing token

---

**403 Forbidden**

User is authenticated but lacks permission.

Example:

A Delivery Partner attempting to create a customer.

---

# 10. Audit Trail

Every important business activity is permanently recorded.

Audit logging improves:

* Accountability
* Security
* Business analysis
* Troubleshooting

Audit records are never deleted.

---

## Logged Activities

Examples include:

Customer Management

* Customer Created
* Customer Updated
* Customer Deactivated

---

Subscription Management

* Subscription Created
* Subscription Modified
* Subscription Cancelled

---

Token Management

* Token Identity Created
* Token Book Issued
* Token Book Reissued
* Token Registered
* Pending Recorded
* Cash Sale Recorded
* Unplanned Delivery Added
* Manual Adjustment

---

Daily Operations

* Milk Dispatch
* Route Generated
* Route Reconciliation
* Route Closed
* Route Reopened

---

Finance

* Token Book Payment
* Outstanding Payment Updated
* Cash Collection Recorded

---

## Audit Information Stored

Each audit record contains:

* User
* Role
* Date
* Time
* Operation
* Module
* Entity
* Record ID
* Remarks

This provides complete traceability for every important business transaction.

---

# 11. Future Roles

The ERP architecture is designed to support additional roles without modifying the existing business logic.

Possible future roles include:

---

## Branch Manager

Responsibilities:

* Monitor branch operations
* View branch reports
* Manage branch employees
* Approve branch requests

---

## Accountant

Responsibilities:

* Payment verification
* Financial reports
* Outstanding payment management
* Daily cash verification

---

## Customer Support

Responsibilities:

* Handle customer requests
* Update subscriptions
* Register complaints
* Follow up pending issues

---

## Auditor

Responsibilities:

* Read-only access
* Audit reports
* Financial verification
* Operational verification

---

## Regional Manager

Responsibilities:

* Monitor multiple branches
* Compare branch performance
* Business analysis

---

## System Administrator

Responsibilities:

* User management
* System configuration
* Security monitoring
* Backup management

---

# 12. Security Principles

The ERP follows modern security practices.

---

## Role-Based Access Control

Every user receives only the permissions required for their role.

---

## Least Privilege Principle

Users cannot access modules unrelated to their responsibilities.

---

## Secure Authentication

JWT-based authentication protects all APIs.

Passwords are stored as secure hashes.

Plain-text passwords are never stored.

---

## API Security

Every protected API verifies:

* Authentication
* Authorization
* User Status
* Token Validity

---

## Data Integrity

The ERP maintains:

* Foreign Key Constraints
* Database Transactions
* Validation Rules
* Duplicate Prevention

---

## Soft Delete Strategy

Master records are not permanently deleted.

Instead, they are marked as inactive.

Examples:

* Customers
* Routes
* Milk Types

Historical transactions remain available.

---

## Complete Business History

Business transactions are never removed.

Historical records remain available for:

* Reporting
* Auditing
* Customer History
* Financial Verification

---

# 13. Business Responsibility Flow

The following diagram summarizes the responsibilities of each role.

```text
                    OWNER
                      │
 ┌────────────────────┼────────────────────┐
 │                    │                    │
 ▼                    ▼                    ▼

Business Setup   Master Data        Reports & Finance

                      │
                      ▼

          Daily Delivery Generation

                      │
                      ▼

              MILK DISPATCH

                      │
                      ▼

            DELIVERY PARTNER

      • Deliver Milk
      • Collect Tokens
      • Collect Cash
      • Receive Customer Requests
      • Return Remaining Milk

                      │
                      ▼

                 CHECKER

      • Register Deliveries
      • Register Token Sheets
      • Register Pending Tokens
      • Register Cash Sales
      • Register Returned Milk
      • Add Unplanned Deliveries
      • Perform Reconciliation
      • Resolve Differences
      • Close Route

                      │
                      ▼

              TOKEN LEDGER

                      │
                      ▼

           REPORTS & ANALYTICS
```

This workflow clearly separates physical delivery operations from office-based reconciliation and accounting.

---

# 14. Conclusion

The User Roles and Responsibilities module provides a structured access model for the Milk Distribution ERP by assigning every business activity to the appropriate user role.

The **Owner** manages business configuration, master data, token books, payments, and reporting.

The **Delivery Partner** focuses exclusively on physical delivery, token collection, cash collection, and customer communication without performing ERP data entry.

The **Checker** performs all office-based operational activities, including delivery registration, token verification, cash sale registration, unplanned delivery registration, reconciliation, correction of operational differences, and route closure.

This clear separation of responsibilities minimizes unnecessary data entry, improves operational efficiency, strengthens accountability, and ensures that every business transaction is securely recorded and fully auditable while accurately reflecting the real workflow of a milk distribution company.
