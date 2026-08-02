# Feature Specification: Reports Pages

**Feature Branch**: `009-reports-pages`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "we gonna implement phase 7 reports pages"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Operational Dashboard Overview (Priority: P1)

As an Owner (and any signed-in role), I want to open the app and land on an operational dashboard that shows today's key performance indicators, so that I get a quick daily overview without running any individual report.

**Why this priority**: This is the P0 story (US-060) and the landing experience. It is the first screen a user sees and gives immediate value; every other report page is a deeper drill-down that remains useful only after the overview exists.

**Independent Test**: Can be fully tested by opening the app's home route, seeing the KPI grid (session count, milk loaded/delivered, cash collected, deliveries by status, pending tokens, unclosed/unbalanced sessions) render with today's numbers, and confirming the values match the session/delivery data for the current date.

**Acceptance Scenarios**:

1. **Given** a user who has signed in with any active role, **When** they open the app's home page, **Then** they land on the dashboard and see today's KPI cards: sessions count, milk loaded, milk delivered, cash collected, deliveries by status, pending tokens, and unclosed/unbalanced sessions.
2. **Given** a delivery session exists for today with DELIVERED and CASH_SALE records, **When** the dashboard loads, **Then** the milk loaded/delivered, cash collected, and deliveries-by-status figures match the session data.
3. **Given** no session exists for today, **When** the dashboard loads, **Then** it shows zero-value KPIs with a friendly empty message rather than an error.
4. **Given** the dashboard is loading or the API fails, **When** the page renders, **Then** a loading state is shown and a failed load surfaces an error message without a blank screen.

---

### User Story 2 - Route Delivery Performance Report (Priority: P1)

As an Owner/Admin, I want to view route delivery performance over a date range, so that I can analyze how much milk each route loaded, delivered, collected as cash, registered as tokens, returned, and whether each route is balanced.

**Why this priority**: This is the P1 operational report (US-061) with the most direct link to the daily delivery workflow — it turns session data into per-route efficiency metrics used every day.

**Independent Test**: Can be fully tested by selecting a date range and a route, seeing the per-route table with loaded/delivered/cash/token/returned quantities and the shortage/surplus flag, then comparing a row's numbers to the actual session totals.

**Acceptance Scenarios**:

1. **Given** sessions exist for the selected period, **When** an Owner selects a date range (or a preset like Today/Week/Month) and optionally a route, **Then** the report shows one row per route with session count, delivery count, loaded/delivered/token/cash/returned quantities, shortage/surplus, and a balanced indicator.
2. **Given** the report is generated, **When** the Owner views it, **Then** a summary row showing totals across the filtered set is displayed alongside the per-route rows.
3. **Given** a DELIVERY_PARTNER role user, **When** they open the report, **Then** only their own route is shown and other routes are not accessible.
4. **Given** an empty period, **When** the report loads, **Then** a friendly empty state is shown instead of an error.

---

### User Story 3 - Revenue Report (Priority: P1)

As an Owner, I want to view revenue over a date range, optionally filtered by route or milk type, so that I can track financial performance by source, payment mode, route, and milk type.

**Why this priority**: This is the P1 financial report (US-062). Revenue visibility is core to running the business, and it is restricted to the Owner as the financial owner.

**Independent Test**: Can be fully tested by selecting a date range and seeing the total revenue with breakdowns by source (token book vs customer bills), payment mode, route, and milk type, then narrowing by route/milk type and confirming the breakdown updates.

**Acceptance Scenarios**:

1. **Given** recorded token-book payments and customer bill payments in the period, **When** an Owner opens the Revenue report with a date range, **Then** the total revenue and breakdowns by source, payment mode, route, and milk type are displayed with percentages.
2. **Given** the Revenue report, **When** an Owner applies a route or milk-type filter, **Then** only the filtered revenue remains in the total and breakdowns.
3. **Given** a non-Owner role user, **When** they navigate to the Revenue report, **Then** access is denied and the access-denied view is shown.
4. **Given** no payments in the period, **When** the report loads, **Then** it shows zero revenue with a friendly empty state.

---

### User Story 4 - Customer Consumption Report (Priority: P1)

As an Owner/Admin/Checker, I want to view a selected customer's consumption over a date range, so that I can understand buying patterns and spot trends.

**Why this priority**: This is the P1 customer insight report (US-063). It connects delivery history to customer-level behavior and feeds the later AI BI goals.

**Independent Test**: Can be fully tested by selecting a customer and date range, seeing the daily consumption trend, the total/average consumption, and a trend badge (increasing/declining/stable) that matches the recent vs preceding averages.

**Acceptance Scenarios**:

