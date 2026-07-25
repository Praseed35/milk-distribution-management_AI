# API_REFERENCE.md - Complete API Endpoint Reference

> Every endpoint with request/response schemas, status codes, and validation rules.

---

## Base URL

```
http://localhost:8000
```

Start with: `uvicorn app.main:app --reload`

---

## Authentication

### POST `/auth/login`

Login and receive a JWT access token.

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Response 200**:
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer"
}
```

**Response 401**:
```json
{"detail": "Invalid username or password"}
```

**Response 422**: Validation error (missing fields)

---

### GET `/auth/me`

Get current authenticated user profile.

**Headers**: `Authorization: Bearer <token>`

**Response 200**:
```json
{
    "id": 1,
    "username": "owner",
    "role": "OWNER"
}
```

**Response 401**: Missing or invalid token

---

### PUT `/auth/change-password`

Change the current user's password.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
    "current_password": "string (6-128 chars)",
    "new_password": "string (6-128 chars)",
    "confirm_password": "string (6-128 chars)"
}
```

**Validation**:
- new_password and confirm_password must match
- new_password must differ from current_password
- current_password must be correct

**Response 200**:
```json
{"message": "Password changed successfully."}
```

**Response 400**: `{"detail": "Current password is incorrect."}`

---

### GET `/auth/owner-dashboard`

Owner-only dashboard endpoint.

**Headers**: `Authorization: Bearer <token>` (OWNER role required)

**Response 200**:
```json
{"message": "Welcome Owner"}
```

**Response 403**: `{"detail": "Access denied"}`

**Response 401**: Missing or invalid token

---

## Users

### GET `/users/`

List all users (no auth required).

**Response 200**: `[{id, username, role, is_active}]`

---

### POST `/users/`

Create a new user.

**Request Body**:
```json
{
    "username": "string",
    "password": "string",
    "role": "string"
}
```

**Response 200**: `{id, username, role, is_active}`

**Response 400**: `{"detail": "Username already exists"}`

**Response 422**: Validation error

---

## Routes

### GET `/routes/`

List all active routes.

**Response 200**: `[{id, route_code, route_name, description, is_active, created_at, updated_at}]`

---

### GET `/routes/{route_id}`

Get a single route by ID.

**Response 200**: `{id, route_code, route_name, description, is_active, created_at, updated_at}`

**Response 404**: `{"detail": "Route not found."}`

---

### POST `/routes/`

Create a new route.

**Request Body**:
```json
{
    "route_code": "string (2-20 chars)",
    "route_name": "string (2-100 chars)",
    "description": "string|null (max 255 chars)"
}
```

**Response 200**: `{id, route_code, route_name, description, is_active, created_at, updated_at}`

**Response 400**: `{"detail": "Route code 'X' already exists."}` or `{"detail": "Route name 'X' already exists."}`

---

### PUT `/routes/{route_id}`

Update an existing route. All fields required.

**Request Body**: Same as POST

**Response 200**: Updated route object

**Response 400**: Duplicate code/name
**Response 404**: Route not found

---

### DELETE `/routes/{route_id}`

Soft-delete a route (sets is_active=False).

**Response 200**: Route with is_active=false

**Response 404**: Route not found

---

## Customers

### GET `/customers/`

List all active customers.

**Response 200**: `[{id, customer_code, customer_name, primary_phone, alternate_phone, address, route_id, remarks, is_active, created_at, updated_at}]`

---

### GET `/customers/{customer_id}`

Get a single customer by ID.

**Response 200**: Customer object

**Response 404**: `{"detail": "Customer not found."}`

---

### POST `/customers/`

Create a new customer. customer_code is auto-generated.

**Request Body**:
```json
{
    "customer_name": "string (2-100 chars)",
    "primary_phone": "string (exactly 10 chars)",
    "alternate_phone": "string|null (exactly 10 chars)",
    "address": "string|null (max 255 chars)",
    "route_id": "integer",
    "remarks": "string|null (max 255 chars)"
}
```

**Response 200**: Customer with auto-generated customer_code (e.g., "C00016")

**Response 400**: `{"detail": "Primary phone 'X' already exists."}` or `{"detail": "Primary phone and alternate phone cannot be the same."}`
**Response 404**: `{"detail": "Route not found."}` or `{"detail": "Selected route is inactive."}`

---

### PUT `/customers/{customer_id}`

Update a customer. All fields required.

**Request Body**: Same as POST

**Response 200**: Updated customer

**Response 400/404**: Various errors

---

### DELETE `/customers/{customer_id}`

Soft-delete a customer.

**Response 200**: Customer with is_active=false

**Response 404**: Customer not found

---

## Milk Types

### GET `/milk-types/`

List all active milk types.

**Response 200**: `[{id, milk_name, volume_ml, description, is_active, created_at, updated_at}]`

---

### GET `/milk-types/{milk_type_id}`

**Response 200**: MilkType object
**Response 404**: `{"detail": "Milk type not found."}`

---

### POST `/milk-types/`

**Request Body**:
```json
{
    "milk_name": "string (2-100 chars)",
    "volume_ml": "integer (> 0)",
    "description": "string|null (max 255 chars)"
}
```

