# Quickstart: Payment Management Pages — Validation Guide

**Date**: 2026-08-01 | **Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

End-to-end validation scenarios for Phase 6. References [contracts/payments-api.md](contracts/payments-api.md) and [data-model.md](data-model.md). Full implementation detail lives in `tasks.md`; this is a run/verify guide.

## Prerequisites

- Backend running against a Postgres DB (dev: `python -m scripts.seed` after initializing).
- Frontend dev server running (proxy `/api` → backend; `changeOrigin: false`).
- Login as `owner / owner123` (or `admin / admin123`).

## Manual validation flows

### Flow 1 — Record an ADVANCE payment

1. Navigate **Finance → Payments → Create Payment**.
2. Choose a customer, payment type `ADVANCE`, amount `500.00`, mode `CASH`, optional reference/remarks.
3. Save → redirected to the list; the new row shows customer, amount, mode `CASH`, type `ADVANCE`, system date, and **no** linked bill.
4. Expected: success toast; history reflects the payment. *(FR-003, FR-006)*

### Flow 2 — Generate a bill, then pay it (BILL_PAYMENT)

1. Ensure the chosen customer has DELIVERED deliveries in a date range (create a delivery session via **Delivery → Sessions** and register DELIVERED rows, per the Phase 5 flow).
2. Navigate **Finance → Bills → Generate Bill**: select the customer, set period start/end covering the deliveries, generate.
3. Expected: bill created with line items per milk type and a correct total; appears in **Bills** list with status `PENDING`.
4. Open the bill detail → note line items and totals. *(FR-009, FR-010, FR-011, FR-014)*
5. **Finance → Payments → Create Payment**, type `BILL_PAYMENT`, select the bill, pay its balance.
6. Expected: bill shows `paid_amount = balance`, `balance_amount = 0`, status `PAID`. *(FR-007, SC-002)*
7. Re-open **Outstanding** → the customer's `balance` decreased by the payment; `last_payment_date` updated. *(FR-017, FR-018, SC-005)*
   - Note: the backend excludes fully-`PAID` bills from `total_billed` while `total_paid` counts all payments, so a fully-paid bill shows a negative `balance` in Outstanding (observed 2026-08-01; frontend renders the API response as-is).

### Flow 3 — No-deliveries bill generation

1. On **Generate Bill**, include a customer with no deliveries in the selected period.
2. Expected: no bill for that customer; the page explains the reason; other selected customers still generate. *(FR-012, SC-003)*

### Flow 4 — Bill status management

1. From a bill's detail, change status to `OVERDUE`, confirm.
2. Expected: list shows `OVERDUE` badge. *(FR-015)*
3. Cancel a bill that has applied payments → confirmation warns payments remain recorded; after acknowledging, status is `CANCELLED` and the customer's outstanding `total_billed` no longer includes it. *(FR-016, Edge Cases)*

### Flow 5 — Filters and access control

1. **Payments** and **Bills** lists filter by customer / mode or status / date range. *(FR-001, FR-002, FR-009)*
2. Log in as `checker1 / checker123`: Finance menu absent; direct URL `/payments` shows the access-denied view. *(FR-019, SC-006)*

## Automated validation (Playwright E2E)

Suite runner: from repo root, start E2E backend (`scripts/e2e_backend.py`, DB `milk_management_e2e` reseeded each run) + Vite on 5174, then `npx playwright test` in `frontend/`. Full instructions: `.ai/14_testing_guidelines.md`.

`payments.spec.ts` must cover:
- Setup: create a delivery session and mark deliveries DELIVERED (reuse the Phase 5 flow) so bill generation has data; login as owner.
- Record ADVANCE payment → appears in history.
- Generate bill → appears in Bills list with expected total.
- Record BILL_PAYMENT → bill becomes PAID; outstanding balance reflects it.
- Bill status update with confirmation (mark `OVERDUE`).
- Negative checks: BILL_PAYMENT without a bill blocked; no-delivery generation shows the explanation and creates no bill.
- Role check: CHECKER cannot access `/payments` (via `checker` auth state).

Expected: new spec passes alongside the existing 32 green specs; `npx tsc -b` clean; `oxlint` reports no new issues.

## Acceptance criteria mapping

| Quickstart flow | Spec FR / SC |
|---|---|
| Flow 1 | FR-003, FR-006, SC-001 |
| Flow 2 | FR-007, FR-009–011, FR-014, FR-017–018, SC-002, SC-005 |
| Flow 3 | FR-012, SC-003 |
| Flow 4 | FR-015–016 |
| Flow 5 | FR-001–002, FR-009, FR-019, SC-004, SC-006 |
| E2E | SC-002, SC-003, SC-006, SC-007 |
