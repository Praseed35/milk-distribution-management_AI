# API Design Guidelines

## Purpose

This document defines the API design standards for the Milk Distribution Management System.

All REST APIs should follow these guidelines to ensure consistency, maintainability, and a predictable developer experience.

Every AI assistant must follow these standards when creating or modifying API endpoints.

---

# API Architecture

The project follows RESTful principles.

Request Flow

```
Client

↓

FastAPI Router

↓

Dependency Injection

↓

Service Layer

↓

SQLAlchemy ORM

↓

PostgreSQL

↓

Response Schema

↓

Client
```

Routers should remain thin and delegate business logic to services.

---

# API Versioning

All endpoints must be versioned.

Current version

```
/api/v1/
```

Examples

```
GET  /api/v1/customers

POST /api/v1/customers

GET  /api/v1/routes

POST /api/v1/token-books

GET  /api/v1/cash-sales
```

Never expose unversioned endpoints.

---

# Resource Naming

Use plural nouns.

Good

```
/customers

/routes

/employees

/token-books

/cash-sales

/payments
```

Bad

```
/getCustomer

/createCustomer

/customer-list
```

---

# HTTP Methods

Use HTTP methods according to their purpose.

GET

Retrieve data.

POST

Create resources.

PUT

Replace an existing resource.

PATCH

Partially update a resource.

DELETE

Deactivate or remove a resource (prefer soft delete for business entities).

---

# URL Design

URLs represent resources, not actions.

Good

```
GET /customers/{id}

PUT /customers/{id}

PATCH /customers/{id}

DELETE /customers/{id}
```

Avoid

```
POST /updateCustomer

GET /deleteCustomer

POST /createCustomer
```

---

# Nested Resources

Use nested routes only when there is a clear parent-child relationship.

Examples

```
GET /customers/{customer_id}/token-books

GET /routes/{route_id}/customers

GET /routes/{route_id}/deliveries
```

Avoid deeply nested URLs.

---

# Request Validation

All incoming requests must use Pydantic schemas.

Validation includes

- Required fields
- Data types
- Field lengths
- Allowed values
- Formats

Business validation belongs in services.

---

# Response Schemas

Every endpoint should return a response schema.

Never return SQLAlchemy models directly.

Example

```python
@router.post(
    "/customers",
    response_model=CustomerResponse
)
```

---

# Success Response

Standard format

```json
{
    "success": true,
    "message": "Customer created successfully.",
    "data": {
        ...
    }
}
```

Maintain the same structure across the project.

---

# Error Response

Standard format

```json
{
    "success": false,
    "error": {
        "code": "CUSTOMER_NOT_FOUND",
        "message": "Customer does not exist."
    }
}
```

Do not expose internal exception details.

---

# Pagination

Large collections should support pagination.

Parameters

```
page

page_size
```

Example

```
GET /customers?page=1&page_size=20
```

Avoid returning thousands of records in one response.

---

# Filtering

Support filtering where appropriate.

Examples

```
GET /customers?route_id=5

GET /customers?is_active=true

GET /cash-sales?date=2026-07-22
```

Filtering should not require new endpoints.

---

# Sorting

Allow sorting using query parameters.

Example

```
GET /customers?sort=customer_name

GET /payments?sort=-payment_date
```

Prefix with `-` for descending order.

---

# Searching

Use query parameters.

Example

```
GET /customers?search=Praseed

GET /routes?search=North
```

Search should be case-insensitive whenever practical.

---

# Authentication

Protected endpoints must require authentication.

Example

```
Authorization

Bearer <access_token>
```

Public endpoints should be limited to authentication and health checks.

---

# Authorization

Services must enforce role permissions.

Example

Owner

✔ Manage customers

Checker

✔ Verify deliveries

Delivery Partner

✔ Record deliveries

Do not rely solely on frontend restrictions.

---

# Idempotency

GET requests must not modify data.

PUT requests should be idempotent.

POST requests create new resources.

PATCH requests update only specified fields.

---

# Status Codes

Use appropriate status codes.

```
200 OK

201 Created

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Unprocessable Entity

500 Internal Server Error
```

Avoid returning `200` for failed operations.

---

# File Uploads

If future modules support file uploads:

- Validate file type
- Validate file size
- Store metadata
- Never trust file names from clients

---

# Documentation

Every endpoint should include

- Summary
- Description
- Response model
- Status codes
- Tags

Example

```python
@router.get(
    "/customers",
    summary="List customers",
    description="Retrieve all active customers.",
    response_model=list[CustomerResponse],
    tags=["Customers"]
)
```

---

# Deprecation

Do not remove APIs immediately.

Steps

1. Mark deprecated.
2. Maintain backward compatibility.
3. Introduce replacement.
4. Remove only in the next major version.

---

# AI Checklist

Before creating an endpoint

✔ Use the correct HTTP method

✔ Use request schemas

✔ Use response schemas

✔ Call services only

✔ Require authentication if needed

✔ Return correct status codes

✔ Follow REST principles

Never

- Put business logic inside routers.
- Return ORM models.
- Expose internal exceptions.
- Break API versioning.
- Create action-based URLs.

---

# Golden Rule

An API should represent business resources, not implementation details.

Clients should be able to understand an endpoint's purpose from its URL, HTTP method, and documented schema without reading the backend implementation.