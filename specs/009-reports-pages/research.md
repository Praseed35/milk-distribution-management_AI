# Research: Reports Pages (Phase 7)

> Phase 0 output — decisions resolving the unknowns in the Technical Context.

## R1: Report response shapes

**Decision**: Handle two distinct response shapes in `api/reports.ts` and `hooks/useReports.ts`:
- **Envelope** `{ data: T[], total, page, page_size, generated_at }` → route-delivery, token-utilization, collection-efficiency. Pages render `data` and, where relevant, a client-computed summary row.
- **Direct object** → revenue (`RevenueReport`), consumption (`CustomerConsumptionReport`), dashboard (`OperationalDashboard`). Pages render the object fields directly.

**Rationale**: Matches `app/routers/reports.py` exactly. `route_delivery`, `token_utilization`, and `collection_efficiency` endpoints return `_envelope(items, page, page_size)`; the revenue, consumption, and dashboard endpoints return the schema object itself.

**Alternatives considered**: Type the envelope generically (`Envelope<T>`) and reuse it for all three list-style reports — adopted. Rebuilding a summary server-side — rejected (no backend changes allowed).

## R2: Missing summary/totals in envelope responses

**Decision**: Compute summary rows client-side. For route-delivery, sum the item columns into a "Totals" row. For token-utilization, sum `total_sheets_used`/`total_sheets_remaining`/`total_books_issued` and derive `overall_utilization_percentage`. For collection-efficiency, sum `total_billed`/`total_paid`/`total_balance` and derive `overall_collection_percentage` from the sums.

**Rationale**: Although the backend schemas (`RouteDeliveryReport`, `TokenUtilizationReport`, `CollectionEfficiencyReport`) define summary/overall fields, the actual envelope responses contain only `data`. Deriving totals from the visible rows guarantees the displayed summary always matches the table (SC-002/SC-005).

**Alternatives considered**: Showing only the item table without a summary — rejected (spec FR-003/FR-006 require summary/overall figures).

## R3: Date-range and preset parameters

**Decision**: Add a `REPORT_PRESETS` constant to `src/lib/constants.ts` mirroring the backend's supported presets: `today`, `yesterday`, `this_week`, `last_week`, `this_month`, `last_month`, `this_year` (labels "Today", "Yesterday", "This Week", "Last Week", "This Month", "Last Month", "This Year"). Report pages offer a preset select OR from/to date inputs (mutually exclusive — choosing a preset clears the date inputs and vice versa). The default period is the current month (matches the backend default when no params are sent).

**Rationale**: The backend `resolve_date_range` (in `app/services/reports/common.py`) supports exactly these presets and defaults to month-to-date when nothing is provided.

**Alternatives considered**: Sending `from_date`/`to_date` only — rejected (presets give users quick, correct periods and match the backend capability).

## R4: CSV export

**Decision**: `api/reports.ts` exposes `exportReportCsv(path, params, filename)` that calls the endpoint with `params: { ...params, format: "csv" }` and `responseType: "blob"`, then triggers a download via `URL.createObjectURL` + a temporary `<a download>` element. CSV is offered on the three list-style reports (route-delivery, token-utilization, collection-efficiency), and optionally on revenue/consumption.

**Rationale**: The backend returns `StreamingResponse` (`text/csv`) with a `Content-Disposition` attachment header when `format=csv`. The shared Axios client defaults to JSON, so the blob response type must be set per-request; the download is done client-side with the browser's blob URL mechanism (no server file storage).

**Alternatives considered**: Opening `format=csv` in a new tab/window — rejected (hard to keep auth header consistent and UX is worse).

## R5: Cache refresh

**Decision**: Each list-style report page and the dashboard gets a "Refresh" button that calls the query with `refresh: true` (bypasses the backend in-memory cache) and invalidates the react-query key. `useReports.ts` includes `refresh` in the query key so a refresh re-fetches.

**Rationale**: The backend caches per user + filter combination (TTL 60–300s) and honors `?refresh=true`; this satisfies spec FR-012.

**Alternatives considered**: Relying only on the backend TTL — rejected (users expect explicit refresh on operational reports).

## R6: Role mapping (client RoleGuards)

**Decision**: Route guards mirror backend enforcement exactly:

| Route | Backend dependency | Client RoleGuard |
|---|---|---|
| `/reports/dashboard` | `require_role([OWNER, ADMIN, CHECKER, DELIVERY_PARTNER])` | all 4 roles |
| `/reports/route-delivery` | `get_current_user` (role-restricted to own route for DELIVERY_PARTNER) | all 4 roles |
| `/reports/revenue` | `require_role([OWNER])` | OWNER |
| `/reports/consumption/:customerId` | `require_role([OWNER, ADMIN, CHECKER])` | OWNER, ADMIN, CHECKER |
| `/reports/token-utilization` | `require_role([OWNER, ADMIN])` | OWNER, ADMIN |
| `/reports/collection-efficiency` | `require_role([OWNER, ADMIN])` | OWNER, ADMIN |

**Rationale**: Client-side guards must never be looser than server enforcement. `src/config/permissions.ts` already lists the Reports menu with these role sets; the guards match.

**Alternatives considered**: Making every report OWNER/ADMIN only — rejected (back-end explicitly allows CHECKER on dashboard/consumption and DELIVERY_PARTNER on dashboard/route-delivery, and the spec demands those roles see their data).

## R7: Dashboard as the root landing page

**Decision**: Replace the placeholder `src/pages/DashboardPage.tsx` with a thin component that `<Navigate to="/reports/dashboard" replace />` (or render the reports dashboard directly at `/`). Register `/reports/dashboard` in `App.tsx` as a real route; keep the top-level "Dashboard" nav item (path `/`) and the "Reports → Dashboard" item (path `/reports/dashboard`) both working.

**Rationale**: T136 requires `/reports/dashboard` to be the root redirect target; the nav already has both entries and both must resolve.

**Alternatives considered**: Rendering the same dashboard component at both paths — acceptable; the redirect approach is simpler and matches T136 wording.

## R8: Dashboard KPI grid contents

**Decision**: DashboardPage renders KPI cards from `OperationalDashboard`: total_sessions, total_milk_loaded, total_milk_delivered, total_cash_collected, deliveries_by_status (5 statuses), pending_token_count, unclosed_sessions, unbalanced_sessions, completed_not_closed. Cards use a new `KpiCard` primitive (title, value, optional sub-label) and a deliveries-by-status breakdown (colored badges or a small stacked card set).

**Rationale**: The backend dashboard service returns exactly these fields; the spec FR-001 lists them.

## R9: Trend badge and aging buckets

**Decision**: ConsumptionReportPage shows the backend `trend.change_percentage` (recent 7-day avg vs preceding 21-day avg) as a badge — "Increasing" (green, positive change), "Declining" (red, negative), "Stable" (slate, |change| below ~5%). CollectionEfficiencyPage renders the four aging buckets (`aging_current`, `aging_31_60`, `aging_61_90`, `aging_90_plus`) with color coding by severity (emerald → amber → orange → red) and validates visually that the four sum to `balance`.

**Rationale**: Matches the `ConsumptionTrend` and `CustomerCollectionItem` schemas and spec FR-006/FR-008.

**Alternatives considered**: Computing the trend client-side — rejected (backend already computes it).

## Consolidated unknowns log

All Technical Context unknowns are resolved (R1–R9). No `[NEEDS CLARIFICATION]` markers remain.
