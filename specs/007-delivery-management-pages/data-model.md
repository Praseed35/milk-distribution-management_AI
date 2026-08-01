# Data Model: Delivery Management Pages (Phase 5)

**Feature**: 007-delivery-management-pages
**Date**: 2026-07-31

**Scope note**: This feature is primarily a frontend SPA. No new database entities are created. This document describes the entities the SPA consumes and the one backend behavior change (checklist generation at session create). All field lists below mirror the existing backend schemas exactly.

## 1. Delivery Session

Table `delivery_sessions` (`app/models/delivery_session.py`). One route's run for one date + shift.

| Field | Type | Notes |
|---|---|---|
| id | int | PK |
| route_id | int | FK routes; **unique with date+shift** (DB constraint `uq_session_route_date_shift` + service check) |
| delivery_date | date | YYYY-MM-DD |
| shift | str | MORNING / EVENING (regex-validated) |
| delivery_partner_id | int | FK employees |
| status | str | PLANNED / STARTED / COMPLETED / CLOSED |
| total_milk_loaded | decimal | liters, set at dispatch |
| total_token_registered | decimal | sum of DELIVERED quantities |
| total_cash_sales | decimal | set by reconciliation submit |
| total_returned_milk | decimal | set by reconciliation submit |
| reconciliation_status | str | PENDING / BALANCED / UNBALANCED |
| reopened_by / reopened_at | int? / datetime? | set by reopen |
| reopen_count | int | incremented on reopen |
| version | int | optimistic lock (no PUT endpoint currently) |
| is_active | bool | soft delete |
| created_at / updated_at | datetime | |

**Response shape** (`DeliverySessionResponse`): `{ id, route_id, route_name: null, delivery_date, shift, delivery_partner_id, delivery_partner_name: null, status, total_milk_loaded, total_token_registered, total_cash_sales, total_returned_milk, reconciliation_status, reopen_count, version, created_at, updated_at }`. `route_name`/`delivery_partner_name` always serialize null → SPA joins names client-side (research D5).

**State transitions** (defined in `delivery_service.VALID_SESSION_TRANSITIONS`):

```
PLANNED ──dispatch/start──▶ STARTED ──complete (NEW)──▶ COMPLETED ──close (balanced only)──▶ CLOSED
CLOSED ──reopen (OWNER, reason required)──▶ COMPLETED
```

- Dispatch/start: PLANNED only, `total_milk_loaded > 0`, once per session (400 if already recorded).
- Complete: STARTED only (400 otherwise). **New endpoint** `POST /deliveries/sessions/{id}/complete`.
- Close: COMPLETED only and `is_balanced` (|difference| < 0.01); otherwise 400 `SessionNotBalancedError` with the difference. Sets reconciliation_status=BALANCED.
- Reopen: CLOSED only, `reason` required (1–500 chars), increments reopen_count, logs SESSION_REOPEN edit. **Now OWNER-only** (403 otherwise).

**Checklist generation at create (backend fix 1)**: `create_session` now calls the repaired `generate_delivery_list()` which creates one `DailyDelivery` per active subscription on the session's route for the session's shift:
- planned_quantity = `morning_quantity` (MORNING) or `evening_quantity` (EVENING); subscriptions with 0 for that shift are skipped.
- Customers with an active exception (status ACTIVE, `start_date ≤ delivery_date ≤ COALESCE(end_date, delivery_date)`, `shift IS NULL OR shift = session.shift`) are excluded.
- `delivery_status="PLANNED"`, `delivery_source="PLANNED"`, `delivered_quantity=0`, `shift`/`delivery_date` copied from session.

## 2. Daily Delivery

Table `daily_deliveries` (`app/models/daily_delivery.py`). A single customer's line within a session.

| Field | Type | Notes |
|---|---|---|
| id | int | PK |
| session_id | int | FK delivery_sessions |
| customer_id | int | FK customers |
| milk_type_id | int | FK milk_types |
| planned_quantity | int | from subscription (0 for unplanned) |
| delivered_quantity | int | 0 until delivered |
| delivery_status | str | PLANNED (generated, UI "unregistered") / DELIVERED / PENDING_TOKEN / CASH_SALE / NOT_DELIVERED / CANCELLED |
| delivery_source | str | PLANNED / UNPLANNED |
| token_sheet_number | int? | set by token registration |
| token_book_issue_id | int? | FK token_book_issues |
| cash_amount | decimal? | for CASH_SALE |
| version | int | optimistic lock for PUTs |
| is_active | bool | soft delete |
| created_at / updated_at | datetime | |