**Response 200**: Created MilkType
**Response 400**: `{"detail": "Milk name 'X' already exists."}`

---

### PUT `/milk-types/{milk_type_id}`

Same as POST body. All fields required.

---

### DELETE `/milk-types/{milk_type_id}`

Soft-delete. Returns is_active=false.

---

## Employees

### GET `/employees/`

List all active employees.

**Response 200**: `[{id, employee_code, name, phone, address, role, route_id, is_active, username, created_at, updated_at}]`

Note: `username` is included from the linked User (null if no linked user).

---

### GET `/employees/{employee_id}`

**Response 200**: Employee object
**Response 404**: Employee not found

---

### POST `/employees/` (OWNER only)

Create an employee. Optionally creates a linked user account.

**Headers**: `Authorization: Bearer <token>` (OWNER role required)

**Request Body**:
```json
{
    "name": "string (2-100 chars)",
    "phone": "string (10-20 chars)",
    "address": "string|null (max 255 chars)",
    "role": "string (1-50 chars)",
    "route_id": "integer|null (> 0)",
    "username": "string|null (3-100 chars)",
    "password": "string|null (6-128 chars)",
    "confirm_password": "string|null (6-128 chars)"
}
```

**Validation**:
- If any of username/password/confirm_password is provided, ALL three must be provided
- password and confirm_password must match
- Phone must be unique
- If route_id provided, route must exist and be active
- If username provided, must not already exist

**Response 201**: Employee object (employee_code auto-generated as E{NNNNN})

---

### PUT `/employees/{employee_id}`

Update employee details (not credentials).

**Request Body** (all fields optional):
```json
{
    "name": "string|null",
    "phone": "string|null",
    "address": "string|null",
    "role": "string|null",
    "route_id": "integer|null"
}
```

---

### PUT `/employees/{employee_id}/credentials` (OWNER only)

Update the linked user's credentials.

**Request Body**:
```json
{
    "username": "string|null (3-100 chars)",
    "password": "string|null (6-128 chars)",
    "confirm_password": "string|null (6-128 chars)"
}
```

**Validation**: At least one field required. Password fields must be provided together.

**Response 400**: `{"detail": "Employee has no linked user account."}` if no user linked.

---

### DELETE `/employees/{employee_id}`

Soft-delete employee.

---

## Subscriptions

### GET `/subscriptions/`

List all active subscriptions with joined data.

**Response 200** (SubscriptionListResponse):
```json
[{
    "id": 1,
    "customer_id": 1,
    "customer_code": "C00001",
    "customer_name": "Rajesh Kumar",
    "route_name": "Downtown Route",
    "milk_type_name": "Full Cream Milk",
    "milk_type_volume": 1000,
    "morning_quantity": 2,
    "evening_quantity": 1,
    "status": "ACTIVE",
    "is_active": true
}]
```

---

### GET `/subscriptions/{subscription_id}`

Get detailed subscription with nested objects.

**Response 200** (SubscriptionDetailResponse):
```json
{
    "id": 1,
    "customer": {
        "id": 1,
        "customer_code": "C00001",
        "customer_name": "Rajesh Kumar",
        "primary_phone": "9876543210"
    },
    "milk_type": {
        "id": 1,
        "milk_name": "Full Cream Milk",
        "volume_ml": 1000
    },
    "morning_quantity": 2,
    "evening_quantity": 1,
    "status": "ACTIVE",
    "start_date": "2026-07-20T10:00:00Z",
    "end_date": null,
    "remarks": "...",
    "is_active": true,
    "created_at": "...",
    "updated_at": "..."
}
```

---

### GET `/subscriptions/customer/{customer_id}`

Get all subscriptions for a specific customer (list format).

---

### POST `/subscriptions/`

**Request Body**:
```json
{
    "customer_id": "integer (> 0)",
    "milk_type_id": "integer (> 0)",
    "morning_quantity": "integer (>= 0, default 0)",
    "evening_quantity": "integer (>= 0, default 0)",
    "status": "string (default 'ACTIVE', max 20 chars)",
    "remarks": "string|null (max 255 chars)"
}
```

**Response 201**: Created subscription

**Errors**:
- 404: Customer or MilkType not found
- 400: Inactive customer/milk_type, invalid quantities, duplicate subscription

---

### PUT `/subscriptions/{subscription_id}`

Partial update (all fields optional).

**Request Body**:
```json
{
    "morning_quantity": "integer|null",
    "evening_quantity": "integer|null",
    "status": "string|null",
    "remarks": "string|null"
}
```

**Business rule**: After update, at least one quantity must be > 0.

---

### DELETE `/subscriptions/{subscription_id}`

Deactivates subscription (sets is_active=False, status="INACTIVE").

---

## Delivery Exceptions

### GET `/delivery-exceptions/`

List all active exceptions with joined data.

**Response 200** (DeliveryExceptionListResponse):
```json
[{
    "id": 1,
    "subscription_id": 1,
    "customer_id": 1,
    "customer_code": "C00001",
    "customer_name": "Rajesh Kumar",
    "route_name": "Downtown Route",
    "exception_type": "VACATION",
    "start_date": "2026-08-01T00:00:00Z",
    "end_date": "2026-08-05T00:00:00Z",
    "status": "ACTIVE",
    "is_active": true
}]
```

