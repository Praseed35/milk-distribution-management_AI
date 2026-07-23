# Architecture

## Purpose

This document defines the software architecture of the Milk Distribution Management System.

Every AI assistant must understand this architecture before creating or modifying code.

The goal is to keep the project modular, maintainable, and consistent.

---

# Architecture Style

The application follows a layered architecture.

```
                HTTP Request
                     │
                     ▼
             FastAPI Router
                     │
                     ▼
          Dependency Injection
                     │
                     ▼
               Service Layer
                     │
                     ▼
          SQLAlchemy ORM Models
                     │
                     ▼
               PostgreSQL
```

Every layer has a single responsibility.

---

# Layer Responsibilities

## 1. Router Layer

Location

```
app/routers/
```

Purpose

- Expose REST APIs
- Parse HTTP requests
- Validate request schemas
- Inject dependencies
- Call service methods
- Return HTTP responses

Responsibilities

- Request validation
- Authentication dependencies
- Authorization dependencies
- Response serialization

Never

- Write business logic
- Query the database
- Implement calculations
- Access SQLAlchemy models directly

Example

```
POST /customers
        │
        ▼
customer_service.create_customer()
```

---

## 2. Dependency Layer

Location

```
app/dependencies.py
```

Purpose

Provides reusable FastAPI dependencies.

Examples

- Current authenticated user
- Database session
- Permission checking
- JWT validation

Responsibilities

- Authentication
- Authorization
- Shared dependencies

Never

- Business workflows
- Database queries

---

## 3. Service Layer

Location

```
app/services/
```

Purpose

The Service Layer contains all business logic.

Every business rule belongs here.

Responsibilities

- Business validation
- Workflow execution
- Database operations
- Transactions
- Rule enforcement
- Calling helper utilities

Current Services

```
auth_service.py

customer_service.py

delivery_service.py

reconciliation_service.py

route_service.py

token_service.py

user_service.py
```

Services may

- Read models
- Create models
- Update models
- Delete models (soft delete where applicable)

Services may use

- SQLAlchemy Session
- Utility functions
- Constants
- Exceptions

Never

- Return HTTP responses
- Access Request objects
- Define API routes

---

## 4. Model Layer

Location

```
app/models/
```

Purpose

Defines SQLAlchemy ORM models.

Responsibilities

- Table definitions
- Relationships
- Constraints
- Indexes

Models should contain

- Columns
- Relationships
- SQLAlchemy configuration

Models should never contain

- Business logic
- Validation logic
- API logic

---

## 5. Schema Layer

Location

```
app/schemas/
```

Purpose

Defines Pydantic models.

Types

- Create
- Update
- Response
- Login
- Filters

Responsibilities

- Request validation
- Response serialization
- Type safety

Never

- Query the database
- Implement business logic

---

## 6. Exception Layer

Location

```
app/exceptions/
```

Purpose

Contains custom application exceptions.

Current exception modules

```
customer.py

delivery.py

route.py

token_book.py

user.py
```

Responsibilities

- Business exceptions
- Validation exceptions
- Domain-specific errors

Never

- Return HTTP responses directly
- Log unrelated errors

---

## 7. Core Layer

Location

```
app/core/
```

Purpose

Application infrastructure.

Contains

- Configuration
- Security
- Authentication
- JWT utilities
- Roles
- Global constants

Responsibilities

- Application configuration
- Security helpers
- Environment settings

Never

- Business logic

---

## 8. Constants Layer

Location

```
app/constants/
```

Purpose

Stores reusable constant values.

Examples

- Roles
- Statuses
- Shifts

Benefits

- Avoid magic strings
- Improve consistency

---

## 9. Common Layer

Location

```
app/common/
```

Purpose

Shared reusable code that is not tied to a specific business module.

Examples

- Shared DTOs
- Base classes
- Generic utilities

Never place business-specific logic here.

---

## 10. Utils Layer

Location

```
app/utils/
```

Purpose

Contains helper functions.

Examples

- Formatting
- Validators
- Date helpers
- Utility functions

Never

- Access the database
- Implement business workflows

---

## Database Layer

Configuration

```
app/database.py
```

Responsibilities

- SQLAlchemy Engine
- SessionLocal
- Base
- Database connection

All database access uses SQLAlchemy ORM.

Raw SQL should be avoided unless there is a demonstrated performance requirement.

---

# Request Lifecycle

Example

```
Client

↓

FastAPI Router

↓

Authentication

↓

Dependency Injection

↓

Service

↓

SQLAlchemy ORM

↓

PostgreSQL

↓

Service

↓

Router

↓

JSON Response
```

---

# Data Flow

Request

↓

Pydantic Schema

↓

Router

↓

Service

↓

SQLAlchemy Model

↓

Database

↓

Model

↓

Response Schema

↓

JSON

---

# Design Principles

Single Responsibility

Each layer has one responsibility.

Business Logic

Business rules belong only in Services.

Thin Routers

Routers should only coordinate requests.

Reusable Code

Avoid duplicate logic.

Explicit Validation

Validate with Pydantic first.

Business validation belongs in Services.

Consistency

Follow existing project patterns before introducing new ones.

---

# Current Modules

Implemented

- Authentication
- Users
- Customers
- Routes
- Employees
- Milk Allocation
- Cash Sales
- Dashboard
- Reports
- Token Books
- Delivery
- Reconciliation

Future

- Customer Subscriptions
- Delivery Planning
- Shift Scheduling
- Inventory
- Notifications
- AI Analytics
- Mobile Application

---

# AI Development Rules

Before writing code

1. Identify the correct module.
2. Identify the correct service.
3. Reuse existing patterns.
4. Check existing exceptions.
5. Use existing schemas.

While writing code

- Keep routers thin.
- Put business logic in services.
- Use SQLAlchemy ORM.
- Reuse helper functions.
- Raise custom exceptions.
- Use type hints.

Never

- Put business logic in routers.
- Access the database from routers.
- Duplicate existing logic.
- Introduce a new architectural pattern without approval.
- Modify unrelated modules.

---

# Architecture Goals

The architecture should remain

- Modular
- Readable
- Maintainable
- Testable
- Scalable

New features should integrate into the existing architecture instead of creating parallel implementations.

Always preserve consistency with the current project structure.