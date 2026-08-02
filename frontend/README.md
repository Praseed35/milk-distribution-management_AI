# Milk Distribution ERP — Frontend

React SPA frontend for the Milk Distribution ERP.

## Tech Stack

- React 18 + TypeScript
- Vite 5 (dev server on :5173, proxies `/api` → `:8000`)
- Tailwind CSS v4
- React Router v7
- TanStack Query v5
- Axios
- react-hot-toast
- Sentry (optional, via `VITE_SENTRY_DSN`)

## Project Structure

```
src/
├── api/          # Axios API functions per module
├── components/
│   ├── ui/       # Reusable UI primitives (Button, Input, DataTable, etc.)
│   ├── reports/  # Report primitives (KpiCard, PresetFilter, TrendBadge, UtilizationBar, AgingBuckets)
│   ├── layout/   # AppLayout, Sidebar, Header
│   └── guards/   # ProtectedRoute, RoleGuard
├── hooks/        # TanStack Query hooks per module
├── pages/        # Page components grouped by module (incl. reports/)
├── providers/    # AuthProvider, QueryProvider
├── types/        # TypeScript interfaces mirroring backend schemas
├── config/       # permissions.ts
└── lib/          # utils.ts, constants.ts
```

## Implementation Status (Sprint 13)

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Setup, Auth, Layout | ✅ Complete |
| 2 | Master Data CRUD | ✅ Complete |
| 3 | Subscriptions & Exceptions | ✅ Complete |
| 4 | Token Books | ✅ Complete |
| 5 | Delivery Sessions | ✅ Complete |
| 6 | Payments | ✅ Complete |
| 7 | Reports (Dashboard, Route Delivery, Revenue, Consumption, Token Utilization, Collection Efficiency + CSV) | ✅ Complete |
| 8 | Polish & Testing | ⏳ Pending |

## Tests

Playwright E2E lives in `frontend/e2e/` (8 spec files, 45 tests). `npm run test:e2e` auto-starts an
isolated backend on :8001 (`scripts/e2e_backend.py`, database `milk_management_e2e` reset each run)
and a Vite server on :5174 that proxies `/api` → :8001. The report endpoints run with
`REPORT_CACHE_DISABLED=1` so E2E assertions read fresh data.

## Quick Start

```bash
npm install
npm run dev      # http://localhost:5173
```

Login: `owner` / `owner123` (backend must be running on :8000)
