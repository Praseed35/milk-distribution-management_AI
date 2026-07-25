# TECH_DEBT.md - Technical Debt and Known Issues

> Issues that should be addressed but haven't been yet.

---

## High Priority

### 1. Hardcoded Secret Key
**File**: `app/core/config.py`
```python
SECRET_KEY = "milk_management_secret_key_2026"
```
Should use environment variable. Security risk in production.

### 2. Database Name Typo
Database is `milk_managemen_ai` (missing 't' in management). Consistent everywhere but confusing.

### 3. No CORS Configuration
No CORS middleware configured. Required before frontend integration (Sprint 9).

### 4. Inconsistent Exception Hierarchy
`BusinessException` base class exists in `exceptions/base.py` but many exceptions extend `Exception` directly:
- `route.py`: Extend `BusinessException` ✓
- `milk_type.py`: Extend `BusinessException` ✓
- `user.py`: Extend `Exception` directly
- `customer.py`: Extend `Exception` directly
- `employee.py`: Extend `Exception` directly
- `subscription.py`: Extend `Exception` directly
- `delivery_exception.py`: Extend `Exception` directly
- `token_book.py`: Extend `Exception` directly

---

## Medium Priority

### 5. Constants Not Enforced
Status/role enums defined in `constants/` are not used in models or schemas:
- `UserRole` enum not used - roles stored as plain strings
- `Shift` enum imported in subscription schema but not used as constraint
- `SessionStatus`, `TokenStatus`, `DeliveryStatus` defined but never referenced
- `BookIssueStatus`, `PaymentStatus`, `PaymentMode` defined but not enforced

### 6. Users Router Missing CRUD
`/users` only has GET (list) and POST (create). No update or delete endpoints.

### 7. No Pagination
All list endpoints return every active record. Will cause performance issues with large datasets.

### 8. No Filtering/Search
List endpoints have no query parameters. Can't filter by status, route, date range, etc.

### 9. Hardcoded Values in Services
- Customer code generation: `f"C{next_number:05d}"` - hardcoded format
- Employee code generation: `f"E{next_number:05d}"` - hardcoded format
- Default statuses: "ACTIVE", "WAITING", "PENDING" hardcoded in service code

### 10. Empty Directories
`app/common/` and `app/utils/` exist but contain no code. Should be removed or utilized.

---

## Low Priority

### 11. Service Return Type Inconsistency
Some services return SQLAlchemy model objects, others return dicts. Mixed patterns:
- Routes, MilkTypes, Customers: Return model objects
- Subscriptions, DeliveryExceptions, TokenBooks: Return manually constructed dicts

### 12. No Request ID / Logging
No structured logging or request ID tracking for debugging.

### 13. No Rate Limiting
No rate limiting on any endpoint.

### 14. Test DB Name Matching
Test DB URL hardcoded to same production DB. No separate test database.

### 15. User Service Uses Different Pattern
`user_service.create()` returns `None` on duplicate instead of raising exception (inconsistent with other services).

### 16. User Model Missing Timestamps
The `users` table doesn't have `created_at`/`updated_at` columns unlike all other tables.

---

## Architecture Improvements Needed

### For Sprint 3+ (Daily Delivery Management)
- Need a proper delivery session/daily log table
- Need shift-based delivery tracking
- Need route-day assignment capability

### For Sprint 5+ (Reconciliation)
- Need daily totals aggregation
- Need cash collection tracking
- Need discrepancy detection

### For Sprint 6+ (Payment Management)
- Need comprehensive payment ledger
- Need advance payment tracking
- Need bill generation

### For Sprint 9+ (Frontend)
- API versioning (`/api/v1/`)
- CORS middleware
- OpenAPI customization (title, description, version)
- Request/response logging middleware
