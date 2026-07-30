# Implementation Plan: React Frontend for Milk Distribution ERP

**Branch**: `004-react-frontend` | **Date**: 2026-07-31 | **Spec**: `specs/004-react-frontend/spec.md`

**Implementation Status**: ✅ Phase 1 (Setup + Auth + Layout) complete | ✅ Phase 2 (Master Data CRUD) complete | ⏳ Phase 3 (Subscription & Exceptions) — next

**Input**: Feature specification from `/specs/004-react-frontend/spec.md`

## Summary

Add a modern React SPA frontend to the existing FastAPI ERP backend. The frontend provides a complete GUI for all business modules with JWT authentication, role-based access, responsive layout, and dashboard-driven design. Backend changes include CORS middleware and API prefix migration to `/api/v1`. Implementation is phased across 8 phases starting with backend prep + auth scaffold.

## Technical Context

**Language/Version**: TypeScript 5.x, React 18.x

**Primary Dependencies**: Vite 5, React Router v6, Axios, TanStack Query (React Query v5), Tailwind CSS 3, react-hot-toast

**Storage**: N/A (frontend only — all data via API calls to backend)

**Testing**: Vitest + React Testing Library for component/unit tests (deferred to Phase 8)

**Target Platform**: Browser (Chrome, Firefox, Edge, Safari — last 2 versions)

**Project Type**: SPA / Web Application (single-page React app)

**Performance Goals**: Initial bundle < 300KB gzipped, page transitions < 1s

**Constraints**: 30-min JWT token expiry (no refresh token), no offline support, no PWA

**Scale/Scope**: ~80 API endpoints across 14 backend modules, ~30 page routes, role-based routing for 5 roles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: N/A (frontend is a new project type; follows component/page/hook/api layers instead of backend's router/service/model)
- [x] **RBAC**: Enforced via ProtectedRoute + RoleGuard components mapping to role-permission config
- [x] **Schema-Driven Contracts**: TypeScript interfaces in `src/types/` mirror backend Pydantic schemas exactly
- [x] **Soft Deletes**: N/A at UI layer — backend handles soft delete; frontend shows active/inactive toggle
- [x] **Tech Stack**: Frontend uses React + Vite + TS (standard stack for FastAPI SPA); backend additions use existing FastAPI stack
- [x] **Testing**: Phase 8 includes Vitest + RTL; backend changes tested via existing pytest suite
- [x] **Security**: JWT in localStorage (documented tradeoff), Axios interceptor for Authorization header, 401 redirect
- [x] **Migrations**: No new DB schema changes — backend changes are CORS + prefix only, no Alembic needed

## Project Structure

### Documentation (this feature)

```text
specs/004-react-frontend/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
app/
├── main.py              # Modified: CORS + /api/v1 umbrella router + health
├── routers/
│   ├── __init__.py
│   ├── auth.py          # Unchanged (routes moved under /api/v1)
│   └── ...              # All existing routers unchanged
└── ...                  # No model/schema/service changes

frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── routes.ts
│   │   ├── customers.ts
│   │   ├── milk-types.ts
│   │   ├── employees.ts
│   │   ├── subscriptions.ts
│   │   ├── delivery-exceptions.ts
│   │   ├── token-books.ts
│   │   ├── delivery-sessions.ts
│   │   ├── deliveries.ts
│   │   ├── payments.ts
│   │   └── reports.ts
│   ├── components/
│   │   ├── ui/          # DataTable, Button, Input, Select, Badge, ConfirmDialog, PageHeader, LoadingSpinner, EmptyState
│   │   ├── layout/      # AppLayout, Sidebar, Header
│   │   ├── guards/      # ProtectedRoute, RoleGuard
│   │   └── forms/       # Module-specific form components
│   ├── hooks/            # Per-module TanStack Query hooks
│   ├── pages/            # Route-level page components organized by module
│   ├── providers/        # AuthProvider, QueryProvider
│   ├── types/            # TypeScript interfaces mirroring backend schemas
│   ├── config/           # permissions.ts
│   ├── lib/              # utils.ts, constants.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── tailwind.config.js
├── postcss.config.js
└── .gitignore
```

**Structure Decision**: Option 2 (Web application with `app/` backend and new `frontend/`). Backend stays at root-level `app/` unchanged except `main.py`. All new frontend code goes into `frontend/`.

## Complexity Tracking

No constitution violations to justify. The frontend is a new project type not covered by the constitution's backend-specific rules, and all backend additions (CORS, prefix) are simple and constitutional.
