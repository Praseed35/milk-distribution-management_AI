# Contracts: Delivery Sessions, Reconciliation & Report

**Feature**: 007-delivery-management-pages
**Date**: 2026-07-31
**Base URL (SPA)**: `/api/v1` (axios `client.ts`); routers are also mounted at root for legacy/tests only — the SPA never uses root paths.

**Auth**: Most endpoints below have **no auth dependency** (inherited backend behavior). The SPA sends the bearer token on all requests via the axios interceptor. Only `POST .../reopen` and `PUT /deliveries/{id}/edit` require a token — and, after this feature's backend fix, **OWNER only** (403 otherwise).

**Response gaps (SPA must handle)**: `route_name`, `delivery_partner_name`, `customer_name`, `milk_type_name` always serialize as `null` — join display names client-side (`useRoutes`, `useEmployees`, `useMilkTypes`, checklist). Decimal amounts are returned as numbers/strings by FastAPI JSON (float in JS).

---

## Create / List / Detail

### POST `/deliveries/sessions/` → 201
Body:
```json
{ "route_id": 1, "delivery_date": "2026-07-31", "shift": "MORNING", "delivery_partner_id": 5 }
```
**Behavior change (this feature)**: the session is created **and the planned checklist is auto-generated** from active subscriptions minus active exceptions for the route/date/shift.
Response: `DeliverySessionResponse`. Errors: 404 `Route not found` / `Employee not found`; 400 `Session already exists for route {id} on {date} ({shift})`; 422 invalid shift.

### GET `/deliveries/sessions/?route_id=&delivery_date=&shift=&status=&skip=0&limit=100` → 200
Response:
```json
{ "sessions": [ DeliverySessionResponse ], "total": 1 }
```
Only `is_active=true`. Pagination `limit` 1–1000 (SPA uses `PAGE_SIZE=50`).

### GET `/deliveries/sessions/{id}` → 200
Response: `DeliverySessionResponse` **plus `deliveries: [DailyDeliveryResponse8]`** (8-field variant — do NOT use for editing; use `GET /deliveries/session/{id}` instead). 404 if not found/inactive.

---

## Dispatch & Lifecycle

### POST `/deliveries/sessions/{id}/start` | `/dispatch` → 200 (aliases)
Body: `{ "total_milk_loaded": 5.0 }` (`Decimal gt=0`, else 422).
Response: `DeliverySessionResponse` with `status="STARTED"`. Errors: 404; 400 `InvalidSessionStatusError` (must be PLANNED); 400 `Dispatch already recorded` (`total_milk_loaded > 0`).

### POST `/deliveries/sessions/{id}/complete` → 200 — **NEW in this feature**
No body. Response: `DeliverySessionResponse` with `status="COMPLETED"`. Errors: 404; 400 `InvalidSessionStatusError` (must be STARTED).

### POST `/deliveries/sessions/{id}/close` → 200
No body. Server computes reconciliation first. Response: `DeliverySessionResponse` with `status="CLOSED"`, `reconciliation_status="BALANCED"`. Errors: 404; 400 if already CLOSED; 400 `InvalidSessionStatusError` (must be COMPLETED); 400 `SessionNotBalancedError` — message contains `Difference: {n} liters`.

---

## Checklist

### GET `/deliveries/sessions/{id}/checklist` → 200
Response:
```json
{
  "session_id": 1, "route_name": null, "delivery_date": "2026-07-31", "shift": "MORNING",
  "total_expected": 3,
  "customers": [
    { "customer_id": 10, "customer_name": "Ramesh", "address": "12, MG Road", "phone": "9845012345",
      "milk_type": "Cow Milk", "quantity": 2 }
  ]
}
```
404 if session missing. After the create-time generation fix, `total_expected` matches the generated planned rows.

---

## Reconciliation

### GET `/deliveries/sessions/{id}/reconciliation` → 200
Response: `{ session_id, loaded_milk, token_registered, cash_sales, returned_milk, total_accounted, difference, is_balanced, status }` (status PENDING/UNBALANCED/BALANCED). No 404 — missing session returns all-zero PENDING.

### GET `/deliveries/sessions/{id}/reconciliation/summary` → 200
```json
{ "session_id": 1, "route_name": null, "delivery_date": "2026-07-31", "shift": "MORNING",
  "summary": { "total_customers": 3, "delivered": 1, "pending_token": 1, "cash_sale": 1, "not_delivered": 0 },
  "milk_summary": { "loaded": 5, "token_registered": 2, "cash_sales": 1, "returned": 2 } }
```
Missing session → `{"error": "Session not found"}` with HTTP 200 (guard before rendering).

### GET `/deliveries/sessions/{id}/reconciliation/customers` → 200
```json
{ "session_id": 1, "total": 3,
  "customers": [ { "customer_id": 10, "customer_name": null, "phone": null, "address": null,
      "milk_type": null, "planned_quantity": 2, "status": "DELIVERED", "token_sheet": 3,
      "cash_paid": 0, "is_on_schedule": true } ] }
```

### POST `/deliveries/sessions/{id}/reconciliation/validate` → 200
```json
{ "can_close": false, "is_balanced": false,
  "issues": [ { "code": "RECONCILIATION_MISMATCH", "message": "...", "severity": "ERROR" },
              { "code": "PENDING_TOKENS", "message": "...", "severity": "WARNING" } ] }
```
`can_close = is_balanced`.

### POST `/deliveries/sessions/{id}/reconciliation/submit` → 200
⚠️ **Query parameters, not body**:
```
total_cash_collected: float (required)
cash_sales: list[dict] = []
returned_milk: float = 0
returned_reasons: list[dict] | null
token_sheets_collected: list[dict] | null
remarks: str | null
```
Response: `ReconciliationResponse`. Sets session `total_cash_sales` and `total_returned_milk`.

### POST `/deliveries/sessions/{id}/reconciliation/cash-sales` → 201
⚠️ **Query parameters, not body**: `customer_name`, `customer_phone` (10 chars if given), `milk_type_id`, `quantity`, `amount`, `payment_method` (CASH/UPI/CARD, default CASH).
Creates the "Cash Customer" (`customer_code="C_CASH"`) on first use, then an UNPLANNED CASH_SALE delivery. Response: `{ id, session_id, customer_name, milk_type_name: null, quantity, amount, payment_method, created_at }`.

### DELETE `/deliveries/sessions/{id}/reconciliation/cash-sales/{cash_sale_id}` → 200
Response: `{ "message": "Cash sale removed successfully" }`. 404 `Cash sale not found`.

---

## Report (read-only summary after close)

### GET `/deliveries/sessions/{id}/report` → 200
```json
{ "session_id": 1, "route_name": null, "delivery_date": "2026-07-31", "shift": "MORNING",
  "summary": { "total_customers": 3, "delivered": 1, "pending_token": 1, "cash_sale": 1, "not_delivered": 0 },
  "milk_summary": { "loaded": 5, "token_registered": 2, "cash_sales": 1, "returned": 2 } }
```

---

## SPA consumption summary (SessionDetailPage)

- Session header → `GET /deliveries/sessions/{id}`
- Registration checklist rows → `GET /deliveries/session/{id}` (15-field, see [deliveries.md](./deliveries.md))
- Expected-customers summary + names → `GET /deliveries/sessions/{id}/checklist`
- Reconciliation numbers → `GET /deliveries/sessions/{id}/reconciliation` (+ `/summary`, `/customers`)
- Validate before close → `POST .../reconciliation/validate`; submit → `POST .../reconciliation/submit`
- Read-only summary after close → `GET .../report`
