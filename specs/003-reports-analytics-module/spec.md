# Feature Specification: Reports and Analytics Module

**Feature Branch**: `003-reports-analytics-module`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "now we need to implement reports and analytics module"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route-Wise Daily/Weekly/Monthly Reports (Priority: P1)

The business owner wants to see delivery performance per route. They select a route, choose a date range (today, this week, this month, or custom), and view the total milk loaded, total delivered, total collected cash, and any shortages. This helps them identify underperforming routes or delivery partners.

**Why this priority**: Route performance is the most fundamental operational metric. Without it, the business cannot identify which routes are profitable or which delivery partners need attention.

**Independent Test**: Can be fully tested by creating a session for a specific route, recording deliveries with known quantities, and verifying the report returns the correct loaded vs delivered vs cash numbers for that route.

**Acceptance Scenarios**:

1. **Given** a route with 3 active customers each subscribing to 2L of milk, **When** the owner views the route report for today, **Then** the report shows 6L loaded, 6L delivered (assuming all were delivered), and the correct cash collection.
2. **Given** a route where one customer had a delivery exception (vacation), **When** the owner views the route report, **Then** the loaded quantity excludes the excepted customer's quantity.
3. **Given** a route with morning and evening shifts, **When** the owner views the route report filtered to "morning" only, **Then** only morning session data is included.
4. **Given** a date range spanning multiple weeks, **When** the owner groups results by week, **Then** the report shows weekly subtotals for loaded, delivered, and collected amounts.

---

### User Story 2 - Revenue Reports (Priority: P1)

The business owner wants to understand overall revenue trends. They view total revenue (from token book payments and customer bill payments) over custom date ranges, broken down by milk type, route, or payment mode. This helps them track business growth and seasonal patterns.

**Why this priority**: Revenue visibility is critical for any business. Without it, the owner cannot make informed decisions about pricing, staffing, or expansion.

**Independent Test**: Can be fully tested by creating known payments (token book payments + customer payments) across different milk types and routes, then verifying that the revenue report aggregates them correctly.

**Acceptance Scenarios**:

1. **Given** 5 token book payments (total 5000 INR) and 3 customer bill payments (total 3000 INR) exist in the current month, **When** the owner views the monthly revenue report, **Then** total revenue shows 8000 INR with the correct breakdown by source.
2. **Given** revenue data exists across 3 milk types, **When** the owner views revenue grouped by milk type, **Then** each milk type shows its subtotal with a percentage contribution.
3. **Given** a date range with no payments or bills, **When** the owner views the revenue report, **Then** the report shows zero revenue with a clear message (no error).

---

### User Story 3 - Collection Efficiency Reports (Priority: P2)

The business owner wants to track how efficiently they are collecting payments from customers. They view total billed amounts vs total collected amounts over a period, with outstanding balances per customer. This helps them follow up on overdue payments and identify defaulters.

**Why this priority**: Cash flow is critical. Collection efficiency directly impacts business liquidity. This is P2 because revenue (P1) must exist before collection efficiency can be measured.

**Independent Test**: Can be fully tested by generating bills for known customers with known delivered quantities, recording partial/full payments, and verifying that the collection efficiency percentage is calculated correctly.

**Acceptance Scenarios**:

1. **Given** a customer was billed 1000 INR for the month and has paid 600 INR, **When** the owner views collection efficiency for that customer, **Then** the report shows 60% collection rate with 400 INR outstanding.
2. **Given** a date range with generated bills but no payments recorded, **When** the owner views collection efficiency, **Then** the report shows 0% collection with the full billed amount as outstanding.
3. **Given** the owner filters by route, **When** viewing collection efficiency, **Then** the report aggregates only customers belonging to that route.

---

### User Story 4 - Customer-Wise Consumption Reports (Priority: P2)

The owner or admin wants to see a specific customer's consumption history — how much milk they ordered per day/week/month, what milk types, and any changes in consumption patterns. This helps identify growing customers, declining customers, or opportunities for upselling.

**Why this priority**: Customer retention and growth require visibility into individual consumption trends. This is P2 because aggregate reports (P1) are more immediately valuable.

**Independent Test**: Can be fully tested by creating a customer with a subscription, recording deliveries over 30 days, and verifying that the consumption report shows daily quantities with the correct totals and averages.

**Acceptance Scenarios**:

1. **Given** a customer has been receiving 2L daily for 30 days, **When** the owner views the monthly consumption report, **Then** the report shows 60L total consumption with a 2L/day average.
2. **Given** a customer's consumption dropped from 2L/day to 1L/day mid-month, **When** viewing the consumption trend, **Then** the report shows the decline with a date marker.
3. **Given** a non-existent customer ID, **When** querying consumption, **Then** the system returns a clear not-found error.