1. **Given** a customer with delivery records in the period, **When** an Owner selects the customer and date range, **Then** the report shows daily quantities, total consumption, average daily consumption, and days with data.
2. **Given** the report is generated, **When** the Owner inspects it, **Then** a trend badge indicates whether consumption is increasing, declining, or stable based on recent vs preceding averages.
3. **Given** a customer selector, **When** the Owner changes the selected customer, **Then** the report updates to that customer's data.
4. **Given** a nonexistent or inactive customer is selected, **When** the report loads, **Then** a clear not-found message is shown.

---

### User Story 5 - Token Utilization Report (Priority: P1)

As an Owner/Admin, I want to view token book utilization, so that I can manage token book inventory and identify customers running low on sheets.

**Why this priority**: This is the P1 inventory report (US-064). Low-token detection prevents delivery interruptions when books run out.

**Independent Test**: Can be fully tested by opening the report, seeing per-customer utilization percentages with visual bars, filtering by route/customer, and adjusting the low threshold so books below it are flagged.

**Acceptance Scenarios**:

1. **Given** customers with issued token books, **When** an Owner opens the Token Utilization report, **Then** each customer shows sheets used, sheets remaining, utilization percentage, and the count of books below the threshold.
2. **Given** the report, **When** the Owner changes the low threshold (e.g., 20% to 30%), **Then** the flagged low-book count updates accordingly.
3. **Given** the report, **When** the Owner filters by route or customer, **Then** only matching customers are shown.
4. **Given** a DELIVERY_PARTNER role user, **When** they open the report, **Then** only their own route's customers are shown.

---

### User Story 6 - Collection Efficiency Report (Priority: P2)

As an Owner/Admin, I want to view collection efficiency with aging analysis, so that I can manage receivables and follow up on overdue amounts.

**Why this priority**: This is the P2 receivables report (US-065). It is valuable for collections follow-up but depends on billing/payment data that the P1 reports also surface, so it is lower priority.

**Independent Test**: Can be fully tested by opening the report, seeing each customer's billed/paid/balance and collection percentage, and confirming the aging buckets (current, 31–60, 61–90, 90+) are color-coded and sum to the balance.

**Acceptance Scenarios**:

1. **Given** customers with bills and payments, **When** an Owner opens the Collection Efficiency report with a date range, **Then** each customer shows total billed, total paid, balance, collection percentage, last bill/payment dates, and aging buckets.
2. **Given** the report, **When** the Owner inspects the aging buckets, **Then** buckets are color-coded by severity (e.g., older = more severe) and each customer's buckets sum to their balance.
3. **Given** the report, **When** the Owner applies a route filter or minimum outstanding filter, **Then** only matching customers are shown.
4. **Given** an overall view, **When** the report loads, **Then** the overall collection percentage across the filtered set is displayed.

---

### Edge Cases

- **No data in period**: Every report shows a friendly empty state with zero-value summaries instead of an error.
- **Loading and API failure**: Each page shows a loading state while fetching and an error message on failure, without losing the chosen filters.
- **Role restrictions**: CHECKER/DELIVERY_PARTNER are denied on Owner-only reports (Revenue) via the access-denied view; DELIVERY_PARTNER sees only their own route on route-scoped reports.
- **Changing filters**: Re-selecting a preset or date range re-fetches the report; stale results from a previous selection are not shown.
- **Low threshold boundary**: Setting the low threshold to 100% flags all books; setting it to 1% flags almost none — the threshold applies consistently.
- **Customer with no token book**: Such customers are absent from the token utilization report (no false rows).
- **CSV export failure**: A failed export surfaces an error message; the on-screen table remains usable.

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): Frontend-only feature — no backend changes. Pages/API modules follow the established `types → api → hooks → pages` layering; the existing backend reports routers/services/schemas are consumed as-is.
- **Role-Based Access Control** (Principle II): Each report page's client-side RoleGuard MUST match the backend report endpoint's role requirement (dashboard: all authenticated roles; route-delivery: all roles with per-route restriction; revenue: OWNER; consumption: OWNER/ADMIN/CHECKER; token-utilization: OWNER/ADMIN; collection-efficiency: OWNER/ADMIN). The backend already enforces these; the client mirrors them for navigation/UX.
- **Soft Deletes** (Principle IV): No new entities; reports are read-only aggregations over existing data, so no delete paths exist.
- **Schema-Driven Contracts** (Principle V): Frontend TypeScript interfaces mirror the existing backend report response schemas exactly; no new backend schemas are introduced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST render an operational dashboard at the app's home route showing today's KPI cards: total sessions, milk loaded, milk delivered, cash collected, deliveries by status, pending tokens, and unclosed/unbalanced sessions.
- **FR-002**: The system MUST show a loading state while the dashboard loads and a friendly zero-value state when there is no data for the day.
- **FR-003**: The system MUST render a Route Delivery report with a date-range (or preset Today/Week/Month) selector and an optional route selector, showing per-route session count, delivery count, loaded/delivered/token/cash/returned quantities, shortage/surplus, and a balanced indicator, plus a summary row.
- **FR-004**: The system MUST render a Revenue report with a date-range (or preset) selector and optional route and milk-type filters, showing total revenue and breakdowns by source, payment mode, route, and milk type with percentages.
- **FR-005**: The system MUST restrict the Revenue report to the OWNER role (navigation hidden for others; direct URL access shows the access-denied view).
- **FR-006**: The system MUST render a Customer Consumption report with a customer selector and date range, showing daily quantities, total/average consumption, days with data, and a trend badge (increasing/declining/stable) based on recent vs preceding averages.
- **FR-007**: The system MUST render a Token Utilization report with route/customer filters and an adjustable low threshold, showing per-customer sheets used, sheets remaining, utilization percentage with a visual bar, and the count of books below the threshold.
- **FR-008**: The system MUST render a Collection Efficiency report with a date range and route/minimum-outstanding filters, showing per-customer billed/paid/balance, collection percentage, last bill/payment dates, and color-coded aging buckets (current, 31–60, 61–90, 90+) that sum to the balance, plus an overall collection percentage.
- **FR-009**: For the list-style reports (route delivery, token utilization, collection efficiency), the system MUST provide a CSV download of the current filtered result set.
- **FR-010**: Every report page MUST show a loading state while fetching, a friendly empty state when the result set is empty, and an error notification on failed requests without discarding the user's selected filters.
- **FR-011**: The system MUST apply per-route access for DELIVERY_PARTNER users on route-scoped reports so they only ever see their own route.
- **FR-012**: Report queries MUST be cached per user + filter combination so repeat views of the same report are fast, and MUST allow an explicit refresh to bypass the cache.

