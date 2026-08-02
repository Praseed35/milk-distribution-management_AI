# Implementation Plan: Reports Pages

**Branch**: `009-reports-pages` | **Date**: 2026-08-02 | **Spec**: `specs/009-reports-pages/spec.md`

**Input**: Feature specification from `/specs/009-reports-pages/spec.md`

## Summary

Frontend-only Phase 7: add six report pages to the React SPA that consume the existing backend `/reports/*` endpoints unchanged. The pages are Operational Dashboard (becomes the `/` landing target), Route Delivery, Revenue, Customer Consumption, Token Utilization, and Collection Efficiency. Work follows the established `types → api → hooks → pages` layering, adds `frontend/src/api/reports.ts` + `hooks/useReports.ts` + `types/reports.ts`, and registers six routes in `App.tsx` with RoleGuards that mirror the backend RBAC (Revenue OWNER-only). List-style reports get CSV download and an explicit refresh that bypasses the backend cache.

## Technical Context

**Language/Version**: TypeScript 6.x, React 19.x (verified from `frontend/package.json`)

**Primary Dependencies**: Vite 8, React Router v7 (v6-style API), Axios (existing `src/api/client.ts`, `baseURL: "/api/v1"`), TanStack Query v5, Tailwind CSS 4, react-hot-toast; existing UI kit in `src/components/ui/` (DataTable, Badge, Input, Select, PageHeader, LoadingSpinner, EmptyState, Button, Textarea, ConfirmDialog)

**Storage**: N/A (frontend only — report data fetched live from the backend; backend has its own in-memory report cache keyed by user + filters)

**Testing**: Backend reports already tested (24 tests in `tests/test_reports.py`). Frontend E2E (Playwright) for reports deferred to Phase 8 per the parent spec; the 6 pages are validated manually via the quickstart scenarios below and via `npm run build` + `npm run lint`.

**Target Platform**: Browser (Chrome, Firefox, Edge, Safari — last 2 versions)

**Project Type**: SPA / Web Application (React)

**Performance Goals**: Pages render filtered results in < 1s on normal connection; no unnecessary re-fetch when filters unchanged (react-query caching).

**Constraints**: 30-min JWT expiry (existing); backend report cache bypassed only via `?refresh=true`; CSV returned as a blob download (no server file storage).

**Scale/Scope**: 6 report pages, 6 backend endpoints consumed as-is, ~15 new/updated frontend files.

**Unknowns (all resolved in research.md)**:
- Report endpoints use two response shapes: paginated envelope (`{data,total,page,page_size,generated_at}`) for route-delivery, token-utilization, collection-efficiency; and direct report objects for revenue, consumption, dashboard.
- The envelope responses do NOT include the summary objects defined in the backend schemas (`RouteDeliveryReport.summary`, `TokenUtilizationReport` overall fields, `CollectionEfficiencyReport` overall fields) — summary/totals must be computed client-side from `data`.
- Backend accepts `preset` in {today, yesterday, this_week, last_week, this_month, last_month, this_year} OR `from_date`/`to_date`; default period is current month.
- CSV export requires `responseType: "blob"` on the axios call (the shared client defaults to JSON) and an in-page anchor-triggered download.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Frontend-only — follows the established `types → api → hooks → pages` layering matching Phases 1–6; backend routers/services/schemas consumed unchanged (no backend edits).
- [x] **RBAC**: Each new route wrapped in `RoleGuard` matching the backend endpoint role (dashboard + route-delivery: all authenticated roles with DELIVERY_PARTNER route restriction; revenue: OWNER; consumption: OWNER/ADMIN/CHECKER; token-utilization + collection-efficiency: OWNER/ADMIN). Navigation already reflects this in `src/config/permissions.ts`.
- [x] **Schema-Driven Contracts**: `types/reports.ts` interfaces mirror the backend report response schemas exactly (OperationalDashboard, RouteDeliveryItem, RevenueBreakdown/RevenueReport, ConsumptionDay/Trend/Report, TokenUtilizationItem/Report, CustomerCollectionItem/CollectionEfficiencyReport).
- [x] **Soft Deletes**: N/A at UI layer — reports are read-only aggregations over existing data; no delete paths exist.
- [x] **Tech Stack**: Uses the established frontend stack only; no new backend dependencies.
- [x] **Testing**: No backend changes → no new pytest required; backend report endpoints already covered (24 tests). Frontend build (`tsc -b && vite build`) and lint (`oxlint`) must pass; manual validation via quickstart V11–V16.
- [x] **Security**: All calls go through the existing authed Axios client (Bearer token, 401 → login redirect); no new secrets; report data is business data already role-restricted server-side.
- [x] **Migrations**: No schema changes → no Alembic migration.

## Project Structure

### Documentation (this feature)

```text
specs/009-reports-pages/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── reports-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/src/
├── types/
│   └── reports.ts                # NEW — TS interfaces mirroring app/schemas/reports.py
├── api/
│   └── reports.ts                # NEW — 6 report fetchers + CSV blob download helper
├── hooks/
│   └── useReports.ts             # NEW — TanStack Query hooks per report + refresh param
├── lib/
│   ├── constants.ts              # EDIT — add REPORT_PRESETS
│   └── utils.ts                  # EDIT — add formatQuantity/percent helpers if needed
├── pages/
│   ├── DashboardPage.tsx         # EDIT — replaced by redirect to /reports/dashboard (T136)
│   └── reports/
│       ├── DashboardPage.tsx     # NEW — KPI cards grid (today's operational dashboard)
│       ├── RouteDeliveryReportPage.tsx   # NEW — date range + route selector + metrics table
│       ├── RevenueReportPage.tsx         # NEW — date range + route/milk-type filters + breakdown
│       ├── ConsumptionReportPage.tsx     # NEW — customer selector + trend badge
│       ├── TokenUtilizationPage.tsx      # NEW — utilization bars + low threshold filter
│       └── CollectionEfficiencyPage.tsx  # NEW — aging buckets, color-coded
├── components/
│   ├── ui/
│   │   └── KpiCard.tsx           # NEW — small card primitive for the dashboard grid
│   └── reports/                  # NEW — optional shared bits (PresetFilter, TrendBadge, UtilizationBar, AgingBuckets)
└── App.tsx                       # EDIT — register 6 routes with RoleGuards; "/" → Navigate to /reports/dashboard
```

**Structure Decision**: Option 2 (Web application). All changes live under `frontend/src/` following the exact file conventions already used by the payments phase (types → api → hooks → pages). No backend files change.

## Complexity Tracking

No constitution violations to justify. This is a read-only frontend phase consuming an existing, fully-tested backend; no new layers, dependencies, or migrations are introduced.

### Re-Check (post-design, 2026-08-02)

- [x] **Layered Architecture**: New files only in the established frontend layers; backend untouched.
- [x] **RBAC**: RoleGuards per route match backend `require_role`/`get_current_user` scope; DELIVERY_PARTNER sees only their own route via the backend's `get_role_restricted_routes` logic (client shows whatever the API returns).
- [x] **Schema-Driven Contracts**: Interfaces in `types/reports.ts` mirror `app/schemas/reports.py`; envelope `data` arrays are typed to the item schemas and summary totals are computed client-side.
- [x] **Soft Deletes**: N/A (read-only reports).
- [x] **Testing**: Build + lint gates; quickstart V11–V16 manual validation; E2E deferred to Phase 8.
- [x] **Security**: No new security surface; all requests via existing authed client.
- [x] **Migrations**: None.
