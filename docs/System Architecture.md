# Chapter 2 – System Architecture

---

> **Note:** This document describes the complete planned architecture. As of July 2026, the following layers are implemented: Router, Service, Schema, Model, Authentication, Exception layers. Sprint 1 (Master Data) and Sprint 2 (Subscriptions + Delivery Exceptions) are complete. See the Current Implementation Status section for details.

---

# 1. Introduction

The Milk Distribution ERP follows a modular, domain-driven architecture that models the real operational workflow of a milk distribution business. Instead of organizing the application around database tables or simple CRUD operations, the system is divided into independent business domains such as customer management, delivery planning, token accounting, finance, and reporting.

Each domain has a clearly defined responsibility and communicates with other domains through well-defined business rules. This architecture improves maintainability, scalability, testing, and future expansion while ensuring the software accurately reflects real business operations.

The backend is developed using FastAPI with PostgreSQL as the primary database.

---

# 2. Architecture Goals

The system architecture is designed to achieve the following goals:

* Model real business workflows.
* Separate independent business processes.
* Minimize unnecessary data entry.
* Maintain complete business history.
* Support future business expansion.
* Provide secure role-based access.
* Simplify maintenance and testing.
* Ensure high performance and scalability.

---

# 3. Architectural Principles

The ERP follows several architectural principles.

---

## Principle 1 – Business Driven Design

The software is designed around business operations instead of database tables.

Examples of business domains include:

* Customer Management
* Delivery Planning
* Daily Operations
* Token Accounting
* Finance
* Reporting

---

## Principle 2 – Separation of Responsibilities

Every module performs only one responsibility.

Examples:

Customer Module

* Customer information

Delivery Module

* Milk delivery

Token Module

* Token accounting

Finance Module

* Payment management

This separation makes the ERP easier to maintain and extend.

---

## Principle 3 – Delivery and Payment are Independent

Milk delivery and payment collection are separate business processes.

Milk may be delivered even if the customer does not immediately provide a token sheet.

Likewise, customers may settle pending token sheets on future days.

---

## Principle 4 – Minimal Data Entry

Each employee enters only the information necessary for their role.

Delivery Partner

* Deliver milk
* Collect token sheets
* Collect cash

Checker

* Register token sheets
* Register payments
* Perform reconciliation

Owner

* Configure business
* Manage master data
* Monitor reports

This minimizes workload and reduces data entry errors.

---

## Principle 5 – Assisted Decision Making

The ERP assists employees by providing warnings and automatic calculations instead of blocking workflows.

Examples include:

* Non-sequential token sheets
* New book used before previous completion
* Reconciliation differences
* Missing token sheets

The final decision always belongs to the checker or owner.

---

## Principle 6 – Complete Audit Trail

Every important business transaction is permanently stored.

Examples:

* Customer creation
* Subscription updates
* Token book issuance
* Token registration
* Payments
* Manual adjustments

Historical information is never lost.

---

# 4. Overall System Architecture

```text id="j3tnw8"
                    Client Applications
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     Web Portal      Admin Portal     Future Mobile App
          │                │                │
          └────────────────┼────────────────┘
                           │
                     FastAPI Backend
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
 Authentication      Business Services     Validation
                           │
                     PostgreSQL Database
```

The backend acts as the central business engine responsible for authentication, validation, business rules, and database operations.

---

# 5. Business Domains

The ERP is divided into six independent business domains.

```text id="8l3rlj"
Milk Distribution ERP

│
├── Authentication
│
├── Master Data
│
├── Delivery Planning
│
├── Daily Operations
│
├── Token Accounting
│
├── Finance
│
└── Reporting
```

Each domain focuses on one business capability.

---

# 6. Master Data Domain

The Master Data Domain contains information that changes infrequently.

Modules include:

* Users
* Routes
* Customers
* Milk Types

These entities are shared across the ERP.

---

# 7. Delivery Planning Domain

The Delivery Planning Domain determines what milk should be delivered.

Responsibilities include:

* Customer subscriptions
* Delivery exceptions
* Daily delivery generation

The generated delivery list becomes the basis for the delivery partner's route.

---

# 8. Daily Operations Domain

This domain manages daily field operations.

Responsibilities include:

* Delivery route execution
* Customer requests
* Delivery notes
* Milk dispatch
* Daily reconciliation
* Route closing

The Delivery Partner performs physical delivery while the Checker manages office operations.

---

# 9. Token Accounting Domain

The Token Accounting Domain manages payment settlement through token books.

Responsibilities include:

* Token Identity management
* Token Book Issue
* Token Ledger
* Checker verification
* Warning management

The Token Accounting Domain is completely independent from Delivery Planning.

---

# 10. Finance Domain

The Finance Domain manages all monetary transactions.

Responsibilities include:

* Token book payments
* Cash sales
* Outstanding payments
* Daily cash collection
* Financial reconciliation

Both prepaid and postpaid token book sales are supported.

---

# 11. Reporting Domain

The Reporting Domain generates operational and financial reports.

Examples include:

* Customer reports
* Delivery reports
* Route reports
* Token reports
* Payment reports
* Business analytics

Reports are generated from transactional data without manual calculations.

---

# 12. Layered Architecture

Every request passes through multiple application layers.

```text id="0m8xpn"
HTTP Request

↓

Router

↓

Authentication

↓

Validation

↓

Business Service

↓

Database

↓

Business Service

↓

Router

↓

JSON Response
```

Each layer performs a single responsibility.

---

# 13. Router Layer

The Router Layer is responsible for:

