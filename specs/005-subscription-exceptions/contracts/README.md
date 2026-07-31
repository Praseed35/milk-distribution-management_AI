# API Contracts — Subscription & Exceptions Pages

> Frontend-to-backend contracts for this feature. All paths are under `/api/v1` (existing backend). DTO field definitions in [`data-model.md`](../data-model.md).

## Base URL

```
/api/v1
```

All requests carry `Authorization: Bearer <token>` (attached by the existing Axios interceptor). No new backend endpoints.

## Subscriptions

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/subscriptions/` | — | `SubscriptionListResponse[]` | plain array, flat joined fields |
| GET | `/subscriptions/customer/{id}` | — | `SubscriptionListResponse[]` | filter by customer |
| GET | `/subscriptions/{id}` | — | `SubscriptionDetailResponse` | nested customer + milk_type |
| POST | `/subscriptions/` | `SubscriptionCreate` | `SubscriptionResponse` (201) | do NOT send `start_date`/`end_date` |
| PUT | `/subscriptions/{id}` | `SubscriptionUpdate` | `SubscriptionResponse` | |
| DELETE | `/subscriptions/{id}` | — | `SubscriptionResponse` | soft delete → `is_active=false` |

**Create body** (`SubscriptionCreate`):

```json
{
  "customer_id": 1,
  "milk_type_id": 2,
  "morning_quantity": 2,
  "evening_quantity": 1,
  "status": "ACTIVE",
  "remarks": null
}
```

## Delivery Exceptions

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/delivery-exceptions/` | — | `DeliveryExceptionListResponse[]` | plain array, flat joined fields |
| GET | `/delivery-exceptions/subscription/{id}` | — | `DeliveryExceptionResponse[]` | filter by subscription |
| GET | `/delivery-exceptions/{id}` | — | `DeliveryExceptionDetailResponse` | nested subscription |
| POST | `/delivery-exceptions/` | `DeliveryExceptionCreate` | `DeliveryExceptionResponse` (201) | |
| PUT | `/delivery-exceptions/{id}` | `DeliveryExceptionUpdate` | `DeliveryExceptionResponse` | |
| DELETE | `/delivery-exceptions/{id}` | — | `DeliveryExceptionResponse` | soft delete → `is_active=false` |

**Create body** (`DeliveryExceptionCreate`):

```json
{
  "subscription_id": 3,
  "exception_type": "VACATION",
  "shift": "MORNING",
  "start_date": "2026-08-01T00:00:00",
  "end_date": "2026-08-05T00:00:00",
  "reason": "Family trip"
}
```

- `shift` is optional (`"MORNING"` | `"EVENING"` | `null`). `null`/omitted = whole day. Server validates against the `Shift` enum (invalid value → 422).
- `shift` on `PUT` is updatable and can be cleared back to whole day by sending `"shift": null`.
- Overlap rule (same subscription, active, date-overlapping): a whole-day exception conflicts with every shift; a shift-specific exception only conflicts with the same shift or with whole-day exceptions.

## Error Responses

| Status | Shape | Meaning | UI Handling |
|---|---|---|---|
| 400 | `{"detail": "..."}` | overlap / inactive subscription / invalid dates / duplicate | error toast with `detail`; form stays open |
| 404 | `{"detail": "..."}` | subscription/exception not found | error toast |
| 422 | `{"detail": [{loc,msg,type}]}` | field validation failure | mapped to inline field errors where possible, else toast |
| 401 | — | expired/invalid token | existing interceptor → login redirect |

## Response Format Notes

- List endpoints return **plain arrays** — no envelope, no pagination. The API modules type them directly and the DataTable renders the full array with client-side sorting.
- Single-resource endpoints return the resource DTO directly (no `{success, data}` envelope) for these routers.
- Route-level filtering (subscriptions by route, exceptions by customer/route) is **client-side** over the list DTOs — the backend accepts no such query params (known backend gap).

## Reference Implementation Patterns (existing frontend)

Follow the established Phase 2 patterns in `frontend/src/api/customers.ts`, `frontend/src/hooks/useCustomers.ts`, and `frontend/src/pages/customers/CustomerListPage.tsx` — same shape for these two modules.
