# Contract: Payments API (consumed by Phase 6 pages)

**Date**: 2026-08-01 | **Feature**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

The frontend consumes the existing backend router `app/routers/payments.py` (prefix `/api/v1/payments`). All endpoints below are **unchanged** — this document captures the exact contract the new `frontend/src/api/payments.ts` module must implement.

Auth note: the frontend axios client attaches `Authorization: Bearer <token>` and redirects to `/login` on 401. The backend currently does not enforce auth on this router (pre-existing gap, tracked separately).

## 1. Create Payment

- **POST** `/api/v1/payments/` → `201`
- **Request**: `CustomerPaymentCreate`
  ```json
  { "customer_id": 1, "amount": 500.00, "payment_mode": "UPI",
    "payment_type": "BILL_PAYMENT", "reference_number": "UTR123", "bill_id": 4, "remarks": null }
  ```
- **Response**: `CustomerPaymentResponse` (fields per `data-model.md`).
- **Errors**: 404 customer/bill not found; 400 invalid mode/type, bill already PAID or CANCELLED.

## 2. List Payments (history + filters)

- **GET** `/api/v1/payments/` → `200`
- **Query params** (all optional): `customer_id`, `payment_mode`, `payment_type`, `from_date`, `to_date` (dates as `YYYY-MM-DD`).
- **Response**: `CustomerPaymentListResponse[]` (includes `customer_code`, `customer_name`), ordered by `payment_date DESC`.

## 3. Get Payment

- **GET** `/api/v1/payments/{payment_id}` → `200` (`CustomerPaymentResponse`); `404` if not found/inactive.

## 4. Payments by Customer

- **GET** `/api/v1/payments/customer/{customer_id}` → `200` (`CustomerPaymentResponse[]`); `404` unknown customer.

## 5. Update Payment (NOT exposed in UI — immutability rule)

- **PUT** `/api/v1/payments/{payment_id}` — documented for completeness; the UI deliberately does not call it.

## 6. Delete Payment (NOT exposed in UI — immutability rule)

- **DELETE** `/api/v1/payments/{payment_id}` — soft delete; not called by the UI.

## 7. Generate Bill

- **POST** `/api/v1/payments/bills/generate` → `201`
- **Request**: `BillGenerateRequest`
  ```json
  { "customer_id": 1, "bill_period_start": "2026-07-01", "bill_period_end": "2026-07-31",
    "due_date": "2026-08-15", "remarks": null }
  ```
- **Response**: `CustomerBillResponse` (with `items`).
- **Errors**: 404 unknown customer; 400 no DELIVERED/CASH_SALE deliveries in period (`NoDeliveriesForBillError`) or milk type error.

## 8. List Bills

- **GET** `/api/v1/payments/bills/` → `200`
- **Query params** (all optional): `customer_id`, `status`, `from_date`, `to_date`.
- **Response**: `CustomerBillListResponse[]` (includes `customer_code`, `customer_name`), ordered by `bill_date DESC`.

## 9. Get Bill

- **GET** `/api/v1/payments/bills/{bill_id}` → `200` (`CustomerBillResponse` with `items`); `404` if not found/inactive.

## 10. Bills by Customer

- **GET** `/api/v1/payments/bills/customer/{customer_id}` → `200` (`CustomerBillResponse[]`); `404` unknown customer.

## 11. Update Bill Status

- **PUT** `/api/v1/payments/bills/{bill_id}/status` → `200`
- **Request**: `BillStatusUpdate`
  ```json
  { "status": "CANCELLED" }
  ```
- **Valid statuses**: `PENDING`, `PARTIAL`, `PAID`, `OVERDUE`, `CANCELLED`.
- **Response**: `CustomerBillResponse`.
- **Errors**: `404` bill not found; `400` invalid status.

## 12. Outstanding Balance (per customer)

- **GET** `/api/v1/payments/outstanding/{customer_id}` → `200`
- **Response**: `OutstandingBalanceResponse` (`total_billed`, `total_paid`, `balance`, `last_bill_date`, `last_payment_date`).
- **Errors**: `404` unknown customer.
- **Backend semantics (observed 2026-08-01)**: `total_billed` sums only bills with status `PENDING`/`PARTIAL`/`OVERDUE` (fully `PAID` and `CANCELLED` bills are excluded), while `total_paid` sums **all** active payments. Consequence: once a bill is fully paid, it drops out of `total_billed` but its payments remain in `total_paid`, so `balance` can become negative. The UI renders the response as-is (frontend-only phase).

## Frontend module surface (`frontend/src/api/payments.ts`)

```ts
listPayments(params?: { customer_id?; payment_mode?; payment_type?; from_date?; to_date? })
createPayment(data: CustomerPaymentCreate)
generateBill(data: BillGenerateRequest)
listBills(params?: { customer_id?; status?; from_date?; to_date? })
getBill(id: number)
updateBillStatus(id: number, status: BillStatus)
getOutstanding(customerId: number)
```

Reused from existing modules: `getCustomers()` (`api/customers.ts` + `useCustomers`) for customer dropdowns, and `useTokenBookPayments` is NOT used (different domain — customer payments are distinct from token-book payments).
