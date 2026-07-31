# API Contracts — Token Book Pages

> Frontend-to-backend contracts for this feature. All paths are under `/api/v1` (existing backend). DTO field definitions in [`data-model.md`](../data-model.md).

## Base URL

```
/api/v1
```

All requests carry `Authorization: Bearer <token>` (attached by the existing Axios interceptor). No new backend endpoints.

## Token Identities

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/token-books/identities/` | — | `TokenIdentityListResponse[]` | plain array, flat joined fields, `is_active=true` only |
| GET | `/token-books/identities/customer/{id}` | — | `TokenIdentityResponse[]` | filter by customer (non-flat shape — used only if needed) |
| GET | `/token-books/identities/{id}` | — | `TokenIdentityDetailResponse` | nested customer + milk_type |
| POST | `/token-books/identities/` | `TokenIdentityCreate` | `TokenIdentityResponse` (201) | duplicate customer+milk+token → 400 |
| PUT | `/token-books/identities/{id}` | `TokenIdentityUpdate` | `TokenIdentityResponse` | updates `token_number` only |
| DELETE | `/token-books/identities/{id}` | — | `TokenIdentityResponse` | soft delete → `is_active=false` |

**Create body** (`TokenIdentityCreate`):

```json
{
  "customer_id": 1,
  "milk_type_id": 2,
  "token_number": 100
}
```

## Token Book Issues

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/token-books/issues/` | — | `TokenBookIssueListResponse[]` | plain array, flat joined fields |
| GET | `/token-books/issues/identity/{id}` | — | `TokenBookIssueResponse[]` | filter by identity (non-flat shape) |
| GET | `/token-books/issues/{id}` | — | `TokenBookIssueDetailResponse` | nested token_identity |
| POST | `/token-books/issues/` | `TokenBookIssueCreate` | `TokenBookIssueResponse` (201) | active book exists → 400; duplicate issue number → 400 |
| PUT | `/token-books/issues/{id}` | `TokenBookIssueUpdate` | `TokenBookIssueResponse` | status / current_sheet / completion_date / remarks |
| DELETE | `/token-books/issues/{id}` | — | `TokenBookIssueResponse` | soft delete → `is_active=false` |

**Create body** (`TokenBookIssueCreate`):

```json
{
  "token_identity_id": 1,
  "issue_number": 5,
  "remarks": null
}
```

- `issue_date`, `current_sheet` (0), `status` ("WAITING") are backend-assigned on create; never sent.
- Status values: `WAITING` | `ACTIVE` | `COMPLETED`.

## Token Book Payments

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| GET | `/token-books/payments/` | — | `TokenBookPaymentListResponse[]` | plain array, flat joined fields |
| GET | `/token-books/payments/issue/{id}` | — | `TokenBookPaymentResponse[]` | filter by issue (non-flat shape) |
| GET | `/token-books/payments/{id}` | — | `TokenBookPaymentDetailResponse` | nested token_book_issue |
| POST | `/token-books/payments/` | `TokenBookPaymentCreate` | `TokenBookPaymentResponse` (201) | `amount_paid` > `book_price` → 400 |
| PUT | `/token-books/payments/{id}` | `TokenBookPaymentUpdate` | `TokenBookPaymentResponse` | recomputes `balance_amount` + `payment_status` |
| DELETE | `/token-books/payments/{id}` | — | `TokenBookPaymentResponse` | soft delete → `is_active=false` |

**Create body** (`TokenBookPaymentCreate`):

```json
{
  "token_book_issue_id": 1,
  "payment_mode": "PREPAID",
  "book_price": 100,
  "amount_paid": 100,
  "remarks": null
}
```

- `payment_mode`: `PREPAID` | `POSTPAID` (constant `TOKEN_PAYMENT_MODES` already in `frontend/src/lib/constants.ts`).
- `payment_status` (PAID / PARTIAL / PENDING) and `balance_amount` are computed server-side: balance ≤ 0 → PAID; amount_paid > 0 → PARTIAL; else PENDING.

## Error Responses

| Status | Shape | Meaning | UI Handling |
|---|---|---|---|
| 400 | `{"detail": "..."}` | duplicate identity / active book exists / duplicate issue number / invalid payment amount | error toast with `detail`; form stays open |
| 404 | `{"detail": "..."}` | customer/milk type/identity/issue/payment not found | error toast |
| 422 | `{"detail": [{loc,msg,type}]}` | field validation failure | mapped to inline field errors where possible, else toast |
| 401 | — | expired/invalid token | existing interceptor → login redirect |

## Response Format Notes

- List endpoints return **plain arrays** — no envelope, no pagination. The API modules type them directly and the DataTable renders the full array with client-side sorting.
- Single-resource endpoints return the resource DTO directly (no `{success, data}` envelope) for these routers.
- Customer/milk-type/identity/issue filters are **client-side** over the flat list DTOs — the list endpoints accept no query params, and the dedicated filter endpoints return non-flat shapes (known backend gap).

## Reference Implementation Patterns (existing frontend)

Follow the established Phase 3 patterns in `frontend/src/api/subscriptions.ts`, `frontend/src/hooks/useSubscriptions.ts`, and `frontend/src/pages/subscriptions/SubscriptionListPage.tsx` — same shape for these three modules.
