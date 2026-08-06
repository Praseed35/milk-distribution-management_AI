# Feature Status (As of August 4, 2026 — Updated)

## Backend

### Master Data (Sprint 1) — COMPLETED ✅ TESTED ✅
- Authentication (JWT login, me, change-password) ✅
- Users (create, list) ✅
- Routes (full CRUD) ✅
- Customers (full CRUD + auto codes) ✅
- Milk Types (full CRUD) ✅
- Employees (full CRUD + optional user linking) ✅

### Subscriptions + Delivery Exceptions (Sprint 2) — COMPLETED ✅ TESTED ✅
- Subscriptions (full CRUD + by customer + deactivation) ✅
- Delivery Exceptions (full CRUD + by subscription + overlap detection) ✅

### Token Book Management — Core (Sprint 4) — COMPLETED ✅ TESTED ✅
- Token Identities (full CRUD + by customer) ✅
- Token Book Issues (full CRUD + by identity + active book enforcement) ✅
- Token Book Payments (full CRUD + by issue + auto status calc) ✅
- Note: TokenBookIssue model has additional fields (customer_id, milk_type_id, book_number, total_sheets)

### Daily Delivery Management (Sprint 3) — COMPLETED ✅ TESTED ✅
- Delivery Sessions ✅ (create, start, dispatch, close, list, get)
- Delivery Items / DailyDeliveries ✅ (planned list generation, status tracking)
- Shift-based tracking ✅ (MORNING/EVENING on sessions + deliveries)
- Delivery partner assignment ✅
- Delivery status: DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED ✅
- Token sheet validation (sequential, gap, out-of-order, old-book) ✅
- Unplanned delivery registration ✅
- Delivery checklist generation ✅
- Session reopen with audit trail ✅
- Optimistic locking (version column) ✅
- All bugs fixed ✅

### Reconciliation (Sprint 5) — COMPLETED ✅ TESTED ✅
- Daily reconciliation (loaded vs token vs cash vs returned) ✅
- Cash collection tracking ✅
- Shortage/surplus detection ✅
- Reconciliation validation ✅
- Cash sale add/remove during reconciliation ✅
- Session summary report ✅
- Customer delivery status view ✅

### Payment Management (Sprint 6) — COMPLETED ✅ TESTED ✅
- Customer payment ledger (CASH, UPI, CARD, CHEQUE, BANK_TRANSFER) ✅
- Advance payment tracking ✅
- Monthly bill generation (from delivered qty × unit_price) ✅
- Bill line items per milk type ✅
- Outstanding balance tracking (billed vs paid) ✅
- Payment collection modes: ADVANCE, BILL_PAYMENT ✅

### Extended Token Features — NOT IMPLEMENTED
- Token Register (sheet-level ledger) ❌
- Warning Log dashboard ❌

### Reports and Analytics (Sprint 7) — COMPLETED ✅ TESTED ✅
- Route delivery reports (loaded vs delivered vs cash vs shortage) ✅
- Revenue reports (by source, payment mode, route, milk type) ✅
- Collection efficiency (billed vs paid vs outstanding, aging buckets) ✅
- Customer consumption (daily trend with detection: increasing/declining/stable) ✅
- Token book utilization (sheets used/remaining, low threshold flags) ✅
- Operational dashboard (session counts, deliveries, flagged issues) ✅
- CSV export (all list endpoints via ?format=csv) ✅
- In-memory cache (configurable TTL, bypass with ?refresh=true; module-level `REPORT_CACHE_DISABLED=1` env var disables `get()`/`set()` entirely — used by E2E to avoid stale zero-session data) ✅
- RBAC enforcement (OWNER=all, ADMIN/CHECKER=operational, DELIVERY_PARTNER=own route) ✅
- Alembic migration (indexes on delivery_status, payment_date, bill_period_start) ✅
- 24 tests across 6 story areas + RBAC + CSV + auth ✅

### AI Business Intelligence (Sprint 8 / specs/010) — COMPLETED ✅ (all tasks T001–T037, incl. E2E T035 + quickstart T036)
- Statistical demand forecast (weekday-seasonal moving average, per route/milk type, horizon 1-30) ✅
- Anomaly detection (deterministic z-score: high returns, cash shortfall, delivery-milk mismatch, low sales day, consumption drop) ✅
- Churn-risk scoring (0-100, LOW/MEDIUM/HIGH, factor breakdown) ✅
- AI narrative `/ai/insights` (OWNER-only; LLM + stats-only degradation on `AI_LLM_DISABLED`/failure) ✅
- Conversational Q&A `/ai/chat` (OWNER-only; per-user sliding-window rate limit → 429; LLM down → 503) ✅
- In-memory 300s per-user cache on all AI GETs (`?refresh=true` bypasses); chat never cached ✅
- RBAC: forecast/anomalies/churn OWNER/ADMIN; insights/chat OWNER only ✅
- 87 tests in `tests/test_ai.py` (incl. edge cases: horizon/limit/days_back bounds, status+inactive filters, cache TTL & `?refresh`, balanced/today-unclosed exclusions, severity ordering, churn factor sum/cap, insights presets & reversed ranges, chat max/whitespace boundaries, sliding-window rate-limit reset, PII stripping) ✅
- Frontend: `AIInsightsPage` with ForecastSection, AnomalyList, ChurnRiskTable, InsightNarrative, ChatPanel; `types/ai.ts`/`api/ai.ts`/`hooks/useAI.ts`; nav + RoleGuard OWNER/ADMIN ✅
- E2E: `frontend/e2e/ai.spec.ts` (7 tests — forecast bars, anomalies/churn render, stats-only notice, chat 503, CHECKER nav/denial, horizon clamp 1–30, forecast Refresh, chat Send disabled for empty/whitespace) green; `scripts/e2e_backend.py` sets `AI_LLM_DISABLED=1` alongside `REPORT_CACHE_DISABLED=1` ✅
- Quickstart `quickstart.md` scenarios 1–3, 5, 6 validated (live-LLM Scenario 4 is a manual smoke test, never run in CI) ✅
- Route optimization suggestions ❌ (deferred — not in specs/010 scope)

