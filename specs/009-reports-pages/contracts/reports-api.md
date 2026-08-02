# API Contracts — Reports Endpoints

> Frontend-to-backend contracts for the six report endpoints consumed by Phase 7.
> All requests go through the shared Axios client (`baseURL: "/api/v1"`, Bearer token).

## Base

```
Base URL: /api/v1
Auth:     Authorization: Bearer <token>  (required on all report endpoints)
```

## Roles (server-enforced)

| Endpoint | Allowed roles |
|----------|---------------|
| `GET /reports/dashboard` | OWNER, ADMIN, CHECKER, DELIVERY_PARTNER |
| `GET /reports/route-delivery` | all roles; DELIVERY_PARTNER restricted to own route (403 otherwise) |
| `GET /reports/revenue` | OWNER only (403 for others) |
| `GET /reports/customer/{id}/consumption` | OWNER, ADMIN, CHECKER |
| `GET /reports/token-utilization` | OWNER, ADMIN; DELIVERY_PARTNER restricted to own route |
| `GET /reports/collection-efficiency` | OWNER, ADMIN |

## Date-range parameters (shared)

Every endpoint (except dashboard) accepts **either** `preset` **or** `from_date`/`to_date`:

```
preset ∈ today | yesterday | this_week | last_week | this_month | last_month | this_year
```

- If only `from_date` given → single-day report.
- If neither given → defaults to current month (month-to-date).
- `refresh=true` bypasses the backend in-memory cache.

---

## 1. Operational Dashboard

```
GET /reports/dashboard?refresh=false
```

No date params — always today. **Response** (direct object):

```json
{
  "report_date": "2026-08-02",
  "total_sessions": 3,
  "total_milk_loaded": 120.0,
  "total_milk_delivered": 114.0,
  "total_cash_collected": 1450.0,
  "deliveries_by_status": { "DELIVERED": 40, "PENDING_TOKEN": 2, "CASH_SALE": 5, "NOT_DELIVERED": 1, "CANCELLED": 0 },
  "pending_token_count": 2,
  "unclosed_sessions": 1,
  "unbalanced_sessions": 1,
  "completed_not_closed": 0
}
```

---

## 2. Route Delivery Report

```
GET /reports/route-delivery?route_id=&shift=&preset=&from_date=&to_date=&page=&page_size=&format=json&refresh=false
```

**Response** (envelope):

```json
{
  "data": [
    {
      "route_id": 1, "route_name": "Route A", "route_code": "R001",
      "session_count": 2, "delivery_count": 30,
      "total_loaded_quantity": 120.0, "total_delivered_quantity": 114.0,
      "total_cash_collected": 1450.0, "total_token_registered": 95.0,
      "total_returned_quantity": 6.0, "shortage_surplus": -1.0, "is_balanced": false
    }
  ],
  "total": 1, "page": 1, "page_size": 50, "generated_at": "2026-08-02T09:00:00"
}
```

`format=csv` → `StreamingResponse` (`text/csv`) attachment. Summary row is computed client-side.

---

## 3. Revenue Report

```
GET /reports/revenue?route_id=&milk_type_id=&payment_mode=&preset=&from_date=&to_date=&group_by=source&format=json&refresh=false
```

**Response** (direct object — no envelope):

```json
{
  "date_from": "2026-08-01", "date_to": "2026-08-02",
  "total_revenue": 5000.0, "token_book_revenue": 3200.0, "customer_bill_revenue": 1800.0,
  "by_source": [ { "source": "TOKEN_BOOK", "payment_mode": null, "route_name": null, "milk_type_name": null, "amount": 3200.0, "percentage": 64.0 } ],
  "by_payment_mode": [ { "source": null, "payment_mode": "CASH", "route_name": null, "milk_type_name": null, "amount": 2000.0, "percentage": 40.0 } ],
  "by_route": [ { "source": null, "payment_mode": null, "route_name": "Route A", "milk_type_name": null, "amount": 3000.0, "percentage": 60.0 } ],
  "by_milk_type": [ { "source": null, "payment_mode": null, "route_name": null, "milk_type_name": "Cow", "amount": 4000.0, "percentage": 80.0 } ]
}
```

---

## 4. Customer Consumption

```
GET /reports/customer/{customer_id}/consumption?preset=&from_date=&to_date=&group_by=day&format=json&refresh=false
```

**Response** (direct object):

```json
{
  "customer_id": 5, "customer_name": "Vikram",
  "date_from": "2026-07-03", "date_to": "2026-08-02", "group_by": "day",
  "total_consumption": 90.0, "average_daily": 3.0, "days_with_data": 30,
  "trend": { "period": "30d", "recent_7day_avg": 2.8, "preceding_21day_avg": 3.1, "change_percentage": -9.7 },
  "items": [ { "date": "2026-08-01", "total_quantity": 3.0, "by_milk_type": [{ "milk_type": "Cow", "quantity": 3.0 }] } ]
}
```

`404 {"detail": "Customer not found"}` when the customer does not exist.

---

## 5. Token Utilization

```
GET /reports/token-utilization?route_id=&customer_id=&low_threshold=20&format=json&refresh=false
```

**Response** (envelope):

```json
{
  "data": [
    {
      "customer_id": 5, "customer_name": "Vikram", "route_name": "Route A", "token_number": 12,
      "milk_type_name": "Cow", "total_books_issued": 3, "active_books": 1, "completed_books": 2,
      "total_sheets_used": 90, "total_sheets_remaining": 10,
      "utilization_percentage": 90.0, "books_below_20_percent": 1
    }
  ],
  "total": 1, "page": 1, "page_size": 50, "generated_at": "2026-08-02T09:00:00"
}
```

Overall utilization computed client-side: `used / (used + remaining) × 100`.

---

## 6. Collection Efficiency

```
GET /reports/collection-efficiency?route_id=&min_outstanding=&preset=&from_date=&to_date=&format=json&refresh=false
```

**Response** (envelope):

```json
{
  "data": [
    {
      "customer_id": 5, "customer_code": "C00005", "customer_name": "Vikram", "route_name": "Route A",
      "total_billed": 4500.0, "total_paid": 3000.0, "balance": 1500.0, "collection_percentage": 66.67,
      "last_bill_date": "2026-07-31", "last_payment_date": "2026-07-20",
      "aging_current": 500.0, "aging_31_60": 700.0, "aging_61_90": 300.0, "aging_90_plus": 0.0
    }
  ],
  "total": 1, "page": 1, "page_size": 50, "generated_at": "2026-08-02T09:00:00"
}
```

Aging invariant: `aging_current + aging_31_60 + aging_61_90 + aging_90_plus === balance`.

## CSV

All list-style endpoints accept `&format=csv` and return `text/csv` with a
`Content-Disposition: attachment` header. The frontend requests these with `responseType: "blob"`
and downloads via a temporary anchor (see research R4).

## Error responses

- `401` — missing/expired token (shared client redirects to `/login`).
- `403 {"detail": "Access denied"}` — role not allowed, or DELIVERY_PARTNER requesting another route.
- `404 {"detail": "Customer not found"}` — consumption for unknown customer.
