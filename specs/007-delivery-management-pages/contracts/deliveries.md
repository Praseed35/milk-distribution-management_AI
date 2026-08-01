# Contracts: Deliveries (Registration, Token Sheets, Edit & Reopen)

**Feature**: 007-delivery-management-pages
**Date**: 2026-07-31
**Base URL (SPA)**: `/api/v1`.

**Auth**: `PUT /deliveries/{id}/edit` and `POST /deliveries/session/{id}/reopen` require a valid token and, **after this feature's backend fix**, are **OWNER-only** (403 otherwise). All other endpoints in this file have no auth dependency (inherited). The SPA gates all pages via `RoleGuard` and sends the bearer token always.

**DailyDeliveryResponse (15-field)** — returned by `PUT /deliveries/{id}`, `POST /deliveries/unplanned`, `GET /deliveries/session/{id}`:
```ts
{
  id: number; session_id: number; customer_id: number; customer_name: string | null;
  milk_type_id: number; milk_type_name: string | null; planned_quantity: number;
  delivered_quantity: number; delivery_status: "DELIVERED" | "PENDING_TOKEN" | "CASH_SALE" |
    "NOT_DELIVERED" | "CANCELLED" | "PLANNED";
  delivery_source: "PLANNED" | "UNPLANNED"; token_sheet_number: number | null;
  token_book_issue_id: number | null; cash_amount: number | null; version: number;
  created_at: string; updated_at: string;
}
```
`customer_name`/`milk_type_name` always null — join client-side. The 8-field variant on the session-detail endpoint must NOT be used for editing (no `version`/`cash_amount`/`milk_type_id`).

---

## Registration (open session)

### PUT `/deliveries/{delivery_id}` → 200
Body:
```json
{ "delivery_status": "CASH_SALE", "delivered_quantity": 1, "token_sheet_number": null,
  "cash_amount": 25.00, "remarks": null, "version": 1 }
```
All fields optional except as needed (`delivery_status` ∈ 5 statuses — PLANNED not accepted; `delivered_quantity` ge 0; `remarks` max 500). Response: `DailyDeliveryResponse`. Errors: 404 `Delivery {id} not found`; 400 `Invalid token sheet: ...`; 409 `Session was modified by another user. Please reload and try again.` (version mismatch). Success bumps `version`.

**Usage**: mark a checklist row PENDING_TOKEN / CASH_SALE (with `cash_amount`) / NOT_DELIVERED / CANCELLED. DELIVERED rows go through `register-token` instead.

### POST `/deliveries/{delivery_id}/register-token` → 200
Body:
```json
{ "token_sheet_number": 3, "acknowledged_warnings": ["NON_SEQUENTIAL_SHEET"], "acknowledgment_reason": "Ok" }
```
`token_sheet_number` gt 0; `acknowledged_warnings` list of codes; `acknowledgment_reason` max 500.
Response:
```json
{ "delivery_id": 1, "sheet_registered": true, "token_book_issue_id": 12,
  "new_current_sheet": 4, "warnings_logged": 1, "message": "Token sheet registered" }
```
Sets the delivery DELIVERED, `delivered_quantity = planned_quantity`, links the book issue, advances `current_sheet`. Errors: 404 delivery; 400 `Warnings require acknowledgment: CODE1, CODE2` (when warnings exist and none acknowledged); 400 `Invalid token sheet: No active token book found...`; 400 `Sheet {n} is already used in book {id}`; 400 `Sheet {n} is out of range (max: {m})`.

### POST `/deliveries/validate-token` → 200 (client-side pre-check before register)
Body: `{ "customer_id": 1, "milk_type_id": 1, "sheet_number": 3, "token_book_issue_id": null }`.
Response:
```json
{ "is_valid": true, "can_proceed": true, "requires_acknowledgment": true,
  "warnings": [ { "code": "NON_SEQUENTIAL_SHEET", "message": "Sheet #3 skips ahead...",
                  "severity": "WARNING", "expected_sheet": 2 } ] }
```
Warning codes: NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, GAP_DETECTED, SHEET_ALREADY_USED, NEW_BOOK_BEFORE_OLD_FINISHED. Any warning → `requires_acknowledgment=true`; `is_valid = warnings empty OR requires_acknowledgment`. Errors: 404 customer/milk-type; 400 invalid/used/out-of-range sheet.

