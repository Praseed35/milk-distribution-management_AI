# TECH_DEBT.md - Technical Debt and Known Issues

> Issues that should be addressed but haven't been yet.
> Verified against source: Aug 4, 2026.

---

## 🐛 Known Bugs

### B3. Revenue Report Returns Empty Data on JSON Cache Hit ✅ (found Aug 4, 2026)
**File**: `app/routers/reports.py` (`get_revenue`, lines ~139–147)
On a cache hit with `format=json`, the endpoint returns `_envelope([], page, page_size)` — an **empty** envelope — instead of the cached report data. CSV cache hits work correctly. Impact is masked in E2E because `scripts/e2e_backend.py` sets `REPORT_CACHE_DISABLED=1`, and in dev by `?refresh=true`. Fix: return the cached payload wrapped in the envelope (mirror `collection-efficiency`/`route-delivery` handlers).

### B4. `UserRole` Enum Is Incomplete
**File**: `app/constants/roles.py`
`UserRole` defines only `OWNER`, `CHECKER`, `DELIVERY_PARTNER` — but `ADMIN` is required by the reports RBAC (`app/routers/reports.py` uses `["OWNER","ADMIN",...]`) and `EMPLOYEE` is created by `scripts/seed.py`. `User.role` is a plain `String(50)` so nothing crashes, but the enum is not the source of truth for roles.

### B5. AI LLM Disabled-Mode Caveat (found Aug 5, 2026)
**File**: `app/services/ai/client.py` + `app/core/config.py`
`AI_LLM_DISABLED=1` disables LLM calls so the insights endpoint degrades to `stats_only: true` and chat returns 503. Caveats:
- The mock client (`AI_LLM_PROVIDER=mock`, default) returns canned replies and is indistinguishable from a live LLM in stats-only/503 logic — fine for dev, but the mock never exercises the NVIDIA API payload path.
- Chat's 503-on-disabled is correct per spec (R8), but a frontend relying on chat as a hard feature will see 503 in any environment where the LLM is off.
- LLM is called via `client.chat_completion`; timeouts/errors are surfaced as `AIUnavailableError` → 503 (no retry/backoff yet).

### B6. AI Endpoint Cache Has No Invalidation (found Aug 5, 2026)
**File**: `app/services/ai/cache.py`
Forecast/anomalies/churn-risk/insights share the same 300s TTL pattern as reports (`app/services/reports/cache.py`): results are cached per user and only bypassed by `?refresh=true`. There is no cache invalidation when deliveries/payments/bills are mutated. Same caveat as the reports cache — acceptable for MVP, revisit with write-side invalidation later.

---

## 🔴 Critical Bugs ✅ Fixed

### B1. `Subscription.route_id` doesn't exist (will crash) ✅ FIXED
**File**: `app/services/delivery_service.py`
**Fix**: Now joins through `Customer` table (`Subscription.customer_id → Customer.id`) and filters by `Customer.route_id`.
**Date**: July 29, 2026

### B2. Hardcoded `user_id=1` in delivery routers ✅ FIXED
**File**: `app/routers/delivery_edit.py`
**Fix**: Both `edit_delivery()` and `reopen_session()` now inject `current_user: User = Depends(get_current_user)` and use `current_user.id`.
**Date**: July 29, 2026

---

## High Priority

### 1. Hardcoded Secret Key
**File**: `app/core/config.py`
```python
SECRET_KEY = "milk_management_secret_key_2026"
```
Should use environment variable. Security risk in production.

### 2. No Delivery Session Tests ✅ RESOLVED
Session lifecycle/registration/reconciliation/edit are covered. Phase 5 added `tests/test_delivery_edit.py` (8 OWNER-RBAC tests) and expanded `test_daily_delivery.py` (81 tests). **379 tests total across 13 test files.**

### 3. Database Name Typo
Database is `milk_managemen_ai` (missing 't' in management). Consistent everywhere but confusing.

### 4. No CORS Configuration ✅ RESOLVED
CORS middleware added in `app/main.py` allowing `http://localhost:5173` (Vite dev server). Required for frontend integration — now done.

### 5. Inconsistent Exception Hierarchy
`BusinessException` base class exists in `exceptions/base.py` but many exceptions extend `Exception` directly:
- Extend `BusinessException` ✓: `route.py`, `milk_type.py`, **`delivery.py`**, **`delivery_edit.py`** (newer code is correct)
- Extend `Exception` directly ❌: `user.py`, `customer.py`, `employee.py`, `subscription.py`, `delivery_exception.py`, `token_book.py`

---

## Medium Priority

### 6. Constants Not Enforced
Status/role enums defined in `constants/` are not used in models or schemas:
- `UserRole` enum not used - roles stored as plain strings
- `Shift` enum imported in subscription schema but not used as constraint
- `SessionStatus`, `TokenStatus`, `DeliveryStatus`, `DeliverySource`, `WarningCode`, `ReconciliationStatus` defined but not enforced at model/schema level

### 7. Users Router Missing CRUD
`/users` only has GET (list) and POST (create). No update or delete endpoints. `users` table also lacks `created_at`/`updated_at` timestamps.

### 8. No Pagination on Original Endpoints
Only `delivery_service.list_sessions()` has pagination (skip/limit). All other list endpoints return every active record.

### 9. No Filtering/Search on Original Endpoints
Only delivery session list has query parameter filters (route_id, delivery_date, shift, status). Original endpoints have no filtering.

