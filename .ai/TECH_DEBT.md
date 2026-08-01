# TECH_DEBT.md - Technical Debt and Known Issues

> Issues that should be addressed but haven't been yet.

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

### 14. No Rate Limiting
No rate limiting on any endpoint.

### 15. Test DB Uses Production Database
Test DB URL defaults to same production PostgreSQL (`milk_managemen_ai`). No separate test database. While transaction rollback provides isolation, schema changes during test runs may affect production data.

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
- SECRET_KEY hardening (move to env variable)
- Comprehensive payment ledger / sheet-level token register
- Rate limiting

### Frontend-Specific
- `frontend/src/pages/reports/` exists but is empty (Phase 7 only) — payments pages are complete (Phase 6, specs/008)
- Root `README.md` and `frontend/README.md` historically stale — README frontend status now reflects Phases 1–6 (still says React 19/Vite 8, which matches actual React 19.2.8/Vite 8.2.0)
- `.ai/` docs previously reported 12 migrations / 343 tests — now 13 migrations / 379 tests (verified Aug 1, 2026)
- Backend `/payments/*` router (like most routers) has **no** `get_current_user` dependency — only `reports` and `auth` attach it. Client-side RoleGuards are the only enforcement on payment pages (noted in specs/008 spec.md). Fix backend-wide RBAC in a later sprint.
