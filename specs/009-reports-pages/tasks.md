---

description: "Task list for Reports Pages (Phase 7 React SPA, frontend-only)"

---

# Tasks: Reports Pages

**Input**: Design documents from `/specs/009-reports-pages/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/reports-api.md, quickstart.md

**Tests**: No backend tests — this phase adds zero backend code (Sprint 7 backend reports already covered by `tests/test_reports.py`, 24 tests). Frontend verification is `cd frontend && npm run build` (tsc -b + vite build) and `npm run lint` per task checkpoint, plus automated Playwright E2E coverage for quickstart scenarios V11–V18 in `frontend/e2e/reports.spec.ts` (7 tests, run with `npm run test:e2e` from `frontend/`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend: `frontend/src/...` (React SPA — `types → api → hooks → pages`)
- Mirror existing conventions from Phase 6 (`types/payment.ts`, `api/payments.ts`, `hooks/usePayments.ts`, payments pages) and Phase 5 (delivery pages)
- Backend: NOT touched — `app/routers/reports.py` and `app/services/reports/*` consumed unchanged

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline verification plus the shared type/constants layer. No project initialization needed (existing Vite React SPA).

- [x] T001 Verify frontend baseline: run `cd frontend && npm run build && npm run lint` — must be clean before feature work starts
- [x] T002 [P] Add `REPORT_PRESETS` to `frontend/src/lib/constants.ts` — array of `{ value, label }` for `today | yesterday | this_week | last_week | this_month | last_month | this_year` (labels "Today"/"Yesterday"/"This Week"/"Last Week"/"This Month"/"Last Month"/"This Year") — mirror the backend `resolve_date_range` presets (research R3)
- [x] T003 [P] Create `frontend/src/types/reports.ts` — interfaces mirroring `app/schemas/reports.py` + `data-model.md` exactly (snake_case): `ReportEnvelope<T>` (`data`, `total`, `page`, `page_size`, `generated_at`), `OperationalDashboard` (incl. `deliveries_by_status: Record<...>`), `RouteDeliveryItem`, `RevenueBreakdown`, `RevenueReport` (incl. `by_source`/`by_payment_mode`/`by_route`/`by_milk_type`), `ConsumptionDay`, `ConsumptionTrend`, `CustomerConsumptionReport`, `TokenUtilizationItem`, `CustomerCollectionItem`, plus params interfaces `ReportDateParams` (`preset?`, `from_date?`, `to_date?`, `refresh?`), `RouteDeliveryParams`, `RevenueParams`, `ConsumptionParams`, `TokenUtilizationParams`, `CollectionEfficiencyParams`

**Checkpoint**: `cd frontend && npx tsc -b` passes; types are the single source of truth for all API calls (Principle V).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared API module, hooks, and small report UI primitives every report page consumes. **⚠️ CRITICAL**: No user story can work end-to-end until these complete.

- [x] T004 Create `frontend/src/api/reports.ts` — fetchers returning `response.data`, mirroring `api/payments.ts` style: `getDashboard(refresh?)` (GET `/reports/dashboard`), `getRouteDelivery(params?)` (GET `/reports/route-delivery`), `getRevenue(params?)` (GET `/reports/revenue`), `getConsumption(customerId, params?)` (GET `/reports/customer/{customerId}/consumption`), `getTokenUtilization(params?)` (GET `/reports/token-utilization`), `getCollectionEfficiency(params?)` (GET `/reports/collection-efficiency`); plus `downloadReportCsv(path, params, filename)` that calls the endpoint with `params: { ...params, format: "csv" }` and `responseType: "blob"` then triggers a download via `URL.createObjectURL` + temporary `<a download>` anchor (research R4)
- [x] T005 Create `frontend/src/hooks/useReports.ts` — TanStack Query hooks following `usePayments.ts` pattern, each taking a params object and including `refresh` in the query key so a refresh re-fetches: `useDashboard(refresh?)` (key `["reports", "dashboard", refresh]`), `useRouteDelivery(params?)` (key `["reports", "route-delivery", params]`), `useRevenue(params?)`, `useConsumption(customerId, params?)` (key `["reports", "consumption", customerId, params]`, `enabled: !!customerId`), `useTokenUtilization(params?)`, `useCollectionEfficiency(params?)`
- [x] T006 [P] Create `frontend/src/components/reports/` shared primitives (new directory): `KpiCard.tsx` (title, value, optional sub-label/color), `PresetFilter.tsx` (preset `Select` OR from/to date `Input`s — mutually exclusive per research R3 — plus an optional "Refresh" button wired to `refresh: true`), `TrendBadge.tsx` (renders Increasing/Declining/Stable from `change_percentage`, threshold |5%|, per research R9), `UtilizationBar.tsx` (percentage bar with color by threshold), `AgingBuckets.tsx` (four color-coded buckets that sum to balance)

**Checkpoint**: `cd frontend && npx tsc -b` passes with the new modules; user story implementation can begin.

---

## Phase 3: User Story 1 - Operational Dashboard (Priority: P1) 🎯 MVP

**Goal**: The app's landing page is a live operational dashboard with today's KPIs (US-060 / T135–T136).

**Independent Test**: Log in and land on `/reports/dashboard`; KPI cards (sessions, milk loaded/delivered, cash collected, deliveries by status, pending tokens, unclosed/unbalanced sessions) render and match today's session data.

### Implementation for User Story 1

- [x] T007 [US1] Create `frontend/src/pages/reports/DashboardPage.tsx` — `useDashboard()`; `PageHeader` "Operational Dashboard" with date; KPI card grid using `KpiCard`: `total_sessions`, `total_milk_loaded`, `total_milk_delivered`, `total_cash_collected` (`formatCurrency`), `pending_token_count`, `unclosed_sessions`, `unbalanced_sessions`, `completed_not_closed`; deliveries-by-status breakdown using `getStatusColor` badges (`STATUS_BADGE_MAP`/`DELIVERY_STATUS`); `LoadingSpinner` while loading, `EmptyState` on failure (FR-001/FR-002)
- [x] T008 [US1] Register `/reports/dashboard` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN","CHECKER","DELIVERY_PARTNER"]}>` (matches backend `require_role`), and change the index route from the placeholder `<DashboardPage />` to `<Navigate to="/reports/dashboard" replace />`; delete the now-unused `frontend/src/pages/DashboardPage.tsx` placeholder (T136; research R7)

**Checkpoint**: US1 independently testable — dashboard renders at `/` and `/reports/dashboard` (SC-001).

---

## Phase 4: User Story 2 - Route Delivery Report (Priority: P1)

**Goal**: Per-route delivery performance over a period with totals (US-061 / T137–T138).

**Independent Test**: Select This Week + a route; table shows session/delivery counts, loaded/delivered/token/cash/returned quantities, shortage/surplus, balanced indicator, and a totals summary row matching session data.

### Implementation for User Story 2

- [x] T009 [US2] Create `frontend/src/pages/reports/RouteDeliveryReportPage.tsx` — `useRoutes()` for the route `Select` (All routes); `PresetFilter`; `useRouteDelivery(params)`; `DataTable` columns route, session count, delivery count, loaded, delivered, token registered, cash collected, returned, shortage/surplus, balanced (`getStatusColor` badge for BALANCED/UNBALANCED); client-computed totals summary row from `data` (research R2, FR-003); CSV download button → `downloadReportCsv("/reports/route-delivery", params, "route-delivery-report")` (FR-009); `LoadingSpinner`/`EmptyState` (FR-010)
- [x] T010 [US2] Register `/reports/route-delivery` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN","CHECKER","DELIVERY_PARTNER"]}>` (backend `get_current_user`; DELIVERY_PARTNER restricted to own route server-side)

**Checkpoint**: US2 independently testable — route delivery report renders with totals (SC-002).

---

## Phase 5: User Story 3 - Revenue Report (Priority: P1)

**Goal**: Revenue with breakdowns by source/mode/route/milk type; OWNER only (US-062 / T139–T140).

**Independent Test**: Select This Month; total revenue and breakdowns render with percentages; route/milk-type filters narrow the numbers; a non-Owner is denied access.

### Implementation for User Story 3

- [x] T011 [US3] Create `frontend/src/pages/reports/RevenueReportPage.tsx` — `PresetFilter` + optional route `Select` (`useRoutes`) and milk-type `Select` (`useMilkTypes`); `useRevenue(params)`; summary cards for `total_revenue` (`formatCurrency`), `token_book_revenue`, `customer_bill_revenue`; four `DataTable`s for `by_source`, `by_payment_mode`, `by_route`, `by_milk_type` (source/mode/route/milk-type name, amount, percentage); optional CSV download; `LoadingSpinner`/`EmptyState` (FR-004/FR-009/FR-010)
- [x] T012 [US3] Register `/reports/revenue` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER"]}>` (FR-005/SC-006; backend `require_role(["OWNER"])`)

**Checkpoint**: US3 independently testable — revenue renders for Owner; access denied for others (SC-003, SC-006).

---

## Phase 6: User Story 4 - Customer Consumption (Priority: P1)

**Goal**: Per-customer consumption trend with a trend badge (US-063 / T141–T142).

**Independent Test**: Select a customer and date range; daily quantities, total/average, days with data, and an Increasing/Declining/Stable badge render and update on customer change.

### Implementation for User Story 4

- [x] T013 [US4] Create `frontend/src/pages/reports/ConsumptionReportPage.tsx` — customer `Select` (`useCustomers`) plus optional `:customerId` from the URL param as initial selection; `PresetFilter`; `useConsumption(customerId, params)`; summary cards (`total_consumption`, `average_daily`, `days_with_data`) + `TrendBadge` (`trend.change_percentage`); daily trend table (`formatDate`, `total_quantity`, per-milk-type breakdown); `LoadingSpinner`/`EmptyState`; 404 → "Customer not found" message (FR-006, FR-010)
- [x] T014 [US4] Register `/reports/consumption` (list with selector) and `/reports/consumption/:customerId` (pre-selected) in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN","CHECKER"]}>` (backend `require_role`)

**Checkpoint**: US4 independently testable — consumption trend renders for a selected customer (FR-006).

---

## Phase 7: User Story 5 - Token Utilization (Priority: P1)

**Goal**: Token book utilization with adjustable low threshold (US-064 / T143–T144).

**Independent Test**: Open the report; per-customer sheets used/remaining, utilization bars, and books-below-threshold render; changing the threshold updates the flagged count.

### Implementation for User Story 5

- [x] T015 [US5] Create `frontend/src/pages/reports/TokenUtilizationPage.tsx` — optional route `Select` (`useRoutes`), low-threshold `Input` (number 1–100, default 20); `useTokenUtilization(params)`; `DataTable` columns customer, route, token number, milk type, books issued, active/completed, sheets used, sheets remaining, utilization `UtilizationBar`, `books_below_20_percent` badge; client-computed overall utilization (research R2, FR-007); CSV download; `LoadingSpinner`/`EmptyState` (FR-009/FR-010)
- [x] T016 [US5] Register `/reports/token-utilization` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>` (backend `require_role`)

**Checkpoint**: US5 independently testable — token utilization renders with threshold flagging (SC-004).

---

## Phase 8: User Story 6 - Collection Efficiency (Priority: P2)

**Goal**: Collection efficiency with color-coded aging analysis (US-065 / T145–T146).

**Independent Test**: Open the report; per-customer billed/paid/balance, collection %, last bill/payment dates, and four aging buckets render; the buckets sum to balance; overall collection % is shown.

### Implementation for User Story 6

- [x] T017 [US6] Create `frontend/src/pages/reports/CollectionEfficiencyPage.tsx` — `PresetFilter` + optional route `Select` + min-outstanding `Input`; `useCollectionEfficiency(params)`; overall collection % card (client-computed `total_paid/total_billed`); `DataTable` columns customer (code + name), route, billed, paid, balance, collection %, last bill/payment date, and `AgingBuckets` (current/31–60/61–90/90+ color-coded, sums to balance per research R9); CSV download; `LoadingSpinner`/`EmptyState` (FR-008/FR-009/FR-010, SC-005)
- [x] T018 [US6] Register `/reports/collection-efficiency` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>` (backend `require_role`)

**Checkpoint**: US6 independently testable — collection efficiency renders with aging buckets (SC-005).

---

## Phase 9: Polish & Verification

**Purpose**: Navigation coverage, build/lint gates, and end-to-end manual validation across all six reports.

- [x] T019 Verify `frontend/src/config/permissions.ts` Reports menu covers the new routes (Dashboard `/reports/dashboard`, Route Delivery, Revenue, Consumption, Token Utilization, Collection Efficiency — already present); confirm the top-level "Dashboard" nav item (path `/`) still works for DELIVERY_PARTNER via the redirect, and adjust roles only if a navigation gap is found (do NOT add DELIVERY_PARTNER to the Revenue/Token/Collection items — backend denies them)
- [x] T020 Run `cd frontend && npm run build && npm run lint` — must pass clean (oxlint warning-free for new files)
- [x] T021 Validate quickstart.md scenarios V11–V18 with seeded delivery data (dashboard landing, route delivery totals, revenue OWNER-only + non-owner denial, consumption trend, token threshold, aging buckets, CSV download, DELIVERY_PARTNER route scope). Manual checks were recorded in quickstart.md; scenarios are now also automated by `frontend/e2e/reports.spec.ts` (7 tests: dashboard today-session KPIs, route-delivery aggregation + CSV export, consumption breakdown, revenue + collection aging invariant, token threshold flagging, role restrictions for CHECKER/EMPLOYEE, DELIVERY_PARTNER route scope). Full Playwright suite: `cd frontend && npm run test:e2e` — 45 tests green.

**Checkpoint**: All six report pages render with real data; build and lint green; quickstart validated.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–8)**: All depend on Foundational completion; each is independently testable
- **Polish (Phase 9)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Foundational T004/T005/T006 — no other story dependency (MVP)
- **User Story 2 (P1)**: Foundational — no other story dependency
- **User Story 3 (P1)**: Foundational — no other story dependency
- **User Story 4 (P1)**: Foundational — no other story dependency
- **User Story 5 (P1)**: Foundational — no other story dependency
- **User Story 6 (P2)**: Foundational — no other story dependency

### Within Each User Story

- Types before API before hooks before pages (Phases 1–2)
- Page scaffold before its filters/actions
- Route registration in `App.tsx` after its page is created

### Parallel Opportunities

- T002/T003 (constants + types) run in parallel
- T004/T005/T006 (API + hooks + shared components) are different files — can run in parallel after T002/T003
- After Foundational, page scaffolds T007/T009/T011/T013/T015/T017 are different files and can run in parallel
- Route registrations T008/T010/T012/T014/T016/T018 all edit `frontend/src/App.tsx` — sequential, no [P]
- T019 and T020 can run in parallel; T021 last

---

## Parallel Example: Report Pages After Foundational

```bash
Task: "Create DashboardPage in frontend/src/pages/reports/DashboardPage.tsx"
Task: "Create RouteDeliveryReportPage in frontend/src/pages/reports/RouteDeliveryReportPage.tsx"
Task: "Create RevenueReportPage in frontend/src/pages/reports/RevenueReportPage.tsx"
Task: "Create ConsumptionReportPage in frontend/src/pages/reports/ConsumptionReportPage.tsx"
Task: "Create TokenUtilizationPage in frontend/src/pages/reports/TokenUtilizationPage.tsx"
Task: "Create CollectionEfficiencyPage in frontend/src/pages/reports/CollectionEfficiencyPage.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (types + constants)
2. Complete Phase 2: Foundational (API + hooks + shared components) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (dashboard landing page)
4. **STOP and VALIDATE**: `npm run build` + `npm run lint` + V11 dashboard check
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → report pages can call the backend
2. Add US1 → test independently (dashboard at `/`) → demo (MVP!)
3. Add US2 → test independently (route delivery + totals) → demo
4. Add US3 → test independently (revenue + OWNER guard) → demo
5. Add US4 → test independently (consumption trend) → demo
6. Add US5 → test independently (token utilization) → demo
7. Add US6 → test independently (aging buckets) → demo
8. Final: nav verification + build/lint + quickstart V11–V18

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (types, constants, API, hooks, shared components are the critical path)
2. Developer A: US1 (Dashboard) then US2 (Route Delivery)
3. Developer B: US3 (Revenue) then US6 (Collection Efficiency)
4. Developer C: US4 (Consumption) then US5 (Token Utilization)
5. Developer D: App.tsx route registration (sequential) + Phase 9 polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All `App.tsx` route tasks MUST be sequential (same file)
- Backend is NOT modified in this phase — `app/routers/reports.py` and `app/services/reports/*` are consumed as-is
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
