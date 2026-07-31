# TODO.md - Development Roadmap

> Sprint-based development plan with dependencies and status.

---

## Current State (Actual — July 31, 2026)

**Completed Code**: Sprints 1, 2, 3 (delivery), 4-core (token books), 5 (reconciliation), 6 (payments), 7 (reports)
**Tested Code**: All Sprints 1–7 ✅
**Frontend**: Sprint 9 in progress — Phase 1 (Setup/Auth/Layout) + Phase 2 (Master Data CRUD) complete; Phases 3–8 pending
**Untested Code**: None
**Total Tables**: 17
**Total API Endpoints**: ~84
**Known Bugs**: 0

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

### Sprint 8: AI Business Intelligence (NOT STARTED)
- [ ] Demand forecasting
- [ ] Customer churn prediction
- [ ] Route optimization suggestions
- [ ] Anomaly detection (unusual orders, payments)

### Sprint 9: Frontend - React (IN PROGRESS — Phase 1 & 2 COMPLETE ✅)
- [x] Phase 1: Backend prep (CORS, /api/v1 prefix, health) + frontend scaffold + auth + layout
- [x] Phase 2: Master Data CRUD (routes, customers, milk types, employees, users)
- [ ] Phase 3: Subscriptions & Exceptions pages
- [ ] Phase 4: Token book pages
- [ ] Phase 5: Delivery management pages (session lifecycle, registration, reconciliation)
- [ ] Phase 6: Payment pages
- [ ] Phase 7: Report pages
- [ ] Phase 8: Polish & testing

### Sprint 10: Testing and Deployment (NOT STARTED)
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

---

## Immediate Next Steps (Priority Order)

1. **🔴 HIGH**: Frontend Phase 3 — Subscriptions & Exceptions pages (T070-T083 in `specs/004-react-frontend/tasks.md`)
2. **🔴 HIGH**: Frontend Phase 4 — Token Books pages (T084-T099)
3. **🔴 HIGH**: Frontend Phase 5 — Delivery Management pages (T100-T122) — highest operational value
4. **🟡 MEDIUM**: Frontend Phase 6 — Payments pages (T123-T131)
5. **🟡 MEDIUM**: Frontend Phase 7 — Reports pages (T132-T146)
6. **🟡 MEDIUM**: Address SECRET_KEY hardening (move to env variable)
7. **🟢 LOW**: Remove empty migration `1154a3a25414` or implement intended logic
8. **🟢 LOW**: Add pagination/filtering to original CRUD endpoints
9. **🟢 LOW**: Standardize HTTP status codes (201 vs 200 on create)