### Key Entities *(include if feature involves data)*

- **Operational Dashboard**: A snapshot of today's KPIs — total sessions, milk loaded/delivered, cash collected, deliveries by status, pending tokens, and unclosed/unbalanced session counts.
- **Route Delivery Report**: Per-route delivery performance over a period — session count, delivery count, loaded/delivered/token-registered/cash/returned quantities, shortage/surplus, balanced flag, and a totals summary.
- **Revenue Report**: Total revenue plus breakdowns by source (token book vs customer bills), payment mode, route, and milk type, with percentages.
- **Customer Consumption Report**: A customer's daily delivered quantities over a period with total/average consumption, days with data, and a computed trend (increasing/declining/stable).
- **Token Utilization Report**: Per-customer token book usage — sheets used/remaining, utilization percentage, books below a configurable threshold.
- **Collection Efficiency Report**: Per-customer billed/paid/balance, collection percentage, last bill/payment dates, and aging buckets (current, 31–60, 61–90, 90+).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A signed-in user can open the app home route and see today's complete dashboard KPI set in under 2 seconds of load time on a normal connection.
- **SC-002**: 100% of Route Delivery report rows match the underlying session/delivery totals for the selected period and route.
- **SC-003**: 100% of Revenue report totals and breakdowns match the sum of recorded payments for the selected filters.
- **SC-004**: 100% of Token Utilization customers below the chosen threshold are flagged, and none above it are.
- **SC-005**: For every customer in the Collection Efficiency report, the aging buckets sum exactly to the customer's displayed balance.
- **SC-006**: Non-Owner roles cannot reach the Revenue report through navigation or direct URL; DELIVERY_PARTNER sees only their own route on route-scoped reports.
- **SC-007**: Every report can be reached, filtered, and its results verified end-to-end against seed data in under 5 minutes by a first-time user.
- **SC-008**: CSV export works for all list-style reports and produces rows matching the on-screen filtered data.

## Assumptions

- This feature is frontend-only and consumes the existing backend `/reports/*` endpoints unchanged (`/dashboard`, `/route-delivery`, `/revenue`, `/collection-efficiency`, `/customer/{id}/consumption`, `/token-utilization`).
- The backend already provides: date-range presets, pagination, in-memory caching (bypassable via `refresh=true`), CSV export via `format=csv`, and role-based route restriction. The frontend surfaces these as filters, download buttons, and role guards.
- Client-side RoleGuards mirror the backend report endpoint roles: Dashboard and Route Delivery for all authenticated roles, Revenue OWNER-only, Consumption OWNER/ADMIN/CHECKER, Token Utilization and Collection Efficiency OWNER/ADMIN.
- The dashboard becomes the app's root route (existing `DashboardPage` placeholder is replaced or superseded by the reports dashboard per T136).
- Report data volumes are small in this deployment (one dairy, handful of routes); the pages render full result sets without virtualized tables.
- Existing UI patterns (DataTable, Badge, Card/KPI, Select, Input, Button, PageHeader, LoadingSpinner, EmptyState, ConfirmDialog-free read-only pages, role guards, react-query hooks) are reused; no new component library is introduced.
- CSV downloads reuse the browser download pattern used elsewhere in the app; no server-side file storage is needed.
- The seed data may not contain sessions/deliveries/bills/payments; E2E validation for this phase first creates delivery data through the existing Delivery pages so reports have real numbers to display.