### 10. Hardcoded Values in Services
- Customer code generation: `f"C{next_number:05d}"` - hardcoded format
- Employee code generation: `f"E{next_number:05d}"` - hardcoded format
- Default statuses: "ACTIVE", "WAITING", "PENDING" hardcoded in service code

### 11. Empty Directories
`app/common/` and `app/utils/` exist but contain no code. Should be removed or utilized.

---

## Low Priority

### 12. Service Return Type Inconsistency
Some services return SQLAlchemy model objects, others return dicts. Mixed patterns:
- Routes, MilkTypes, Customers: Return model objects
- Subscriptions, DeliveryExceptions, TokenBooks: Return manually constructed dicts
- Delivery services: Mix of model objects (create_session returns DeliverySession) and dicts (register_token returns dict)

### 13. No Request ID / Logging
No structured logging or request ID tracking for debugging.

### 14. No Rate Limiting (partially addressed)
No rate limiting on general endpoints. Exception: `/ai/chat` has a per-user sliding-window `RateLimiter` (`app/services/ai/chat.py`, `AI_CHAT_MAX_REQUESTS_PER_MINUTE` default 20 → 429). No rate limiting elsewhere.

### 15. Backend Test DB Uses Production Database
Backend test DB URL defaults to same production PostgreSQL (`milk_managemen_ai`). No separate test database. While transaction rollback provides isolation, schema changes during test runs may affect production data.
**Note**: Playwright E2E does NOT have this problem — `scripts/e2e_backend.py` (new in Phase 5+) resets and seeds an isolated `milk_management_e2e` database and serves the API on port 8001.

### 16. User Service Uses Different Pattern
`user_service.create()` returns `None` on duplicate instead of raising exception (inconsistent with all other services).

### 17. User Model Missing Timestamps
The `users` table doesn't have `created_at`/`updated_at` columns unlike all other tables.

### 18. Empty Migration
**File**: `alembic/versions/1154a3a25414_remove_is_active_in_update_customer_.py`
Empty migration — `upgrade()` and `downgrade()` do nothing. Either implement the intended logic or remove/replace.

---

## Architecture Improvements Needed

### Completed (Already Implemented)
- ✅ Delivery session/daily log table (`delivery_sessions`, `daily_deliveries`)
- ✅ Shift-based delivery tracking (`shift` column on session + delivery)
- ✅ Route-day assignment capability (unique constraint on route_id+date+shift)
- ✅ Daily totals aggregation (`total_milk_loaded`, `total_token_registered`, etc. on session)
- ✅ Cash collection tracking (`total_cash_sales` on session, `cash_amount` on delivery)
- ✅ Discrepancy detection (reconciliation difference calculation)
- ✅ Immutable audit trail (`session_edits` table with JSONB snapshots)
- ✅ Optimistic locking (version column on session + delivery)
- ✅ Pagination + filtering on delivery session list

### Still Needed
- OpenAPI customization (title, description, version)
- Request/response logging middleware
- SECRET_KEY hardening — now reads from `SECRET_KEY` env var via `dotenv` (`app/core/config.py`), but still falls back to the default dev key when unset; require a strong key in production
- Comprehensive payment ledger / sheet-level token register
- Rate limiting beyond `/ai/chat`

### Frontend-Specific
- Frontend Phase 7 (reports pages) is complete; the 300s in-memory report cache (`app/services/reports/cache.py`) has no invalidation on delivery/payment mutation — `REPORT_CACHE_DISABLED=1` exists for E2E; production may need cache invalidation on writes (payments pages are complete, Phase 6 specs/008). AI endpoints reuse the same pattern via `app/services/ai/cache.py` (see B6).
- The AI Insights page (`/reports/ai`, specs/010) renders forecast/anomalies/churn (OWNER/ADMIN) and insights narrative + chat (OWNER only). `scripts/e2e_backend.py` sets both `AI_LLM_DISABLED=1` and `REPORT_CACHE_DISABLED=1`; `frontend/e2e/ai.spec.ts` (7 specs, T035) is green.
- Root `README.md` and `frontend/README.md` historically stale — README frontend status now reflects Phases 1–6 (still says React 19/Vite 8, which matches actual React 19.2.8/Vite 8.2.0)
- `.ai/` docs previously reported 12 migrations / 343 tests — now 13 migrations / 379 tests (verified Aug 1, 2026); current: 466 tests across 14 files (Aug 6, 2026)
- `scripts/` now contains 4 files: `seed.py`, `seed_history.py` (30 days of sessions/deliveries/bills/payments for the AI pages + reports), `test_subscriptions.py`, and `e2e_backend.py` (E2E DB reset + API on :8001; honors `E2E_DB_NAME`, `E2E_PORT`, `DATABASE_URL` overrides; sets `REPORT_CACHE_DISABLED=1`)
- Backend `/payments/*` router (like most routers) has **no** `get_current_user` dependency — only `reports` and `auth` attach it. Client-side RoleGuards are the only enforcement on payment pages (noted in specs/008 spec.md). Fix backend-wide RBAC in a later sprint.
- **CORS mismatch**: `app/main.py` allows only `http://localhost:5173`, but Playwright runs the frontend on `:5174` (via `frontend/playwright.config.ts`). E2E works because Playwright tests hit the API through the Vite proxy (`/api` → `:8001`), which does not enforce CORS. A real user on `:5174` would be blocked.