---

### User Story 5 - Token Book Utilization Reports (Priority: P3)

The business owner wants to see how token books are being utilized — how many sheets have been used vs remaining per customer, how many books are active vs completed, and which customers need new books soon. This helps manage token book inventory and prevent delivery disruptions.

**Why this priority**: Token book management is important for operational smoothness, but it is less critical than revenue and route performance reporting.

**Independent Test**: Can be fully tested by creating token identities with book issues, recording deliveries that consume sheets, and verifying that the utilization report shows correct used/remaining counts.

**Acceptance Scenarios**:

1. **Given** a customer has a token book with 30 sheets and 20 sheets have been used via registered deliveries, **When** viewing token utilization, **Then** the report shows 20 used, 10 remaining, 66% utilization.
2. **Given** a customer has 2 token books — one active and one completed, **When** viewing utilization, **Then** the report shows utilization for the active book and marks the completed book as fully utilized.
3. **Given** no token books exist for a customer, **When** viewing utilization, **Then** the report shows zero utilization with a note that no books are issued.

---

### User Story 6 - Operational Summary Dashboard (Priority: P3)

The owner wants a single-page overview of today's operations: number of active sessions, total milk loaded vs delivered, total cash collected, pending deliveries, and any flagged issues (unbalanced sessions, unclosed sessions from previous days). This provides a quick pulse-check of the day's business.

**Why this priority**: A dashboard view is valuable for daily management but depends on all other reports being in place. It is the integration point for all reporting data.

**Independent Test**: Can be fully tested by creating sessions across multiple routes, recording various delivery states, and verifying that the dashboard summary correctly aggregates all operational metrics for the current day.

**Acceptance Scenarios**:

1. **Given** 3 active sessions today (Route A, B, C) with various states, **When** viewing the dashboard, **Then** it shows: total sessions count, total loaded milk, total delivered milk, total cash collected, pending count.
2. **Given** a session from yesterday was never closed, **When** viewing the dashboard, **Then** it shows a flag/warning for the unclosed session.
3. **Given** a session has a reconciliation difference (shortage), **When** viewing the dashboard, **Then** it shows a flag for the unbalanced session.

### Edge Cases

- What happens when querying a date range with no data? Return empty results with zero counts, not an error.
- What happens when a customer has both active and inactive subscriptions? Only active subscription deliveries should be counted for "expected" quantities; historical deliveries are counted regardless.
- What happens when a session is reopened and deliveries are edited? Reports should reflect the latest state (edits are applied), not the original state.
- How does the system handle partial months for monthly reports? A month with only 15 days of data should show 15 days of totals with a note that the period is incomplete.
- What happens when a payment is recorded after a bill is generated? Outstanding balance should update — reports should always reflect the current state, not a snapshot.
- How are refunds or adjustments handled in revenue reports? Negative line items (if supported) should reduce revenue totals.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): All code MUST be placed in the correct layer (routers, services, models, schemas, core). No business logic in routers. Report generation logic belongs in services; routers only handle request parameters and response formatting.
- **Role-Based Access Control** (Principle II): All report endpoints MUST require authentication. Report access should be: OWNER — full access to all reports; ADMIN — route, customer consumption, and collection reports (no revenue/salary reports); CHECKER — read-only access to delivery status reports; DELIVERY_PARTNER — access only to their assigned route's route delivery reports (US1) and operational dashboard (US6). Partners cannot access financial reports (revenue, collection efficiency, token utilization).
- **Soft Deletes** (Principle IV): Reports MUST respect soft deletes — inactive customers, routes, and milk types should be excluded from aggregate reports unless explicitly requested.
- **Schema-Driven Contracts** (Principle V): Each report MUST have dedicated Response schemas. Reports are read-only — no Create/Update schemas are needed, but a ReportRequest schema with filter parameters and a ReportResponse schema are required.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide route-wise delivery reports with loaded quantity, delivered quantity, returned quantity, cash collected, and shortage/surplus, filterable by date range (daily/weekly/monthly/custom) and shift (morning/evening/both).
- **FR-002**: System MUST provide revenue reports aggregating all payment sources (token book payments + customer bill payments), filterable by date range, milk type, route, and payment mode.
- **FR-003**: System MUST provide collection efficiency reports showing billed vs paid vs outstanding per customer, with aggregate totals per route, filterable by date range.
- **FR-004**: System MUST provide customer-wise consumption reports showing daily/weekly/monthly quantities delivered, by milk type, with trend data over a date range.
- **FR-005**: System MUST provide token book utilization reports showing used sheets, remaining sheets, utilization percentage, and status per customer/identity, filterable by route.
- **FR-006**: System MUST provide an operational summary dashboard showing today's key metrics: active sessions, total loaded, total delivered, total collected, pending deliveries, unclosed sessions, and unbalanced sessions.
- **FR-007**: System MUST support CSV export for all reports in addition to JSON API responses.
- **FR-008**: System MUST paginate report results when the result set exceeds a configurable page size, with total count and page number in the response.
- **FR-009**: System MUST cache report results that are expensive to compute (e.g., monthly revenue) with a configurable TTL, invalidating when underlying data changes.
- **FR-010**: System MUST enforce role-based access on each report endpoint, restricting sensitive reports (revenue, salary) to OWNER role only.

