# API_REFERENCE.md - Complete API Endpoint Reference

> Every endpoint with request/response schemas, status codes, and validation rules.

---

## Base URL

```
Primary:   http://localhost:8000/api/v1
Legacy:    http://localhost:8000           (root-level routes, deprecated but kept for backward compatibility)
```

Start with: `uvicorn app.main:app --reload`

**Note**: All endpoints in this document are shown at their root paths for readability. Every endpoint is ALSO available under the `/api/v1` prefix (e.g., `POST /auth/login` → `POST /api/v1/auth/login`). The React frontend uses the `/api/v1` paths exclusively.

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
    "shift": "string|null (MORNING|EVENING — null = whole day)",
    "start_date": "datetime",
    "end_date": "datetime|null",
    "reason": "string|null (max 255 chars)"
}
```

**Response 201**: Created exception

**Errors**:
- 404: Subscription not found
- 400: Inactive subscription, invalid shift, end_date < start_date, overlapping exception

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

## Delivery Sessions

### POST `/deliveries/sessions/`

Create a new delivery session.

**Request Body**:
```json
{
    "route_id": "integer",
    "delivery_date": "date (YYYY-MM-DD)",
    "shift": "string (MORNING|EVENING)",
    "delivery_partner_id": "integer"
}
```

**Response 201**: Created DeliverySession with status=PLANNED

**Errors**: 404 (route/employee not found), 400 (duplicate session)

---

### GET `/deliveries/sessions/`

List delivery sessions with optional filters and pagination.

**Query Parameters**:
- `route_id` (int, optional): Filter by route
- `delivery_date` (date, optional): Filter by date
- `shift` (str, optional): MORNING or EVENING
- `status` (str, optional): PLANNED/STARTED/COMPLETED/CLOSED
- `skip` (int, default 0): Pagination offset
- `limit` (int, default 100, max 1000): Pagination limit

**Response 200**: `{sessions: [...], total: int}`

---

### GET `/deliveries/sessions/{session_id}`

Get session detail with deliveries list.

**Response 200**: DeliverySession with nested deliveries array
**Response 404**: Session not found

---

### POST `/deliveries/sessions/{session_id}/start`

Start a session (alias for dispatch). Sets status to STARTED.

**Request Body**: Same as `/dispatch`

---

### POST `/deliveries/sessions/{session_id}/dispatch`

Record milk dispatch. Sets total_milk_loaded and changes status to STARTED.

**Request Body**:
```json
{
    "total_milk_loaded": "decimal (> 0)"
}
```

**Response 200**: Updated DeliverySession (status=STARTED)

**Errors**:
- 404: Session not found
- 400: Session not in PLANNED status, or dispatch already recorded

---

### POST `/deliveries/sessions/{session_id}/complete`

Mark a started session as COMPLETED (STARTED -> COMPLETED). Added during Phase 5 (Delivery Management pages).

**Request Body**: none

**Response 200**: Updated DeliverySession (status=COMPLETED)

**Errors**:
- 404: Session not found
- 400: Session not in STARTED status

---

### POST `/deliveries/sessions/{session_id}/close`

Close a session. Requires balanced reconciliation.

**Response 200**: Updated DeliverySession (status=CLOSED, reconciliation_status=BALANCED)

**Errors**:
- 404: Session not found
- 400: Session not in COMPLETED status, already closed, or not balanced

---

### GET `/deliveries/sessions/{session_id}/checklist`

Get delivery checklist for a session.

**Response 200**:
```json
{
    "session_id": 1,
    "route_name": "Downtown Route",
    "delivery_date": "2026-07-29",
    "shift": "MORNING",
    "total_expected": 5,
    "customers": [
        {
            "customer_id": 1,
            "customer_name": "Rajesh Kumar",
            "address": "12 MG Road",
            "phone": "9876543210",
            "milk_type": "Full Cream Milk",
            "quantity": 2
        }
    ]
}
```

**Response 404**: Session not found

---

### GET `/deliveries/sessions/{session_id}/reconciliation`

Calculate reconciliation for a session.

**Response 200**:
```json
{
    "session_id": 1,
    "loaded_milk": 50.0,
    "token_registered": 40.0,
    "cash_sales": 8.0,
    "returned_milk": 2.0,
    "total_accounted": 50.0,
    "difference": 0.0,
    "is_balanced": true,
    "status": "BALANCED"
}
```

---

### GET `/deliveries/sessions/{session_id}/reconciliation/summary`

Get session summary data.

---

### GET `/deliveries/sessions/{session_id}/reconciliation/customers`

Get per-customer delivery status for a session.

---

### POST `/deliveries/sessions/{session_id}/reconciliation/validate`

Validate if a session can be closed. Returns issues list.

---

### POST `/deliveries/sessions/{session_id}/reconciliation/submit`

Submit reconciliation with cash collected, returns, and token sheets.

**Parameters**: total_cash_collected, cash_sales[], returned_milk, returned_reasons[], token_sheets_collected[], remarks

---

### POST `/deliveries/sessions/{session_id}/reconciliation/cash-sales`

Add a cash sale during reconciliation.

**Query Parameters**: customer_name, customer_phone, milk_type_id, quantity, amount, payment_method

---

### DELETE `/deliveries/sessions/{session_id}/reconciliation/cash-sales/{cash_sale_id}`

Remove a cash sale.

---

### GET `/deliveries/sessions/{session_id}/report`

Get session report with summary and milk summary.

**Response 200**:
```json
{
    "session_id": 1,
    "route_name": "Downtown Route",
    "delivery_date": "2026-07-29",
    "shift": "MORNING",
    "summary": {
        "total_customers": 5,
        "delivered": 3,
        "pending_token": 1,
        "cash_sale": 1,
        "not_delivered": 0
    },
    "milk_summary": {
        "loaded": 50.0,
        "token_registered": 40.0,
        "cash_sales": 10.0,
        "returned": 0.0
    }
}
```

---

## Deliveries

### PUT `/deliveries/{delivery_id}`

Update a delivery's status, quantity, token sheet, or cash amount. Uses optimistic locking.

**Request Body** (all fields optional):
```json
{
    "delivery_status": "DELIVERED|PENDING_TOKEN|CASH_SALE|NOT_DELIVERED|CANCELLED|null",
    "delivered_quantity": "int|null (>= 0)",
    "token_sheet_number": "int|null",
    "cash_amount": "decimal|null",
    "remarks": "string|null (max 500 chars)",
    "version": "int|null"
}
```

**Response 200**: Updated DailyDelivery

**Errors**: 404 (delivery not found), 400 (invalid token sheet), **409 (concurrent edit)**

---

### POST `/deliveries/unplanned`

Register an unplanned delivery.

**Request Body**:
```json
{
    "session_id": "integer",
    "customer_id": "integer",
    "milk_type_id": "integer",
    "delivered_quantity": "integer (>= 0)",
    "delivery_status": "DELIVERED|PENDING_TOKEN|CASH_SALE",
    "registration_method": "TOKEN_SHEET|CASH|PENDING",
    "token_sheet_number": "int|null",
    "reason": "string (1-500 chars)"
}
```

**Response 201**: Created DailyDelivery

**Errors**: 404 (session/customer/milk_type), 400 (invalid token sheet)

---

### POST `/deliveries/{delivery_id}/register-token`

Register a token sheet for a delivery.

**Request Body**:
```json
{
    "token_sheet_number": "int (> 0)",
    "acknowledged_warnings": ["string list of warning codes"],
    "acknowledgment_reason": "string|null (max 500 chars)"
}
```

**Response 200**:
```json
{
    "delivery_id": 1,
    "sheet_registered": true,
    "token_book_issue_id": 1,
    "new_current_sheet": 3,
    "warnings_logged": 0,
    "message": "Token Sheet #2 registered successfully."
}
```

**Errors**: 404, 400 (invalid sheet, already used)

---

### POST `/deliveries/validate-token`

Validate a token sheet before registration.

**Request Body**:
```json
{
    "customer_id": "integer",
    "milk_type_id": "integer",
    "sheet_number": "int (> 0)",
    "token_book_issue_id": "int|null"
}
```

**Response 200**:
```json
{
    "is_valid": true,
    "warnings": [],
    "can_proceed": true,
    "requires_acknowledgment": false
}
```

---

### GET `/deliveries/customer/{customer_id}/token-status`

Get customer's token book status.

**Response 200**: CustomerTokenStatusResponse with list of token books, old book remaining info.

---

### PUT `/deliveries/{delivery_id}/edit`

Edit a delivery (owner only, requires reopened session).

**Request Body**:
```json
{
    "delivery_status": "DELIVERED|...|null",
    "return_token_sheet": false,
    "reason": "string (1-500 chars)",
    "version": "int|null"
}
```

**Response 200**: `{delivery_id, old_status, new_status, token_sheet_returned, ...}`

**Errors**: 404, 409 (concurrent edit), 400 (invalid)

---

### GET `/deliveries/{delivery_id}/warnings`

Get warnings for a delivery.

---

### GET `/deliveries/session/{session_id}`

Get all deliveries for a session (filterable by status).

**Query Parameters**: status (optional), skip (default 0), limit (default 100)

---

### POST `/deliveries/session/{session_id}/reopen`

Reopen a closed session (owner only).

**Request Body**:
```json
{
    "reason": "string (1-500 chars)"
}
```

**Response 200**: Updated DeliverySession (status=COMPLETED)

**Errors**: 404, 400 (session not closed)

---

### GET `/deliveries/session/{session_id}/edit-history`

Get full edit history for a session.

**Response 200**: List of edit records with old/new values, edited_by, reason, timestamp.

---

## Reports

> All report endpoints require authentication. Date filtering supports preset strings (`today`, `yesterday`, `this_week`, `last_week`, `this_month`, `last_month`, `this_year`) or explicit `from_date`/`to_date`. All list endpoints accept `?format=csv` for CSV export and `?refresh=true` to bypass cache.
>
> **Frontend consumers** (Phase 7, commit 4489d6a): `frontend/src/api/reports.ts` wraps all 6 endpoints below (plus `downloadReportCsv`); see `module_map.md` for the consumer chain (`api/reports.ts` → `hooks/useReports.ts` → `pages/reports/*`).

### GET `/reports/route-delivery`

Delivery performance per route — loaded vs delivered vs cash collected vs returned vs shortage.

**Roles**: OWNER, ADMIN, CHECKER, DELIVERY_PARTNER (own route only)

**Query Parameters**: route_id, preset, from_date, to_date, shift (MORNING/EVENING), group_by (route/day/week/month), format, page, page_size

**Response 200 (JSON)**:
```json
{
  "data": [{
    "route_id": 1, "route_name": "Route A", "route_code": "R001",
    "session_count": 30, "delivery_count": 450,
    "total_loaded_quantity": 900.0, "total_delivered_quantity": 885.0,
    "total_cash_collected": 500.0, "total_token_registered": 800.0,
    "total_returned_quantity": 10.0, "shortage_surplus": 5.0,
    "is_balanced": false
  }],
  "total": 1, "page": 1, "page_size": 50, "generated_at": "2026-07-30T10:30:00"
}
```

**Errors**: 401, 403 (DELIVERY_PARTNER wrong route)

---

### GET `/reports/revenue`

Revenue breakdown by source (token book payments vs customer bill payments), with optional grouping by payment mode, route, or milk type.

**Roles**: OWNER only

**Query Parameters**: preset, from_date, to_date, route_id, milk_type_id, payment_mode, group_by (source/payment_mode/route/milk_type), format, page, page_size

**Response 200 (JSON)**:
```json
{
  "date_from": "2026-07-01", "date_to": "2026-07-30",
  "total_revenue": 8000.0, "token_book_revenue": 5000.0,
  "customer_bill_revenue": 3000.0,
  "by_source": [{"source": "token_book_payments", "amount": 5000.0, "percentage": 62.5}, ...],
  "by_payment_mode": [...], "by_route": [...], "by_milk_type": [...]
}
```

**Errors**: 401, 403

---

### GET `/reports/collection-efficiency`

Billed vs paid vs outstanding per customer with aging buckets (0-30, 31-60, 61-90, 90+).

**Roles**: OWNER, ADMIN

**Query Parameters**: preset, from_date, to_date, route_id, min_outstanding, format, page, page_size

**Response 200 (JSON)**: Array of customer items with total_billed, total_paid, balance, collection_percentage, aging breakdown.

**Errors**: 401, 403

---

### GET `/reports/customer/{customer_id}/consumption`

Customer consumption history with trend detection (increasing/declining/stable).

**Roles**: OWNER, ADMIN, CHECKER

**Path Parameters**: customer_id

**Query Parameters**: preset, from_date, to_date, group_by (day/week/month), format, page, page_size

**Response 200 (JSON)**:
```json
{
  "customer_id": 1, "customer_name": "Customer A",
  "date_from": "2026-07-01", "date_to": "2026-07-30",
  "total_consumption": 60.0, "average_daily": 2.0, "days_with_data": 30,
  "trend": {"period": "stable", "recent_7day_avg": 2.0, "preceding_21day_avg": 1.9, "change_percentage": 5.26},
  "items": [{"date": "2026-07-01", "total_quantity": 2.0, "by_milk_type": [{"milk_type": "Full Cream", "quantity": 2.0}]}]
}
```

**Errors**: 401, 404

---

### GET `/reports/token-utilization`

Token book usage — sheets used, remaining, utilization %, and books nearing replacement.

**Roles**: OWNER, ADMIN

**Query Parameters**: route_id, customer_id, low_threshold (default 20, 1-100), format, page, page_size

**Response 200 (JSON)**: Array of token items with total_sheets_used, total_sheets_remaining, utilization_percentage, books_below_20_percent.

**Errors**: 401, 403

---

### GET `/reports/dashboard`

Single-page operational overview for today — session counts, delivery statuses, flagged issues.

**Roles**: OWNER, ADMIN, CHECKER, DELIVERY_PARTNER (own route)

**Query Parameters**: none (always today), refresh

**Response 200 (JSON)**:
```json
{
  "report_date": "2026-07-30", "total_sessions": 3, "total_milk_loaded": 30.0,
  "total_milk_delivered": 28.0, "total_cash_collected": 5.0,
  "deliveries_by_status": {"DELIVERED": 15, "PENDING_TOKEN": 2, "CASH_SALE": 3, "NOT_DELIVERED": 0, "CANCELLED": 0},
  "pending_token_count": 2, "unclosed_sessions": 1, "unbalanced_sessions": 0, "completed_not_closed": 0
}
```

**Errors**: 401

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
| 409 | Conflict (concurrent edit detected via optimistic locking) |
| 422 | Request validation error (missing/invalid fields) |

---

## Swagger UI

Available at: `http://localhost:8000/docs`

Interactive API documentation with try-it-out capability.
