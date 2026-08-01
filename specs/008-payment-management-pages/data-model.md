# Data Model: Payment Management Pages

**Date**: 2026-08-01 | **Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

This phase is frontend-only. The "data model" is the TypeScript type layer in `frontend/src/types/payment.ts`, which mirrors the existing Pydantic schemas in `app/schemas/payment.py` **exactly** (no new fields, no backend changes). All values below come from the backend response schemas.

## Entity: CustomerPayment

Mirrors `CustomerPaymentResponse` / `CustomerPaymentListResponse` (list variant joins customer for `customer_code`/`customer_name`).

| Field | Type | Notes / Source |
|---|---|---|
| `id` | `number` | |
| `customer_id` | `number` | |
| `customer_code` | `string` | list response only |
| `customer_name` | `string` | list response only |
| `payment_date` | `string` (ISO datetime) | **server-assigned**, not editable |
| `amount` | `number` (Decimal) | `> 0` |
| `payment_mode` | `"CASH" \| "UPI" \| "CARD" \| "CHEQUE" \| "BANK_TRANSFER"` | |
| `payment_type` | `"ADVANCE" \| "BILL_PAYMENT"` | `BILL_PAYMENT` requires `bill_id` |
| `reference_number` | `string \| null` | max 50 |
| `bill_id` | `number \| null` | null for ADVANCE |
| `is_active` | `boolean` | |
| `created_at` / `updated_at` | `string` | |

**Create payload** (`CustomerPaymentCreate`): `customer_id`, `amount`, `payment_mode`, `payment_type`, `reference_number?`, `bill_id?`, `remarks?`.

**Validation rules (backend-enforced, surfaced in UI)**:
- Customer must exist and be active → 404.
- `payment_mode` must be one of the 5 modes → 400.
- `payment_type` must be ADVANCE or BILL_PAYMENT → 400.
- `BILL_PAYMENT` requires an active, non-CANCELLED, non-PAID bill → 404/400.
- `ADVANCE` forces `bill_id = null`.

## Entity: CustomerBill

Mirrors `CustomerBillResponse` / `CustomerBillListResponse`.

| Field | Type | Notes |
|---|---|---|
| `id` | `number` | |
| `customer_id` | `number` | |
| `customer_code` / `customer_name` | `string` | list response only |
| `bill_date` | `string` (date) | server-assigned `current_date` |
| `bill_period_start` / `bill_period_end` | `string` (date) | generation window |
| `total_amount` | `number` | sum of line items |
| `paid_amount` | `number` | sum of active BILL_PAYMENTs |
| `balance_amount` | `number` | `total − paid` (can be 0; backend may carry negative on overpay — never shown negative) |
| `status` | `"PENDING" \| "PARTIAL" \| "PAID" \| "OVERDUE" \| "CANCELLED"` | auto-derived or manually set |
| `due_date` | `string (date) \| null` | |
| `remarks` | `string \| null` | |
| `is_active` | `boolean` | |
| `items` | `CustomerBillItem[]` | detail response only |

**Generate payload** (`BillGenerateRequest`): `customer_id`, `bill_period_start`, `bill_period_end`, `due_date?`, `remarks?`.

**State transitions (status)**:
- `PENDING` → generated initially.
- Auto-derived by payments: `PARTIAL` when `paid_amount > 0`, `PAID` when `balance ≤ 0`.
- Manually set via `PUT /payments/bills/{id}/status`: any of the 5 values (UI uses a confirmation; cancelling a bill with applied payments warns that payments remain recorded).

## Entity: CustomerBillItem

Mirrors `CustomerBillItemResponse` (nested in `CustomerBillResponse.items`).

| Field | Type | Notes |
|---|---|---|
| `id` | `number` | |
| `milk_type_id` | `number` | |
| `milk_name` | `string` | |
| `quantity` | `number` | total delivered qty in period |
| `unit_price` | `number` | milk type's current unit price |
| `amount` | `number` | `quantity × unit_price` |

## Entity: OutstandingBalance (derived view)

Mirrors `OutstandingBalanceResponse` from `GET /payments/outstanding/{customer_id}`.

| Field | Type | Notes |
|---|---|---|
| `customer_id` | `number` | |
| `customer_code` / `customer_name` | `string` | |
| `total_billed` | `number` | sum of active PENDING/PARTIAL/OVERDUE bills |
| `total_paid` | `number` | sum of all active payments |
| `balance` | `number` | `total_billed − total_paid` |
| `last_bill_date` | `string (date) \| null` | |
| `last_payment_date` | `string (datetime) \| null` | |

## Relations

- `CustomerBill 1 — N CustomerBillItem` (`items`).
- `CustomerBill 1 — N CustomerPayment` (payments link via `bill_id`; BILL_PAYMENTs recompute `paid_amount`/`balance_amount`/`status`).
- `OutstandingBalance` is derived per customer from bills + payments; cancelled bills are excluded from `total_billed`.

## Frontend constants (in `frontend/src/lib/constants.ts`)

- Reuse existing `PAYMENT_MODES = ["CASH","UPI","CARD","CHEQUE","BANK_TRANSFER"]`.
- Add `PAYMENT_TYPES = ["ADVANCE","BILL_PAYMENT"]` and `BILL_STATUS` badge map (`PENDING`, `PARTIAL`, `PAID`, `OVERDUE`, `CANCELLED`) merged into `STATUS_BADGE_MAP`.
