# Research: Reports and Analytics Module

**Date**: 2026-07-30 | **Phase**: Phase 0 (Design Decisions)

## Decision Record

### D-001: Report Module Organization

**Decision**: Create a dedicated `app/services/reports/` package with one file per report type, plus a shared query utilities module.

**Rationale**: Report queries are cross-domain (spanning delivery, payment, token, customer tables). Keeping them separate from existing domain services avoids circular dependencies and keeps domain services focused on CRUD/workflow.

**Alternatives Considered**:
- Single `app/services/reports.py` — would become too large (6 report types)
- Adding report methods to existing services — would couple reporting to domain logic and create cross-dependency issues

---

### D-002: CSV Export Strategy

**Decision**: Generate CSV data in-memory as a string using Python's `csv` module with `io.StringIO`, returning as a `StreamingResponse` with `media_type="text/csv"` and appropriate `Content-Disposition` header. Add `Accept: text/csv` or `?format=csv` query parameter to each report endpoint.

**Rationale**: Expected data volumes (<5000 rows per report) fit comfortably in memory. The existing FastAPI `StreamingResponse` pattern is well-established. No need for streaming generators.

**Alternatives Considered**:
- Streaming generator — over-engineering for expected volumes
- Server-side file generation — unnecessary I/O overhead

---

### D-003: Caching Strategy

**Decision**: Use a simple in-memory dictionary cache in the report service layer with configurable TTL. Cache keyed by report type + all filter parameters (hashed). For Phase 1, implement a basic cache with 5-minute TTL for dashboard and revenue reports only. Cache invalidation is manual (bypass with `?refresh=true` query param).

**Rationale**: Most expensive reports (revenue, route delivery over 6 months) benefit from caching within a session. Dashboard data changes infrequently during the day. Expose `?refresh=true` to allow force-refresh without waiting for TTL.

**Alternatives Considered**:
- Redis — not worth the infrastructure dependency for this volume
- Database materialized views — good but adds schema complexity; can be added later
- No caching — acceptable for current scale but spec requires it

---

### D-004: Date Range Filter API Design

**Decision**: Support both preset strings (`"today"`, `"yesterday"`, `"this_week"`, `"last_week"`, `"this_month"`, `"last_month"`, `"this_year"`) and explicit `from_date`/`to_date` query params. If `preset` is provided, `from_date`/`to_date` are ignored. If only `from_date` is given, `to_date` defaults to `from_date`. If neither is given, default to `"this_month"`.

**Rationale**: Presets provide quick common queries. Custom ranges give flexibility for ad-hoc analysis. Sensible defaults make the API easy to use.

**Alternatives Considered**:
- Only custom ranges — less usable for common queries
- Only presets — too restrictive for business analysis

---

### D-005: Route-Level Access for DELIVERY_PARTNER

**Decision**: DELIVERY_PARTNER role can only access reports for their assigned route(s). The report service detects the user's role, and if DELIVERY_PARTNER, automatically filters by the routes assigned to that partner (via `user.employee.route_id` relationship). If the partner explicitly provides a `route_id` parameter that doesn't match their assigned route, return 403.

**Rationale**: This follows the principle of least privilege. The existing `Employee` model has a `route_id` FK, and the `User` has a nullable `employee_id` FK linking to `Employee`.

**Implementation note**: Requires checking `current_user.employee` and `current_user.employee.route_id` in the service layer, not the router.

---

### D-006: Report Response Format

**Decision**: Every report response wraps data in a consistent envelope: `{"data": [...], "total": N, "page": N, "page_size": N, "generated_at": "ISO datetime"}`. CSV export uses the same field names as the JSON response, with one header row.

**Rationale**: Consistent envelope simplifies frontend consumption. The existing `DeliverySessionListResponse` pattern (`sessions` + `total`) is adapted to a generic envelope with metadata.

**Alternatives Considered**:
- Flat list response — loses pagination metadata
- Different CSV format — confusing for frontend developers

---

### D-007: Available Database Indexes

**Decision**: The following existing columns/indexes are critical for report query performance:

| Table | Column | Why Needed |
|-------|--------|-----------|
| `delivery_sessions` | `delivery_date`, `route_id`, `shift` | Route delivery reports filter by date range and route |
| `delivery_sessions` | `status` | Dashboard counts unclosed sessions |
| `daily_deliveries` | `session_id`, `delivery_status` | Joining sessions to deliveries, filtering by status |
| `customer_payments` | `payment_date`, `customer_id` | Revenue and collection reports |
| `customer_bills` | `bill_period_start`, `bill_period_end`, `customer_id` | Collection efficiency reports |
| `token_book_issues` | `token_identity_id`, `status` | Token utilization reports |
| `subscriptions` | `customer_id`, `milk_type_id`, `is_active` | Expected quantity calculation |

If missing, add indexes on `daily_deliveries.delivery_status`, `customer_payments.payment_date`, and `customer_bills.bill_period_start` for report query performance.

---

### D-008: Filter Parameter Validation Patterns

**Decision**: Follow the existing pattern — use optional query parameters with `Query(default=None)` in routers, pass to services as kwargs. Report-specific validation (e.g., date range logic, role-based access) lives in the service layer, not the router.

**Rationale**: Consistent with existing codebase. Keeps routers thin.

---

### D-009: Trend Detection for Consumption Reports

**Decision**: For customer consumption trend, compare the average daily quantity of the most recent 7 days against the average of the preceding 21 days. If the recent average is >10% higher, mark as `"increasing"`. If >10% lower, mark as `"declining"`. Otherwise, `"stable"`. Require at least 14 days of data to compute.

**Rationale**: This is a reasonable heuristic for consumption monitoring. The 10% threshold avoids flagging normal daily variance.

---

### D-010: Outstanding Balance Aging for Collection Reports

**Decision**: In collection efficiency reports, add an aging breakdown per customer: current (0-30 days), 31-60 days, 61-90 days, 90+ days. Aging is computed from bill due dates relative to the report date.

**Rationale**: Aging breakdown is standard for accounts receivable and helps prioritize collection efforts.
