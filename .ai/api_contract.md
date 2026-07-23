# API Contract

## Purpose

This document defines the API standards for the Milk Distribution Management System.

Every REST endpoint must follow these conventions.

The AI MUST follow these rules whenever creating or modifying APIs.

---

# API Design Principles

The API follows REST architecture.

Rules

- Version every endpoint.
- Resource-oriented URLs.
- Stateless requests.
- JSON only.
- Consistent response format.
- Never expose internal implementation.
- Never expose database models directly.
- Never bypass the Service layer.

Base URL

/api/v1

Examples

/api/v1/customers

/api/v1/subscriptions

/api/v1/token-books

/api/v1/deliveries

---

# Standard HTTP Methods

GET

Retrieve resources.

POST

Create resources.

PUT

Replace resources.

PATCH

Partial update.

DELETE

Soft delete only.

Never permanently delete business history.

---

# URL Naming

Use plural nouns.

Good

/customers

/routes

/subscriptions

/payments

Bad

/customer

/createCustomer

/getRoute

No verbs inside URLs.

---

# Response Format

Success

{
    "success": true,
    "message": "Customer created successfully.",
    "data": {}
}

Collection

{
    "success": true,
    "message": "Customers retrieved successfully.",
    "count": 25,
    "data": []
}

Error

{
    "success": false,
    "message": "Customer not found.",
    "error_code": "CUSTOMER_NOT_FOUND"
}

Validation Error

{
    "success": false,
    "message": "Validation failed.",
    "errors": [
        {
            "field": "phone",
            "message": "Phone number is required."
        }
    ]
}

---

# Status Codes

200

GET Success

201

Created

204

Successful delete (soft delete)

400

Business validation error

401

Unauthorized

403

Forbidden

404

Not Found

409

Conflict

422

Request validation failed

500

Unexpected server error

---

# Pagination

Collections must support pagination.

Parameters

?page=1

?page_size=20

Response

{
    "success": true,
    "page": 1,
    "page_size": 20,
    "total": 512,
    "pages": 26,
    "data": []
}

---

# Sorting

Example

GET

/customers?sort=name

Descending

/customers?sort=-created_at

Allowed Fields

name

created_at

updated_at

Never sort by computed fields.

---

# Filtering

Example

/customers

?route_id=...

&status=active

&search=john

Rules

Filtering belongs inside Repository layer.

Never filter inside Router.

---

# Searching

Use query parameter.

Example

/customers?search=Praseed

Search should support

Customer name

Phone

Customer code

Never search using raw SQL.

---

# Authentication

Protected APIs require JWT.

Authorization

Bearer <token>

Public Endpoints

/login

/refresh

/health

Everything else requires authentication.

---

# Authorization

Owner

Full access.

Checker

Operational access.

Delivery Partner

Assigned routes only.

Administrator

System administration.

Authorization belongs inside dependencies.

Never inside routers.

---

# Validation

Validation order

1. Pydantic

↓

2. Service

↓

3. Repository

Pydantic

Type validation.

Service

Business rules.

Repository

Database validation.

---

# CRUD Pattern

Every module should provide

GET Collection

GET By ID

POST

PUT

PATCH

DELETE

Example

Customers

GET

/customers

GET

/customers/{customer_id}

POST

/customers

PUT

/customers/{customer_id}

PATCH

/customers/{customer_id}

DELETE

/customers/{customer_id}

---

# Business APIs

Business operations are separate from CRUD.

Examples

POST

/subscriptions/{id}/pause

POST

/subscriptions/{id}/resume

POST

/routes/{id}/close

POST

/token-books/{id}/issue

POST

/payments/{id}/refund

Never overload CRUD endpoints with business actions.

---

# Error Handling

Services raise custom exceptions.

Routers never catch business exceptions.

Global exception handlers return standardized responses.

Never return stack traces.

---

# Dependencies

Router

↓

Dependency Injection

↓

Authentication

↓

Authorization

↓

Service

↓

Repository

↓

Database

Never access Repository directly from Router.

---

# API Versioning

Current

v1

Future

v2

Breaking changes require a new version.

Never break existing APIs.

---

# Documentation

Every endpoint must include

Summary

Description

Request model

Response model

Possible exceptions

HTTP status codes

Example request

Example response

Use FastAPI OpenAPI documentation.

---

# AI Instructions

When creating an API

Always identify

1. Router

2. Service

3. Repository

4. Schema

5. Model

6. Dependencies

7. Exception

8. Tests

Never create an endpoint without

Validation

Authentication

Authorization

Error handling

Documentation

Always reuse existing architecture.

Never invent a different response format.

Never bypass the Service layer.