# API Reference: Milk Management AI

**Base URL:** `http://localhost:8000`  
**OpenAPI docs:** `http://localhost:8000/docs`

## Authentication

Most endpoints are currently **unprotected**. Auth endpoints are the only ones that use JWT-based auth.

**Get Token:**
```
POST /auth/login
Content-Type: application/json

{ "username": "owner", "password": "owner123" }

Response: { "access_token": "<jwt>", "token_type": "bearer" }
```

**Use Token:**
```
Authorization: Bearer <access_token>
```

---

## Implemented Endpoints

### Auth (`/auth`) — Tag: Authentication

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| POST | `/auth/login` | No | Login, returns JWT | 200 / 401 |
| GET | `/auth/me` | Yes | Get current user profile | 200 / 401 |
| GET | `/auth/owner-dashboard` | Yes (OWNER) | Owner-only dashboard message | 200 / 403 |

**POST /auth/login**
- Request: `{ "username": str, "password": str }`
- Response: `{ "access_token": str, "token_type": "bearer" }`

**GET /auth/me**
- Auth: Bearer token required
- Response: `{ "id": int, "username": str, "role": str }`

**GET /auth/owner-dashboard**
- Auth: Bearer token + OWNER role required
- Response: `{ "message": str }`

---

### Users (`/users`) — Tag: Users

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| GET | `/users/` | No | List all users | 200 |
| POST | `/users/` | No | Create new user | 200 / 400 |

**POST /users/**
- Request: `{ "username": str, "password": str, "role": str }`
- Response: User object (id, username, role, is_active)
- Error 400: Username already exists

---

### Routes (`/routes`) — Tag: Routes

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| POST | `/routes/` | No | Create route | 200 / 400 |
| GET | `/routes/` | No | List all active routes | 200 |
| GET | `/routes/{route_id}` | No | Get route by ID | 200 / 404 |
| PUT | `/routes/{route_id}` | No | Update route | 200 / 400 / 404 |
| DELETE | `/routes/{route_id}` | No | Soft-delete route | 200 / 404 |

**POST /routes/**
- Request: `{ "route_code": str, "route_name": str, "description": str|null }`
- Validations: route_code 2-20 chars, route_name 2-100 chars, description max 255
- Errors 400: Duplicate code or duplicate name

---

### Customers (`/customers`) — Tag: Customers

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| POST | `/customers/` | No | Create customer | 200 / 400 / 404 |
| GET | `/customers/` | No | List all active customers | 200 |
| GET | `/customers/{customer_id}` | No | Get customer by ID | 200 / 404 |
| PUT | `/customers/{customer_id}` | No | Update customer | 200 / 400 / 404 |
| DELETE | `/customers/{customer_id}` | No | Soft-delete customer | 200 / 404 |

**POST /customers/**
- Request: `{ "customer_name": str, "primary_phone": str(10), "alternate_phone": str(10)|null, "address": str|null, "route_id": int, "remarks": str|null }`
- Auto-generates `customer_code` (C00001, C00002, ...)
- Errors:
  - 404: Route not found
  - 400: Inactive route, duplicate phone, same primary/alternate phone

---

### Milk Types (`/milk-types`) — Tag: Milk Types

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| POST | `/milk-types/` | No | Create milk type | 200 / 400 |
| GET | `/milk-types/` | No | List all active milk types | 200 |
| GET | `/milk-types/{milk_type_id}` | No | Get by ID | 200 / 404 |
| PUT | `/milk-types/{milk_type_id}` | No | Update milk type | 200 / 400 / 404 |
| DELETE | `/milk-types/{milk_type_id}` | No | Soft-delete | 200 / 404 |

**POST /milk-types/**
- Request: `{ "milk_name": str, "volume_ml": int, "description": str|null }`
- Validations: milk_name 2-100 chars, volume_ml > 0
- Error 400: Duplicate name

---

### Subscriptions (`/subscriptions`) — Tag: Subscriptions

| Method | Path | Auth | Description | Status |
|--------|------|------|-------------|--------|
| POST | `/subscriptions/` | No | Create subscription | **201** / 400 / 404 |
| GET | `/subscriptions/` | No | List all active subscriptions (joined) | 200 |
| GET | `/subscriptions/{id}` | No | Get subscription detail | 200 / 404 |
| GET | `/subscriptions/customer/{customer_id}` | No | Get by customer | 200 / 404 |
| PUT | `/subscriptions/{id}` | No | Update quantities/status | 200 / 400 / 404 |
| DELETE | `/subscriptions/{id}` | No | Deactivate (soft-delete) | 200 / 400 / 404 |

**POST /subscriptions/**
- Request: `{ "customer_id": int, "milk_type_id": int, "morning_quantity": int, "evening_quantity": int, "remarks": str|null }`
- Validations: customer_id > 0, milk_type_id > 0, morning/evening >= 0, at least one > 0
- Errors: Customer/milk_type not found (404), inactive (400), duplicate subscription (400)

---

## Unimplemented Endpoints (Stub Files, Empty)

| Prefix | Tag | Planned Functionality |
|--------|-----|----------------------|
| `/employees` | Employees | CRUD for employee records |
| `/token-books` | Token Books | Token issuance, collection, carry-forward |
| `/milk-allocation` | Milk Allocation | Daily milk allocation per route/shift |
| `/cash-sales` | Cash Sales | Walk-in cash-based milk sales |
| `/reports` | Reports | Business analytics, delivery/payment/reconciliation reports |
| `/dashboard` | Dashboard | Owner/checker dashboard with KPIs |

---

## Common Response Patterns

**Success (200):**
```json
{ "id": 1, "field": "value", "is_active": true, "created_at": "...", "updated_at": "..." }
```

**Error (4xx):**
```json
{ "detail": "Error message describing the problem" }
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required"
    }
  ]
}
```