### POST `/deliveries/unplanned` → 201
Body:
```json
{ "session_id": 1, "customer_id": 10, "milk_type_id": 1, "delivered_quantity": 1,
  "delivery_status": "DELIVERED", "registration_method": "TOKEN_SHEET",
  "token_sheet_number": 5, "reason": "Walk-in customer" }
```
`delivery_status` ∈ DELIVERED/PENDING_TOKEN/CASH_SALE; `registration_method` ∈ TOKEN_SHEET/CASH/PENDING; `reason` required 1–500. Response: `DailyDeliveryResponse` with `delivery_source="UNPLANNED"`, `planned_quantity=0`. Errors: 404 session/customer/milk-type; 400 `Invalid token sheet` / `Sheet out of range`.

### GET `/deliveries/session/{session_id}?status=&skip=0&limit=100` → 200
```json
{ "session_id": 1, "deliveries": [ DailyDeliveryResponse ], "total": 3 }
```
**Primary checklist source for the registration table** (15-field, both PLANNED and UNPLANNED rows).

### GET `/deliveries/{delivery_id}/warnings` → 200
```json
{ "delivery_id": 1, "warnings": [ { "id": 1, "warning_code": "NON_SEQUENTIAL_SHEET",
  "warning_message": "...", "sheet_number": 3, "expected_sheet": 2,
  "acknowledged_by": null, "acknowledged_at": null } ] }
```

### GET `/deliveries/customer/{customer_id}/token-status` → 200
```json
{ "customer_id": 10, "customer_name": null,
  "token_books": [ { "book_issue_id": 12, "book_number": "BK-001-001", "milk_type": "Cow Milk",
      "issue_date": "2026-07-01", "status": "ACTIVE", "sheets_used": 2, "sheets_remaining": 28,
      "is_old_book": false } ],
  "has_old_book_with_remaining": false, "old_book_remaining": 0 }
```
404 if customer missing.

---

## Owner edit & reopen (post-close corrections)

### POST `/deliveries/session/{session_id}/reopen` → 200 — **OWNER only**
Body: `{ "reason": "Customer complaint" }` (1–500).
Response: `DeliverySessionResponse` with `status="COMPLETED"`, `reopen_count` incremented, `reopened_by/at` set; logs SESSION_REOPEN edit. Errors: 404; 400 `InvalidSessionStatusError` (must be CLOSED); 403 non-OWNER.

### PUT `/deliveries/{delivery_id}/edit` → 200 — **OWNER only**
Body:
```json
{ "delivery_status": "NOT_DELIVERED", "return_token_sheet": true, "reason": "Customer said no milk", "version": 1 }
```
`reason` required 1–500; `return_token_sheet` decrements the book's `current_sheet` (min 1) and clears the delivery's sheet. Session must be COMPLETED or CLOSED.
Response:
```json
{ "delivery_id": 1, "old_status": "DELIVERED", "new_status": "NOT_DELIVERED",
  "token_sheet_returned": true, "token_book_issue_id": 12, "sheet_number": 3,
  "new_current_sheet": 2, "message": "Delivery updated" }
```
Errors: 404; 409 version mismatch; 400 invalid status/sheet; 403 non-OWNER.

### GET `/deliveries/session/{session_id}/edit-history` → 200
**Raw list** (no wrapper):
```json
[ { "edit_id": 1, "delivery_id": 5, "customer_name": null, "edit_type": "STATUS_CHANGE",
    "old_value": { "status": "DELIVERED", "token_sheet": 3 },
    "new_value": { "status": "NOT_DELIVERED", "token_sheet": null },
    "reason": "Customer said no milk", "edited_by": "owner1", "edited_at": "2026-07-31T09:00:00Z" } ]
```
`edit_type` ∈ STATUS_CHANGE | SESSION_REOPEN. Ordered newest-first.

---

## SPA consumption summary

- Checklist registration table → `GET /deliveries/session/{id}`; per-row edits → `PUT /deliveries/{id}` or `POST /deliveries/{id}/register-token`
- Token pre-check → `POST /deliveries/validate-token` (drives the acknowledgment modal); warnings log → `GET /deliveries/{id}/warnings`
- Unplanned → `POST /deliveries/unplanned`
- Owner corrections → `POST /deliveries/session/{id}/reopen`, `PUT /deliveries/{id}/edit`, history → `GET /deliveries/session/{id}/edit-history`
- Token book display for a row → `GET /deliveries/customer/{customer_id}/token-status`