---

### GET `/delivery-exceptions/{exception_id}`

Detail view with nested subscription and customer.

**Response 200** (DeliveryExceptionDetailResponse):
```json
{
    "id": 1,
    "subscription": {
        "id": 1,
        "customer": { "id": 1, "customer_code": "...", "customer_name": "...", "primary_phone": "..." },
        "morning_quantity": 2,
        "evening_quantity": 1
    },
    "exception_type": "VACATION",
    "start_date": "...",
    "end_date": "...",
    "reason": "...",
    "status": "ACTIVE",
    "is_active": true,
    "created_at": "...",
    "updated_at": "..."
}
```

---

### GET `/delivery-exceptions/subscription/{subscription_id}`

List exceptions for a specific subscription.

---

### POST `/delivery-exceptions/`

**Request Body**:
```json
{
    "subscription_id": "integer (> 0)",
    "exception_type": "string (1-20 chars)",
    "start_date": "datetime",
    "end_date": "datetime|null",
    "reason": "string|null (max 255 chars)"
}
```

**Response 201**: Created exception

**Errors**:
- 404: Subscription not found
- 400: Inactive subscription, end_date < start_date, overlapping exception

---

### PUT `/delivery-exceptions/{exception_id}`

Partial update. Overlap check runs on updated values.

---

### DELETE `/delivery-exceptions/{exception_id}`

Cancels exception (sets is_active=False, status="CANCELLED").

---

## Token Books

### Token Identity Endpoints

#### POST `/token-books/identities/`

**Request Body**:
```json
{
    "customer_id": "integer (> 0)",
    "milk_type_id": "integer (> 0)",
    "token_number": "integer (> 0)"
}
```

**Response 201**: Created TokenIdentity

**Errors**:
- 404: Customer or MilkType not found/inactive
- 400: Duplicate identity (same customer + milk_type + token_number)

---

#### GET `/token-books/identities/`

List all active identities with joined customer and milk_type data.

---

#### GET `/token-books/identities/{identity_id}`

Detail view with nested customer and milk_type objects.

---

#### GET `/token-books/identities/customer/{customer_id}`

All identities for a customer.

---

#### PUT `/token-books/identities/{identity_id}`

Only `token_number` can be updated. Duplicate check enforced.

---

#### DELETE `/token-books/identities/{identity_id}`

Soft-delete identity.

---

### Token Book Issue Endpoints

#### POST `/token-books/issues/`

**Request Body**:
```json
{
    "token_identity_id": "integer (> 0)",
    "issue_number": "integer (> 0)",
    "remarks": "string|null (max 255 chars)"
}
```

**Response 201**: Created issue (status=WAITING, current_sheet=0)

**Errors**:
- 404: Token identity not found
- 400: Active book already exists for this identity
- 400: Duplicate issue_number for this identity

---

#### GET `/token-books/issues/`

List all active issues with joined data (customer, milk_type, token_number).

---

#### GET `/token-books/issues/{issue_id}`

Detail view with full nested hierarchy (identity -> customer + milk_type).

---

#### GET `/token-books/issues/identity/{identity_id}`

All issues for a specific identity.

---

#### PUT `/token-books/issues/{issue_id}`

Update status, current_sheet, completion_date, or remarks.

**Request Body** (all fields optional):
```json
{
    "status": "string|null",
    "current_sheet": "integer|null (>= 0)",
    "completion_date": "datetime|null",
    "remarks": "string|null"
}
```

---

#### DELETE `/token-books/issues/{issue_id}`

Soft-delete issue.

---

### Token Book Payment Endpoints

#### POST `/token-books/payments/`

**Request Body**:
```json
{
    "token_book_issue_id": "integer (> 0)",
    "payment_mode": "string (PREPAID/POSTPAID)",
    "book_price": "decimal (> 0)",
    "amount_paid": "decimal (>= 0, default 0)",
    "remarks": "string|null (max 255 chars)"
}
```

**Auto-calculations**:
- balance_amount = book_price - amount_paid
- payment_status: PAID (balance<=0), PARTIAL (amount>0), PENDING (amount=0)

**Response 201**: Created payment

**Errors**:
- 404: Token book issue not found
- 400: Amount paid exceeds book price

---

#### GET `/token-books/payments/`

List all active payments with customer data.

---

#### GET `/token-books/payments/{payment_id}`

Detail view with full nested hierarchy (issue -> identity -> customer + milk_type).

---

#### GET `/token-books/payments/issue/{issue_id}`

All payments for a specific issue.

---

#### PUT `/token-books/payments/{payment_id}`

Update payment fields. Balance and status are auto-recalculated.

---

#### DELETE `/token-books/payments/{payment_id}`

Soft-delete payment.

---

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request / Business rule violation |
| 401 | Authentication required or failed |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 422 | Request validation error (missing/invalid fields) |

---

## Swagger UI

Available at: `http://localhost:8000/docs`

Interactive API documentation with try-it-out capability.
