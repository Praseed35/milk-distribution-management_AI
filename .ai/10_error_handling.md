# Error Handling

## Purpose

This document defines the error handling standards for the Milk Distribution Management System.

Errors should be predictable, consistent, and meaningful.

Every AI assistant must follow these guidelines when raising, creating, or handling exceptions.

---

# Design Principles

Error handling should

- Be consistent
- Be descriptive
- Be reusable
- Preserve business integrity
- Never leak internal implementation details

Business errors should be handled through custom exceptions.

Unexpected system errors should be logged.

---

# Exception Architecture

Project Structure

```
app/

exceptions/

├── auth.py

├── customer.py

├── route.py

├── employee.py

├── token_book.py

├── delivery.py

├── cash_sale.py

├── payment.py

└── common.py
```

Each business module should have its own exception file.

Avoid placing unrelated exceptions together.

---

# Exception Categories

Business Exceptions

Examples

- Customer not found
- Route inactive
- Token already used
- Duplicate customer

↓

HTTP Response

↓

4xx

---

System Exceptions

Examples

- Database unavailable
- Network timeout
- File system error

↓

HTTP Response

↓

5xx

---

Validation Errors

Handled by

Pydantic

Examples

- Missing field
- Invalid data type
- Invalid email
- Invalid date

↓

422 Unprocessable Entity

---

# Exception Flow

```
HTTP Request

↓

Router

↓

Service

↓

Business Validation

↓

Raise Custom Exception

↓

Global Exception Handler

↓

HTTP Response
```

Routers should not contain business validation.

---

# Service Layer

Business exceptions should only be raised inside services.

Example

```python
if customer is None:
    raise CustomerNotFound()
```

Never

```python
raise Exception("Customer not found")
```

---

# Router Layer

Routers should

- Call services
- Return responses

Routers should NOT

- Catch business exceptions
- Perform business validation
- Translate exceptions manually

---

# Custom Exception Pattern

Example

```python
class CustomerNotFound(AppException):

    status_code = 404

    error = "CUSTOMER_NOT_FOUND"

    message = "Customer does not exist."
```

Every exception should contain

- HTTP Status Code
- Error Code
- Human-readable Message

---

# Error Codes

Use uppercase snake_case.

Examples

```
CUSTOMER_NOT_FOUND

ROUTE_NOT_FOUND

INVALID_PASSWORD

TOKEN_ALREADY_USED

ROUTE_NOT_BALANCED

DUPLICATE_CUSTOMER

BOOK_ALREADY_CLOSED
```

Error codes should remain stable for API clients.

---

# HTTP Status Codes

Use appropriate HTTP status codes.

```
400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

500 Internal Server Error
```

Avoid using 500 for business rule violations.

---

# Business Examples

Customer

```
Customer not found

↓

404
```

Duplicate phone

```
Customer already exists

↓

409
```

Inactive route

```
Route inactive

↓

400
```

Unauthorized user

```
Invalid JWT

↓

401
```

Insufficient permissions

```
Owner permission required

↓

403
```

---

# Token Book Examples

Invalid customer

↓

CustomerNotFound

Book already completed

↓

TokenBookClosed

Token already collected

↓

TokenAlreadyUsed

Duplicate token number

↓

DuplicateTokenBook

---

# Delivery Examples

Delivery already completed

↓

DeliveryAlreadyCompleted

Route closed

↓

RouteClosed

Milk quantity invalid

↓

InvalidMilkQuantity

---

# Cash Sale Examples

Negative quantity

↓

InvalidQuantity

Invalid amount

↓

InvalidAmount

Unknown milk type

↓

InvalidMilkType

---

# Reconciliation Examples

Route already reconciled

↓

RouteAlreadyClosed

Mismatch detected

↓

RouteNotBalanced

Duplicate reconciliation

↓

DuplicateReconciliation

---

# Database Errors

Database exceptions should not be exposed directly.

Bad

```
psycopg2.errors.UniqueViolation
```

Good

```
CustomerAlreadyExists
```

Always translate database errors into business exceptions when appropriate.

---

# Logging

Log

- Unexpected exceptions
- Database failures
- Authentication failures
- Critical business failures

Do NOT log

- Passwords
- JWT Tokens
- Sensitive customer information

---

# User Messages

Messages should be understandable.

Good

```
Customer not found.
```

Bad

```
Object reference missing.
```

Do not expose SQL or stack traces.

---

# Exception Hierarchy

Recommended

```
AppException

│

├── AuthException

├── CustomerException

├── RouteException

├── EmployeeException

├── TokenBookException

├── DeliveryException

├── CashSaleException

└── PaymentException
```

Each module should extend a common base exception.

---

# Global Exception Handler

All exceptions should pass through FastAPI's global exception handler.

Responsibilities

- Log errors
- Convert exceptions to HTTP responses
- Return consistent response format

Routers should not duplicate this logic.

---

# Standard Error Response

```json
{
    "success": false,
    "error": {
        "code": "CUSTOMER_NOT_FOUND",
        "message": "Customer does not exist."
    }
}
```

Maintain the same response structure across all endpoints.

---

# AI Checklist

Before creating an exception

✔ Check if a similar exception already exists

✔ Place it in the correct module

✔ Use an appropriate HTTP status code

✔ Create a stable error code

✔ Write a clear message

When raising an exception

✔ Raise custom exceptions only

✔ Preserve business rules

✔ Avoid generic Exception

Never

- Raise Exception directly.
- Expose SQLAlchemy errors.
- Leak stack traces.
- Duplicate exception classes.
- Handle business errors inside routers.

---

# Golden Rule

Exceptions should communicate **business intent**, not implementation details.

A client should understand **what went wrong** without knowing **how the system is implemented**.