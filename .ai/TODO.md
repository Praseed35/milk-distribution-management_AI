# TODO.md - Development Roadmap

> Sprint-based development plan with dependencies and status.

---

## Current State (Actual — August 5, 2026)

**Completed Code**: Sprints 1, 2, 3 (delivery), 4-core (token books), 5 (reconciliation), 6 (payments), 7 (reports), 8-core (AI BI); Frontend Phases 1–7
**Tested Code**: All Sprints 1–7 ✅ (379 tests across 13 files) + AI module (87 tests in `tests/test_ai.py`) + Frontend E2E (52 Playwright specs across 9 files)
**Frontend**: Phase 1–2 (Sprint 9, commit d14589b4) + Phase 3–4 (Sprint 10, commit f536667f) + Phase 5 Delivery Management (specs/007, all tasks [X]) + Phase 6 Payment Management (specs/008, all tasks [X]) + Phase 7 Reports Pages (specs/009, all T001–T021 [X], commit 4489d6a) + AI Insights page (`/reports/ai`, OWNER/ADMIN) complete; Phase 8 pending
**Untested Code**: None
**Total Tables**: 17
**Total API Endpoints**: ~90
**Known Bugs**: 1 — revenue report returns empty JSON envelope on cache hit (`app/routers/reports.py`; TECH_DEBT B3)

---

## Sprint Plan (Actual Status)

### Sprint 1: Master Data (COMPLETED ✅, TESTED ✅)
- [x] User management (basic create)
- [x] JWT Authentication (login, me, change-password)
- [x] Route CRUD
- [x] Customer CRUD with auto-generated codes
- [x] Milk Type CRUD
- [x] Employee CRUD with optional user linking
- [x] Role-based access control
- [x] Seed data script

### Sprint 2: Subscriptions + Delivery Exceptions (COMPLETED ✅, TESTED ✅)
- [x] Subscription CRUD with joined queries
- [x] Subscription deactivation
- [x] Delivery Exception CRUD
- [x] Date overlap detection
- [x] Active subscription/milk type validation
- [x] Subscription by customer endpoint

### Sprint 3: Daily Delivery Management (COMPLETED ✅, TESTED ✅)
**Depends on**: Sprint 1, 2
**Status**: All code written + tested, 68 tests. Bugs fixed.

**What exists**:
- [x] Daily delivery session (morning/evening shift) — `delivery_sessions` table + service
- [x] Route-day assignment with unique constraint (route_id, delivery_date, shift)
- [x] Delivery checklist generation from active subscriptions
- [x] Delivery status tracking (DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED)
- [x] Delivery partner assignment per route per shift
- [x] Token sheet validation (sequential check, gap detection, out-of-order, old-book detection)
- [x] Token registration workflow
- [x] Unplanned delivery registration
- [x] Session state machine: PLANNED -> STARTED -> COMPLETED -> CLOSED
- [x] Session reopen (owner only) with audit trail
- [x] Optimistic locking (version column) on deliveries
- [x] Pagination + filtering on session list

**New Tables** (created in migration `5a6b7c8d9e0f`):
- `delivery_sessions` — Daily session per route per shift
- `daily_deliveries` — Per-customer delivery record in a session
- `session_edits` — Immutable audit log for session edits
- `token_sheet_warnings` — Warning records for non-sequential token sheets

### Sprint 4: Token Book Core (COMPLETED ✅, TESTED ✅)
- [x] Token Identities CRUD
- [x] Token Book Issues CRUD with active book enforcement
- [x] Token Book Payments CRUD with auto-status calculation

### Sprint 5: Reconciliation (COMPLETED ✅, TESTED ✅)
**Depends on**: Sprint 3
**Status**: Tested via delivery test suite.

**What exists**:
- [x] Daily reconciliation calculation (loaded vs token vs cash vs returned)
- [x] Expected vs delivered comparison
- [x] Cash collection tracking
- [x] Shortage/surplus detection
- [x] Reconciliation validation (can_close check)
- [x] Cash sale add/remove during reconciliation
- [x] Session summary report
- [x] Customer delivery status view

### Sprint 6: Payment Management (COMPLETED ✅, TESTED ✅)
**Depends on**: Sprints 1, 3
**Status**: 33 tests, 3 new tables, 14 endpoints.

- [x] Customer payment ledger (CASH, UPI, CARD, CHEQUE, BANK_TRANSFER)
- [x] Advance payment tracking
- [x] Monthly bill generation (from delivered qty × unit_price)
- [x] Bill line items per milk type
- [x] Outstanding balance tracking (billed vs paid vs balance)
- [x] Payment collection by delivery partner (collected_by field)

### Sprint 7: Reports and Analytics (COMPLETED ✅, TESTED ✅)
- [x] Route-wise daily/weekly/monthly reports
- [x] Customer-wise consumption reports
- [x] Revenue reports
- [x] Collection efficiency reports
- [x] Token book utilization reports
- [x] Operational dashboard
- [x] CSV export + in-memory caching + RBAC

### Sprint 8: AI Business Intelligence (IN PROGRESS ✅ backend + frontend core — specs/010, T001–T034 [X])
- [x] Demand forecasting (weekday-seasonal moving average, per route/milk type, horizons 1-30)
- [x] Customer churn prediction (score 0-100, LOW/MEDIUM/HIGH)
- [x] Anomaly detection (deterministic z-score: high returns, cash shortfall, mismatch, low sales, consumption drop)
- [x] AI narrative (`/ai/insights`, OWNER-only, LLM + stats-only degradation)
- [x] Conversational Q&A (`/ai/chat`, OWNER-only, per-user rate limit)
- [ ] Route optimization suggestions (deferred — not part of specs/010 scope)

