# Quickstart: Delivery Management Pages (Phase 5)

**Feature**: 007-delivery-management-pages
**Date**: 2026-07-31

## Overview

Validation guide for the Phase 5 React SPA pages and the three small backend fixes shipped with them. It proves the end-to-end workflow: **create → (checklist auto-generated) → dispatch → register statuses/tokens → reconcile → complete → close**, plus the **OWNER-only reopen/edit** flow.

Contract details: [contracts/sessions.md](./contracts/sessions.md), [contracts/deliveries.md](./contracts/deliveries.md). Data/state model: [data-model.md](./data-model.md).

## Prerequisites

1. PostgreSQL running; backend started (`uvicorn app.main:app --reload`); DB migrated (no new migrations).
2. `frontend/` deps installed; dev server `npm run dev` on `http://localhost:5173` (proxies `/api/v1`).
3. Seed data: at least one route, 2+ customers on that route with **ACTIVE subscriptions** (`morning_quantity > 0`), a milk type, an employee with `role="DELIVERY_PARTNER"`, and a token book identity + ACTIVE issue with sheets remaining for the token-registration scenario. One customer may have an ACTIVE VACATION/NO_MILK exception covering today.
4. Log in as OWNER (and CHECKER for the daily-flow scenarios).

## Backend verification (pytest)

```bash
python -m pytest tests/test_daily_delivery.py tests/test_delivery_edit.py -q
```

Expected: **all pass**, including the new tests:
- create_session auto-generates planned checklist rows (shift-correct quantities, exception excluded, duplicate session still 400)
- complete endpoint: STARTED→COMPLETED; 400 when not STARTED
- close-after-complete: balanced closes, unbalanced 400 with difference
- edit/reopen: 403 for CHECKER/ADMIN; 200 for OWNER

## Frontend verification

```bash
cd frontend
npm run build    # tsc -b && vite build — type-safe against the mirrored contracts
npm run lint     # oxlint
```

Both must pass cleanly.

## Scenario 1 — Normal morning delivery (CHECKER) — SC-001, SC-005

1. **Navigation**: Sign in as CHECKER → sidebar "Delivery → Sessions" (visible; DELIVERY_PARTNER cannot see the page).
2. **Create session**: `/delivery/sessions/new` → select route, today's date, shift **MORNING**, delivery partner → Save. Toast success; redirect to the list; the new row shows status **PLANNED** and today's date.
3. **Checklist generated**: open the session → Dispatch section enabled (PLANNED). Expected-customers summary shows the subscribed customers with their morning quantities and `total_expected > 0`; the VACATION/NO_MILK customer is absent.
4. **Dispatch**: enter `total_milk_loaded` (sum of expected quantities) → confirm. Status becomes **STARTED**; Dispatch section hides; Checklist + Reconciliation sections become usable. Dispatch button must not reappear (dispatch-once).
5. **Register statuses**:
   - Customer A → **DELIVERED**: type sheet number → client `validate-token` → no warnings → `register-token` → row shows DELIVERED + sheet number; reconciliation `token_registered` increases.
   - Customer B → **CASH_SALE**: enter amount (> 0) → row shows CASH_SALE + amount.
   - Customer C → **PENDING_TOKEN**.
   - Customer D → **NOT_DELIVERED**.
   - Add unplanned: "Add Unplanned Delivery" → existing customer or walk-in cash customer (name/phone/milk type/qty/amount, reason required) → appears with `source=UNPLANNED` and counts in reconciliation.
6. **Out-of-sequence sheet (warning + acknowledgment)**: enter a sheet number ahead of the book's current sheet → warnings modal shows NON_SEQUENTIAL_SHEET; **registration is blocked until acknowledged**; acknowledge → `register-token` succeeds with `acknowledged_warnings`; the warning appears in the row's warning log.
7. **Reconcile**: Reconciliation section shows loaded / token-registered / cash-sales / returned / accounted / difference. Enter returned milk if any (e.g., to balance C's pending quantity). **Validate** → issues listed (RECONCILIATION_MISMATCH while unbalanced). Adjust until **BALANCED**.
8. **Complete**: "Complete session" → status **COMPLETED**.
9. **Close**: "Close session" → ConfirmDialog → status **CLOSED**, read-only; Summary section shows the report (counts by status + milk totals). Attempting to change a row after close is rejected (controls disabled / 400).

**Pass criteria**: whole workflow under 5 minutes; close accepted only when BALANCED (SC-002); out-of-sequence never registers silently (SC-003).

## Scenario 2 — Duplicate session (edge case)

On the list page, attempt to create the same route + date + shift again → clear error toast, no session created. On the list, filter by date / route / status → only matching sessions shown.

## Scenario 3 — Owner reopen & edit (SC-004) — P2

1. Sign in as **OWNER**, open a CLOSED session → "Reopen" button visible; **reason is required** (empty reason blocked client-side + 400 server-side). Reopen → status **COMPLETED**, `reopen_count` increments; session editable.
2. Edit a DELIVERED row (e.g., set **NOT_DELIVERED** with `return_token_sheet: true`) → reason required; token sheet returned (book current_sheet decremented), edit recorded.
3. Check **edit history** on the session → STATUS_CHANGE and SESSION_REOPEN entries with reason/editor/timestamp.
4. Reconcile + close again → reconciliation recalculated; closes only when balanced.
5. As **CHECKER**: edit/reopen buttons are absent and direct API calls return **403**.

## Scenario 4 — Empty checklist (edge case)

Create a session on a route with no active subscriptions (or all excepted) → session still opens; checklist shows the EmptyState; the route can be dispatched/reconciled/closed as long as loaded = accounted (0 or via returned/cash).

## Not verified here

- Backend token-registration internals (already covered by the existing suite in `tests/test_daily_delivery.py`).
- Real-device/browser performance metrics; SC-001/SC-005 are manual timing checks.
