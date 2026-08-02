# Quickstart: Reports Pages Validation Guide

> Runnable validation scenarios to prove Phase 7 works end-to-end.
> Prerequisites and setup are shared with `specs/004-react-frontend/quickstart.md` (V1–V4).
> V11–V18 below are also automated by `frontend/e2e/reports.spec.ts` — run the whole suite with
> `cd frontend && npm run test:e2e` (45 tests; the isolated backend on :8001 resets the
> `milk_management_e2e` database each run).

## Prerequisites

- Backend running at `http://localhost:8000` (`uvicorn app.main:app --reload`)
- Database seeded (`python -m scripts.seed`) **and** a delivery session with DELIVERED/CASH_SALE
  deliveries created via the Delivery pages (reports only have numbers once delivery data exists).
- Frontend running at `http://localhost:5173` (`cd frontend && npm install && npm run dev`).

## Setup & gates

```bash
cd frontend
npm run lint        # expect: no errors
npm run build       # expect: tsc -b && vite build succeed
```

## Validation Scenarios

### V11: Dashboard is the landing page

1. Log in as `owner` / `owner123`.
2. **Expected**: you land on `/reports/dashboard` (URL) with a KPI grid: sessions, milk loaded,
   milk delivered, cash collected, deliveries-by-status, pending tokens, unclosed/unbalanced sessions.
3. Dashboard matches today's session/delivery data (compare with the Delivery → Sessions list).

### V12: Route Delivery report

1. Open **Reports → Route Delivery**.
2. Choose preset **This Week** and a route; click Refresh.
3. **Expected**: one row per route with session/delivery counts, loaded/delivered/token/cash/returned
   quantities, shortage/surplus, and a balanced indicator, plus a totals summary row.
4. Verify a row's numbers against the corresponding session detail page.

### V13: Revenue report (OWNER only)

1. As `owner`, open **Reports → Revenue** with preset **This Month**.
2. **Expected**: total revenue plus breakdowns by source, payment mode, route, and milk type with
   percentages; totals match recorded payments.
3. Apply a route filter → breakdown updates.
4. Log out; log in as `checker1` / `checker123` (CHECKER).
5. **Expected**: Revenue is absent from the menu; navigating to `/reports/revenue` directly shows the
   access-denied view. (Note: the seeded `admin` account has the OWNER role, so it does *not* test
   the Revenue denial — use `checker1` or `employee1`.)

### V14: Customer Consumption

1. Open **Reports → Consumption**; select a customer with deliveries and a date range.
2. **Expected**: daily quantities, total/average consumption, days with data, and a trend badge
   (Increasing / Declining / Stable).
3. Change the customer → report updates to that customer's data.

### V15: Token Utilization

1. Open **Reports → Token Utilization**.
2. **Expected**: per-customer sheets used/remaining, utilization % with a visual bar, books below
   threshold. Adjust `low_threshold` (e.g. 30) → the flagged count updates.

### V16: Collection Efficiency

1. Open **Reports → Collection Efficiency** with a date range.
2. **Expected**: per-customer billed/paid/balance, collection %, last bill/payment dates, and
   color-coded aging buckets (current, 31–60, 61–90, 90+). For each customer, the four buckets sum to
   their balance; overall collection % is shown.

### V17: CSV export

1. On **Route Delivery**, click the CSV/download button.
2. **Expected**: a `route-delivery-report-<date>.csv` file downloads whose rows match the on-screen
   table. Repeat on Token Utilization and Collection Efficiency.

### V18: Role restriction (DELIVERY_PARTNER)

1. Log in as `delivery1` / `delivery123` (DELIVERY_PARTNER).
2. **Expected**: Dashboard loads (own route scope); Route Delivery shows only the delivery partner's
   own route; Revenue, Token Utilization, and Collection Efficiency are not reachable.

## Expected outcomes

- All six report pages render with data from the backend (quickstart checkpoint from the parent spec).
- Build (`npm run build`) and lint (`npm run lint`) pass with no errors.
- Full validation matrix referenced from `contracts/reports-api.md` (roles, params, response shapes).

## Out of scope

- Backend report endpoints: already covered by `tests/test_reports.py` (24 tests).
- Frontend report pages: **automated** in `frontend/e2e/reports.spec.ts` (7 tests covering V11–V18),
  run as part of the full Playwright suite (`cd frontend && npm run test:e2e`, 45 tests). The E2E
  backend (`scripts/e2e_backend.py`, port :8001) sets `REPORT_CACHE_DISABLED=1` so the in-memory
  `app/services/reports/cache.py` report cache (TTL 300s, keyed by user) never serves stale
  zero-session data during the run.