**Two response variants — SPA uses the 15-field one** from `app/schemas/daily_delivery.py` (returned by `PUT /deliveries/{id}`, `POST /deliveries/unplanned`, `GET /deliveries/session/{id}`): `{ id, session_id, customer_id, customer_name: null, milk_type_id, milk_type_name: null, planned_quantity, delivered_quantity, delivery_status, delivery_source, token_sheet_number, token_book_issue_id, cash_amount, version, created_at, updated_at }`. The 8-field variant (delivery_session.py) lacks `version`/`cash_amount`/`milk_type_id` and is only used for the read-only session detail header.

**Per-row registration rules** (UI behavior):
- PLANNED → user selects a status:
  - DELIVERED: enter sheet number → `POST /validate-token` → if `requires_acknowledgment`, show warnings modal (codes, e.g. NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, NEW_BOOK_BEFORE_OLD_FINISHED) → `POST /{id}/register-token` with `acknowledged_warnings` + optional reason. Errors: sheet out of range / already used / no active book (400).
  - PENDING_TOKEN: `PUT /{id}` with `delivery_status="PENDING_TOKEN"`.
  - CASH_SALE: require `cash_amount > 0` → `PUT /{id}` with status + amount.
  - NOT_DELIVERED / CANCELLED: `PUT /{id}` with status.
- Unplanned rows: created via `POST /deliveries/unplanned` (status DELIVERED/PENDING_TOKEN/CASH_SALE, `registration_method` TOKEN_SHEET/CASH/PENDING, `reason` required).

## 3. Checklist (read-only, computed)

Returned by `GET /deliveries/sessions/{id}/checklist`:
`{ session_id, route_name: null, delivery_date, shift, total_expected, customers: [{ customer_id, customer_name, address, phone, milk_type, quantity }] }`. Mirrors the generated `daily_deliveries` rows for the session. Used by the SPA for the read-only "expected customers" summary and name/phone/address lookups.

## 4. Reconciliation (computed view)

Returned by `GET /deliveries/sessions/{id}/reconciliation`:
`{ session_id, loaded_milk, token_registered, cash_sales, returned_milk, total_accounted, difference, is_balanced, status }`.

Math: `token_registered` = Σ delivered_quantity where DELIVERED; `cash_sales` = Σ where CASH_SALE; `returned` = session.total_returned_milk; `loaded` = session.total_milk_loaded; `total_accounted = token + cash + returned`; `difference = loaded − accounted`; `is_balanced = |difference| < 0.01`; status PENDING/UNBALANCED/BALANCED.

`POST .../validate` → `{ can_close, is_balanced, issues: [{ code, message, severity }] }`; issue codes RECONCILIATION_MISMATCH (ERROR) and PENDING_TOKENS (WARNING). `can_close = is_balanced`.

`POST .../submit` (query params: `total_cash_collected`, `cash_sales`, `returned_milk`, `returned_reasons`, `token_sheets_collected`, `remarks`) → ReconciliationResponse; sets session totals.

`POST .../reconciliation/cash-sales` (query params: customer_name, customer_phone, milk_type_id, quantity, amount, payment_method=CASH) → creates/uses the special "Cash Customer" (`customer_code="C_CASH"`) and an UNPLANNED CASH_SALE delivery; `DELETE .../cash-sales/{id}` soft-deletes it.

## 5. Token Book Issue (consumed, read/reference only)

Table `token_book_issues`; SPA reads via `GET /deliveries/customer/{customer_id}/token-status` → `{ token_books: [{ book_issue_id, book_number, milk_type, issue_date, status, sheets_used, sheets_remaining, is_old_book }], has_old_book_with_remaining, old_book_remaining }` and token validation responses. Registration advances the book's `current_sheet` server-side; warnings are logged to `token_sheet_warnings` and retrievable via `GET /deliveries/{delivery_id}/warnings`.

## 6. Session Edit (audit trail)

Table `session_edits` (via `delivery_edit_service`). Returned by `GET /deliveries/session/{id}/edit-history` as a **raw list** (no wrapper): `[{ edit_id, delivery_id, customer_name, edit_type: "STATUS_CHANGE"|"SESSION_REOPEN", old_value, new_value, reason, edited_by, edited_at }]`, ordered newest-first. Written by reopen (SESSION_REOPEN) and `PUT /deliveries/{id}/edit` (STATUS_CHANGE, reason required, `return_token_sheet` decrements the book's current_sheet and clears the delivery's sheet).