### Key Entities *(include if feature involves data)*

- **ReportRequest**: A filter specification containing date range (from_date, to_date, or preset), optional route_id, optional customer_id, optional milk_type_id, optional shift, optional group_by (day/week/month), and optional page/page_size for pagination.
- **RouteDeliveryReport**: Aggregated delivery data per route — total loaded quantity, total delivered quantity, total returned quantity, total cash collected, total token-registered quantity, shortage/surplus, number of sessions, number of deliveries.
- **RevenueReport**: Aggregated financial data — total revenue, breakdown by source (token_book_payments, customer_bill_payments), breakdown by milk type, breakdown by route, breakdown by payment mode, with date grouping.
- **CollectionEfficiencyReport**: Per-customer or per-route collection metrics — total billed, total paid, total outstanding, collection percentage, payment count, last payment date.
- **CustomerConsumptionReport**: Per-customer delivery history — daily/weekly quantities by milk type, total consumption, average daily consumption, trend indicator (increasing/stable/declining), date range summary.
- **TokenUtilizationReport**: Token book usage metrics — total books issued, active books, completed books, total sheets used, total sheets remaining, utilization percentage per customer or identity.
- **OperationalDashboard**: A snapshot of today's metrics — session count, total loaded, total delivered, total collected, delivery counts by status (DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED), pending token count, unclosed session count, unbalanced session count.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Business owner can view route-wise delivery performance for any date range and see loaded vs delivered vs cash collected within 5 seconds for data spanning up to 6 months.
- **SC-002**: Business owner can view revenue trends broken down by milk type, route, or payment mode and identify the top 3 revenue-generating routes and milk types.
- **SC-003**: Business owner can identify customers with outstanding balances exceeding 30 days and view their contact information for follow-up.
- **SC-004**: Business owner can identify token books that are below 20% remaining sheets and proactively issue new books before they run out.
- **SC-005**: Business owner can view today's operational dashboard and identify any unclosed or unbalanced sessions within 3 seconds.
- **SC-006**: All report data is accurate to within 0.01 units when cross-validated against individual transaction records.
- **SC-007**: Report data respects soft deletes — inactive customers, routes, and milk types do not appear in aggregate reports by default.

## Assumptions

- Reports will be delivered as JSON API responses with a CSV export option. No frontend/UI is in scope — this is a backend-only feature (Sprint 9 will handle frontend). Frontend will consume these API endpoints.
- Reports compute data in real-time from existing database tables. No separate data warehouse or reporting database is needed. The existing PostgreSQL database is sufficient for the expected data volume.
- Existing authentication and role-based access control will be reused. No new auth mechanisms are needed.
- Reports are read-only — no Create, Update, or Delete operations are needed. Only dedicated Request and Response schemas are required.
- Date ranges support flexible queries: preset options (today, yesterday, this_week, last_week, this_month, last_month, this_year) and custom (from_date, to_date).
- CSV export returns the same data as the JSON response in comma-separated format with headers, using standard MIME type `text/csv`.
- Pagination follows the same pattern as the existing delivery session list endpoint (page, page_size, total_count, total_pages).
- The existing data model is sufficient — no new database tables are required. Reports are derived from queries on existing tables (delivery_sessions, daily_deliveries, customer_payments, customer_bills, token_book_issues, token_book_payments, etc.).
- Report caching may use a simple in-memory or database-backed cache, but this is an optimization detail for the implementation phase.
- The operational dashboard is scoped to "today" only — historical dashboard snapshots are out of scope for v1.
- DELIVERY_PARTNER role can only access route delivery reports (US1) and the operational dashboard (US6), both filtered to their assigned route. Partners have no access to revenue, collection efficiency, customer consumption, or token utilization reports.

## Clarifications

### Session 2026-07-30

- Q: Which reports can a DELIVERY_PARTNER access? → A: Route delivery reports (US1) and operational dashboard (US6) only, filtered to their assigned route. No financial or customer-wide reports.
