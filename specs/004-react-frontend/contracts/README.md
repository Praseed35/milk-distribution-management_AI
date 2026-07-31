# API Contracts — React Frontend

> Frontend-to-backend API contracts for the Milk Distribution ERP.

## Base URL

```
/api/v1
```

Vite dev proxy forwards `/api/*` → `http://localhost:8000`. Frontend Axios instance uses `baseURL: "/api/v1"`.

## Authentication

All endpoints except login and health require `Authorization: Bearer <token>` header. Token obtained via `POST /auth/login`.

## Response Patterns

The backend uses three response patterns. Frontend API client must handle all three:

### Pattern 1: Envelope
```json
{
  "success": true,
  "data": { ... }
}
```
Used by: most CRUD single-resource endpoints.

### Pattern 2: Direct model
```json
{ "id": 1, "route_code": "R001", ... }
```
Used by: some list endpoints (routes, customers, milk-types, employees).

### Pattern 3: Paginated
```json
{
  "sessions": [ ... ],
  "total": 42
}
// or
{
  "data": [ ... ],
  "total": 42,
  "page": 1,
  "page_size": 50,
  "generated_at": "..."
}
```
Used by: delivery sessions list, reports.

## Error Responses

### Validation Error (422)
```json
{
  "detail": [
    { "loc": ["body", "customer_name"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```

### Not Found (404)
```json
{ "detail": "Customer not found" }
```

### Conflict (409)
```json
{ "detail": "Concurrent edit detected. Please refresh." }
```

## Endpoint Catalog

See full endpoint map in [`spec.md`](../spec.md) (lines 388-489) — all ~80 endpoints listed with method, old path, and new `/api/v1` path.

## Key Interaction Flows

### Auth Flow
```
POST /auth/login       → { access_token, token_type }
GET  /auth/me          → { id, username, role }          [Bearer token]
PUT  /auth/change-password → { success: true }            [Bearer token]
```

### Session Workflow (Delivery)
```
POST /deliveries/sessions/                               → session
POST /deliveries/sessions/{id}/dispatch                  → { loaded_quantity }
GET  /deliveries/sessions/{id}/checklist                 → { session, deliveries }
POST /deliveries/{id}/register-token                     → updated delivery
POST /deliveries/validate-token                          → { valid, warning? }
POST /deliveries/unplanned                               → new delivery
GET  /deliveries/sessions/{id}/reconciliation            → reconciliation data
POST /deliveries/sessions/{id}/reconciliation/submit     → balanced status
POST /deliveries/sessions/{id}/close                     → closed session
```

### Payment Flow
```
POST /payments/bills/generate   → bill with items
GET  /payments/outstanding/{id} → outstanding balance
POST /payments/                 → record payment
```

### Subscription & Exception Flow (Phase 3)
List endpoints return **plain arrays** (no pagination envelope). Create returns **201** + resource DTO.

```
# Subscriptions
GET  /subscriptions/                        → SubscriptionListResponse[]   [flat joined fields]
GET  /subscriptions/customer/{id}           → SubscriptionListResponse[]   [filter by customer]
GET  /subscriptions/{id}                    → SubscriptionDetailResponse   [nested customer + milk_type]
POST /subscriptions/                        → 201 SubscriptionResponse      [no start_date/end_date in body]
PUT  /subscriptions/{id}                    → SubscriptionResponse
DELETE /subscriptions/{id}                  → SubscriptionResponse          [soft delete, is_active=false]

# Delivery Exceptions
GET  /delivery-exceptions/                  → DeliveryExceptionListResponse[]  [flat joined fields]
GET  /delivery-exceptions/subscription/{id} → DeliveryExceptionResponse[]       [filter by subscription]
GET  /delivery-exceptions/{id}              → DeliveryExceptionDetailResponse   [nested subscription]
POST /delivery-exceptions/                  → 201 DeliveryExceptionResponse
PUT  /delivery-exceptions/{id}              → DeliveryExceptionResponse
DELETE /delivery-exceptions/{id}            → DeliveryExceptionResponse         [soft delete]
```

**Field notes**
- `SubscriptionCreate` accepts `status` (default `"ACTIVE"`); `start_date`/`end_date` are response-only.
- `exception_type` ∈ `VACATION | NO_MILK | HOLIDAY`.
- Route-level filtering (subscriptions by route, exceptions by customer/route) is **client-side** on the list DTOs — backend accepts no such query params (known backend gap).

### Report Queries
All reports support `?preset=this_month` or `?from_date=&to_date=`, and `?format=csv`.
```
GET /reports/dashboard                   → daily KPIs (no params, always today)
GET /reports/route-delivery?route_id=&preset=this_week
GET /reports/revenue?from_date=&to_date=
GET /reports/customer/{id}/consumption?preset=this_month
GET /reports/token-utilization?low_threshold=20
GET /reports/collection-efficiency?min_outstanding=100
```
