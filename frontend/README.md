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
│   ├── layout/   # AppLayout, Sidebar, Header
│   └── guards/   # ProtectedRoute, RoleGuard
├── hooks/        # TanStack Query hooks per module
├── pages/        # Page components grouped by module
├── providers/    # AuthProvider, QueryProvider
├── types/        # TypeScript interfaces mirroring backend schemas
├── config/       # permissions.ts
└── lib/          # utils.ts, constants.ts
```

## Implementation Status (Sprint 9)

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Setup, Auth, Layout | ✅ Complete |
| 2 | Master Data CRUD | ✅ Complete |
| 3 | Subscriptions & Exceptions | ⏳ Pending |
| 4 | Token Books | ⏳ Pending |
| 5 | Delivery Sessions | ⏳ Pending |
| 6 | Payments | ⏳ Pending |
| 7 | Reports | ⏳ Pending |
| 8 | Testing | ⏳ Pending |

## Quick Start

```bash
npm install
npm run dev      # http://localhost:5173
```

Login: `owner` / `owner123` (backend must be running on :8000)