* Receiving HTTP requests
* Validating request format
* Authenticating users
* Calling business services
* Returning API responses

Business logic is never implemented inside routers.

---

# 14. Service Layer

The Service Layer contains the business logic of the ERP.

Responsibilities include:

* Business validations
* Workflow execution
* Rule enforcement
* Database transactions
* Warning generation
* Business calculations

Examples

Customer Service

* Generate customer codes
* Validate phone numbers

Token Service

* Validate token sequence
* Update ledger
* Generate warnings

Reconciliation Service

* Calculate route balance
* Detect mismatches

---

# 15. Database Layer

The Database Layer stores all business information using SQLAlchemy ORM.

Responsibilities include:

* Data persistence
* Relationships
* Transactions
* Query optimization

Alembic manages schema migrations.

---

# 16. Authentication Architecture

Authentication uses JSON Web Tokens (JWT).

Workflow

```text id="nfhf4b"
User Login

↓

Username

↓

Password

↓

JWT Token

↓

Protected APIs
```

Every protected API validates the user's token before processing requests.

---

# 17. Authorization Architecture

Role-Based Access Control (RBAC) controls access to every module.

Supported roles:

* Owner
* Checker
* Delivery Partner
* Customer (Future)

Each role has predefined permissions.

---

# 18. Daily Operational Flow

The architecture follows the actual business workflow.

```text id="1yhdba"
Generate Delivery List

↓

Dispatch Milk

↓

Delivery Partner Delivers Milk

↓

Collect Tokens

↓

Return to Office

↓

Checker Registers Tokens

↓

Register Payments

↓

Reconcile Route

↓

Resolve Differences

↓

Close Route

↓

Generate Reports
```

Each stage is completed before moving to the next.

---

# 19. Reconciliation Architecture

Daily reconciliation is a core architectural component.

The ERP compares:

```text id="xh4xgw"
Loaded Milk

=

Token Milk Registered

+

Cash Sales

+

Returned Milk
```

Where:

* Loaded Milk is obtained from dispatch records.
* Token Milk Registered is calculated automatically from registered token sheets.
* Cash Sales are entered by the checker.
* Returned Milk is entered by the checker.

If the totals match:

```text id="gxfh9q"
Route Balanced
```

Otherwise:

```text id="sr4a4r"
Difference Detected
```

The route remains open until the mismatch is resolved.

---

# 20. Correction Mode

If reconciliation fails, the ERP enters Correction Mode.

The Checker may:

* Edit registered token sheets.
* Change a Pending entry to a sheet number.
* Correct cash sales.
* Correct returned milk.
* Update remarks.

After corrections, reconciliation is performed again.

A route cannot be finalized until it is balanced.

Only the Owner can reopen a finalized route.

---

# 21. Logging Strategy

Every important business event is logged.

Examples include:

* Customer Created
* Subscription Updated
* Delivery Exception Added
* Token Registered
* Payment Received
* Route Closed
* Manual Adjustment

Logs provide complete traceability.

---

# 22. Current Implementation Status (As of July 2026)

The following layers and modules are currently implemented in the codebase:

## Implemented Application Layers

* Router Layer (FastAPI endpoints)
* Service Layer (Business logic)
* Schema Layer (Pydantic models)
* Model Layer (SQLAlchemy ORM)
* Authentication Layer (JWT)
* Exception Layer (Custom exceptions)

## Implemented Business Modules

| Module | Models | Routers | Services | Status |
|--------|--------|---------|----------|--------|
| Authentication | User | auth | auth_service | Complete |
| Users | User | users | user_service | Complete |
| Customers | Customer | customers | customer_service | Complete |
| Routes | Route | routes | route_service | Complete |
| Milk Types | MilkType | milk_types | milk_type_service | Complete |
| Employees | Employee | employees | - | Complete |
| Subscriptions | Subscription | subscriptions | subscription_service | Complete |
| Delivery Exceptions | DeliveryException | delivery_exceptions | delivery_exception_service | Complete |
| Token Books | TokenBook | token_books | token_service | Partial |
| Cash Sales | CashSale | cash_sales | - | Partial |
| Milk Allocation | MilkAllocation | milk_allocation | delivery_service | Partial |
| Reconciliation | Reconciliation | - | reconciliation_service | Partial |

## Not Yet Implemented

* Daily Delivery Planning (No model/router/service)
* Token Ledger (No model/router/service)
* Payment Management (No model/router/service)
* Reports API (Router exists, service incomplete)
* AI Reports (Not started)
* Frontend (Not started)

## Folder Structure Notes

* `app/repositories/` folder exists but is currently empty
* `app/common/` folder exists for shared components
* `app/constants/` folder contains roles, shifts, statuses
* `app/exceptions/` contains module-specific exceptions

---

# 23. Future Scalability

The architecture supports future enhancements without major redesign.

Planned features include:

* React Web Application
* Flutter Mobile Application
* Customer Self-Service Portal
* GPS Tracking
* QR Code / Barcode Token Books
* WhatsApp Notifications
* Online Payments
* Multi-Branch Management
* Multi-Company Deployment

---

# 23. Conclusion

The Milk Distribution ERP architecture is designed around real business operations rather than simple database transactions. By separating master data, delivery planning, daily operations, token accounting, finance, and reporting into independent business domains, the ERP provides a scalable, maintainable, and audit-friendly platform. The architecture minimizes unnecessary data entry, supports human decision-making through assisted workflows, automates daily reconciliation, and preserves complete business history while remaining flexible enough to accommodate future growth and additional business requirements.