### Sprint 9: Frontend - React Phases 1–2 (COMPLETED ✅, commit d14589b4)
- [x] Phase 1: Backend prep (CORS, /api/v1 prefix, health) + frontend scaffold + auth + layout
- [x] Phase 2: Master Data CRUD (routes, customers, milk types, employees, users)

### Sprint 10: Frontend - React Phases 3–4 (COMPLETED ✅, commit f536667f)
- [x] Phase 3: Subscriptions & Exceptions pages (T070-T083)
- [x] Phase 4: Token book pages (T084-T099)

### Phase 5: Delivery Management Pages (COMPLETED ✅ — specs/007, T001-T037)
- [x] Backend fixes: `generate_delivery_list` rewrite (join via Customer, shift quantities, exception exclusion), `POST /deliveries/sessions/{id}/complete`, server-side OWNER RBAC on edit/reopen
- [x] `frontend/src/pages/delivery/`: SessionListPage, SessionCreatePage, SessionDetailPage, DeliveryEditPage
- [x] api + hooks + types for delivery-sessions and deliveries
- [x] tests: `tests/test_delivery_edit.py` (8 OWNER-RBAC tests) + delivery-suite additions

### Phase 6: Payment Management Pages (COMPLETED ✅ — specs/008, T001-T020)
- [x] `frontend/src/pages/payments/`: PaymentListPage (filters), PaymentFormPage, BillListPage, BillGeneratePage, OutstandingPage, BillDetailPage
- [x] `api/payments.ts` + `hooks/usePayments.ts` + `types/payment.ts` + `PAYMENT_TYPES`/`BILL_STATUS` constants
- [x] Six routes registered in `App.tsx`, all `<RoleGuard roles={["OWNER","ADMIN"]}>`
- [x] tests: 7 E2E specs in `frontend/e2e/payments.spec.ts` (advance/bill payment, bill generate, outstanding, status update, RBAC)

### Phase 7: Reports Pages (COMPLETED ✅ — specs/009, T001-T021, commit 4489d6a)
- [x] `frontend/src/types/reports.ts` (all report interfaces + param interfaces) + `REPORT_PRESETS` in `lib/constants.ts` + `formatQuantity`/`formatPercent` in `lib/utils.ts`
- [x] `frontend/src/api/reports.ts` (6 fetchers + `downloadReportCsv` via `format=csv` blob download) + `hooks/useReports.ts` (`refresh` in query keys)
- [x] `frontend/src/components/reports/`: KpiCard, PresetFilter, TrendBadge, UtilizationBar, AgingBuckets
- [x] `frontend/src/pages/reports/`: DashboardPage, RouteDeliveryReportPage, RevenueReportPage, ConsumptionReportPage, TokenUtilizationPage, CollectionEfficiencyPage
- [x] Routes in `App.tsx` with RoleGuards matching backend RBAC; `/` → `/reports/dashboard` redirect; placeholder DashboardPage deleted
- [x] tests: 7 E2E specs in `frontend/e2e/reports.spec.ts`; backend `REPORT_CACHE_DISABLED=1` env var disables the in-memory report cache for E2E (isolated `milk_management_e2e` DB, reset each run)

### Sprint 13: Frontend - Phase 8 Polish & Testing (NEXT — NOT STARTED)
- [ ] Phase 8: Polish & testing (T147-T158)

### Sprint 11: Testing and Deployment (NOT STARTED)
- [ ] Comprehensive test coverage (target: 95%+)
- [ ] API documentation finalization
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Performance testing
- [ ] Security audit

---

## 🐛 Known Bugs ✅ Fixed (July 29, 2026)

### Bug 1: `Subscription.route_id` doesn't exist ✅ FIXED
**File**: `app/services/delivery_service.py`
**Fix**: Query now joins through Customer table (`Subscription → Customer`) and filters by `Customer.route_id`.

### Bug 2: Hardcoded `user_id=1` in delivery routers ✅ FIXED
**File**: `app/routers/delivery_edit.py`
**Fix**: Both `edit_delivery()` and `reopen_session()` now inject `current_user: User = Depends(get_current_user)`.

## 🐛 Known Bugs Open (found Aug 4, 2026)

### Bug 3: Revenue report empty envelope on JSON cache hit
**File**: `app/routers/reports.py` (`get_revenue`)
On cache hit with `format=json`, returns `_envelope([], ...)` (empty) instead of cached data. CSV path OK. See TECH_DEBT B3.

### Bug 4: `UserRole` enum missing ADMIN + EMPLOYEE
**File**: `app/constants/roles.py`
`ADMIN` used by reports RBAC, `EMPLOYEE` created by seed; neither is in the enum. See TECH_DEBT B4.

---

## Immediate Next Steps (Priority Order)

1. **🔴 HIGH**: Frontend Phase 8 — Polish & testing (T147-T158 in `specs/004-react-frontend/tasks.md`)
2. **🔴 HIGH**: Fix revenue report cache-hit bug (TECH_DEBT B3)
3. **🟡 MEDIUM**: Address SECRET_KEY hardening (move to env variable)
4. **🟡 MEDIUM**: Backend-wide RBAC on `/payments/*` (and other) routers — only `reports`/`auth` use `get_current_user` (see specs/008 spec.md)
5. **🟡 MEDIUM**: Complete `UserRole` enum (ADMIN, EMPLOYEE) or document role strings (TECH_DEBT B4)
6. **🟢 LOW**: Remove empty migration `1154a3a25414` or implement intended logic
7. **🟢 LOW**: Add pagination/filtering to original CRUD endpoints
8. **🟢 LOW**: Standardize HTTP status codes (201 vs 200 on create)