## Frontend (Sprint 9 — COMPLETED; Sprint 10 — COMPLETED; Phase 5 — COMPLETED; Phase 6 — COMPLETED; Phase 7 — COMPLETED)
- **Phase 1: Setup, Auth, Layout — COMPLETED ✅** (backend CORS + /api/v1 prefix + health endpoint; Vite scaffold; auth flow; layout; UI primitives) [Sprint 9, commit d14589b4]
- **Phase 2: Master Data CRUD — COMPLETED ✅** (Routes, Customers, Milk Types, Employees, Users) [Sprint 9]
- **Phase 3: Subscriptions & Exceptions — COMPLETED ✅** (T070-T083: SubscriptionListPage/FormPage, ExceptionListPage/FormPage, CHECKER read-only) [Sprint 10, commit f536667f]
- **Phase 4: Token Books — COMPLETED ✅** (T084-T099: TokenIdentityList/Form, TokenBookIssueList/Form, TokenBookPaymentList/Form, CHECKER read-only) [Sprint 10]
- **Phase 5: Delivery Management — COMPLETED ✅** (specs/007 T001-T037: SessionListPage, SessionCreatePage, SessionDetailPage [dispatch/checklist/registration/reconciliation/close/reopen], DeliveryEditPage; backend fixes: `generate_delivery_list` rewrite, `POST /deliveries/sessions/{id}/complete`, server-side OWNER RBAC on edit/reopen; 8 new tests in `tests/test_delivery_edit.py`)
- **Phase 6: Payment Management — COMPLETED ✅** (specs/008 T001-T020: PaymentListPage [US1+US4 filters], PaymentFormPage [ADVANCE/BILL_PAYMENT + unpaid-bill picker], BillListPage, BillGeneratePage [multi-select + duplicate-period warning], OutstandingPage [per-customer `useQueries`], BillDetailPage [line items + applied payments + status update with ConfirmDialog]; all six routes RoleGuard OWNER/ADMIN; 7 E2E tests in `frontend/e2e/payments.spec.ts`)
- **Phase 7: Reports — COMPLETED ✅** (specs/009 T001-T021, commit 4489d6a: `frontend/src/types/reports.ts` [all report interfaces + params]; `api/reports.ts` [getDashboard, getRouteDelivery, getRevenue, getConsumption, getTokenUtilization, getCollectionEfficiency + `downloadReportCsv` using `format=csv` + blob download]; `hooks/useReports.ts` [TanStack Query, `refresh` in query keys]; `components/reports/` [KpiCard, PresetFilter, TrendBadge, UtilizationBar, AgingBuckets]; `pages/reports/` [DashboardPage, RouteDeliveryReportPage, RevenueReportPage, ConsumptionReportPage, TokenUtilizationPage, CollectionEfficiencyPage]; index `/` → `<Navigate to="/reports/dashboard" replace />`; RoleGuards match backend RBAC — dashboard+route-delivery OWNER/ADMIN/CHECKER/DELIVERY_PARTNER, revenue OWNER only, consumption OWNER/ADMIN/CHECKER, token-utilization+collection-efficiency OWNER/ADMIN; old `pages/DashboardPage.tsx` placeholder deleted; 7 E2E tests in `frontend/e2e/reports.spec.ts`)
- Phase 8: Polish & Testing — NOT STARTED ❌ (T147-T158)

## Testing and Deployment
- Docker, CI/CD — NOT STARTED (Sprint 10)

---

## Summary

> Verified against source Aug 5, 2026.

| Status | Count |
|--------|-------|
| Tested Modules | 15 (master data + subscriptions + exceptions + tokens + delivery + payments + reports + AI) |
| Untested Modules | 0 |
| Known Bugs | 1 (revenue report empty envelope on JSON cache hit — `app/routers/reports.py`; see TECH_DEBT B3) |
| Backend Test Files | 14 (delivery + delivery_edit + payments + reports + ai) |
| Backend Tests | 466 |
| Frontend E2E (Playwright) | 52 specs across 9 spec files (`frontend/e2e/`), incl. 7 for payments + 7 for reports + 7 for AI (`ai.spec.ts`) |
| Tables | 17 (no new tables — AI + reports use aggregation queries) |
| API Endpoints | ~90 (6 report + 5 AI endpoints added) |
| Version | 1.0 Development |

**Note**: "Extended Token Features" (Token Register sheet-level ledger, Warning Log dashboard) are **NOT implemented** — no service or router exists for either. The `token_sheet_warnings` TABLE exists (populated during delivery registration) but has no management UI/API. See `module_map.md`.
