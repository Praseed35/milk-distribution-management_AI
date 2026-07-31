# Implementation Plan: Subscription & Exceptions Pages

**Branch**: `005-subscription-exceptions` | **Date**: 2026-07-31 | **Spec**: `specs/005-subscription-exceptions/spec.md`

**Input**: Feature specification from `/specs/005-subscription-exceptions/spec.md`

**Implementation Status**: 📐 Planned — ready for `/speckit.tasks` (parent feature tasks T070–T083)

## Summary

Add the Subscriptions and Delivery Exceptions pages to the existing React SPA frontend (`frontend/`). OWNER and ADMIN manage subscriptions (customer + milk type + morning/evening quantities) and delivery exceptions (vacation/no-milk/holiday over a date range); CHECKER gets read-only access with actions hidden and create/edit screens blocked by role guard. Backend endpoints already exist — this phase is frontend-only, scoped to Phase 3 of the parent feature `004-react-frontend` (US-020, US-021, US-022).

## Technical Context

**Language/Version**: TypeScript 6.x, React 19.x (verified from `frontend/package.json`)

**Primary Dependencies**: Vite 8, React Router v7 (v6-style `Routes`/`Route` API), Axios, TanStack Query v5, Tailwind CSS 4 (`@tailwindcss/vite`), react-hot-toast, @sentry/react, oxlint — all already installed

**Storage**: N/A (frontend only — data via the existing `/api/v1` backend)

**Testing**: No test tasks — frontend testing deferred to Phase 8 of the parent feature (Vitest + RTL). Verification is manual via `npm run build` + `npm run dev` + quickstart scenarios.

**Target Platform**: Browser (Chrome, Firefox, Edge, Safari — last 2 versions)

**Project Type**: SPA / Web Application (single-page React app) — feature extends the existing `frontend/` project

**Performance Goals**: Page load < 1s on standard office connection; list pages render without pagination (lists return full arrays — backend returns plain arrays, expected volume < 2,000 subscriptions)

**Constraints**: No backend changes (endpoints exist); no pagination envelope on list endpoints (client renders full array); route/customer filters done client-side; 30-min JWT expiry handled by existing Axios interceptor

**Scale/Scope**: 2 new types files, 2 new api modules, 2 new hooks modules, 4 new page components, 6 new routes registered, role-guard wiring for CHECKER read-only. No backend files touched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Frontend follows the established project layering (types → api → hooks → pages) matching Phases 1–2 of the parent feature. No backend/routers/services changes.
- [x] **RBAC**: List routes allow OWNER/ADMIN/CHECKER; create/edit routes wrapped in `RoleGuard` restricted to OWNER/ADMIN; actions hidden via `useAuth()` role check. Backend enforces authorization independently.
- [x] **Schema-Driven Contracts**: TypeScript interfaces in `src/types/subscription.ts` and `src/types/delivery-exception.ts` mirror `app/schemas/subscription.py` and `app/schemas/delivery_exception.py` exactly (flat list DTOs vs nested detail DTOs).
- [x] **Soft Deletes**: Deactivate actions call backend soft-delete endpoints; inactive records shown with INACTIVE badge.
- [x] **Tech Stack**: Uses the established frontend stack already installed in `frontend/package.json` (React 19, Vite 8, Tailwind 4, TanStack Query v5, axios). No new libraries.
- [x] **Testing**: No new backend endpoints, so no new pytest coverage required. Frontend tests deferred to parent Phase 8 per parent spec. Build must pass (`npm run build`).
- [x] **Security**: No new security surface; all calls go through the existing authed Axios client with 401 interceptor. No secrets involved.
- [x] **Migrations**: No database schema changes — no Alembic needed.

## Project Structure

### Documentation (this feature)

```text
specs/005-subscription-exceptions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
frontend/src/
├── types/
│   ├── subscription.ts          # NEW — SubscriptionCreate/Update/List/Detail interfaces
│   └── delivery-exception.ts    # NEW — ExceptionType, DeliveryException* interfaces
├── api/
│   ├── subscriptions.ts         # NEW — CRUD + customer-filter functions
│   └── delivery-exceptions.ts   # NEW — CRUD + subscription-filter functions
├── hooks/
│   ├── useSubscriptions.ts      # NEW — useSubscriptions/useSubscription/useCreate/useUpdate/useDelete
│   └── useDeliveryExceptions.ts # NEW — same pattern for exceptions
├── pages/
│   ├── subscriptions/
│   │   ├── SubscriptionListPage.tsx    # NEW — list + customer filter + role-aware actions
│   │   └── SubscriptionFormPage.tsx    # NEW — create/edit, customer + milk-type dropdowns
│   └── delivery-exceptions/
│       ├── ExceptionListPage.tsx       # NEW — list + subscription filter + role-aware actions
│       └── ExceptionFormPage.tsx       # NEW — create/edit, subscription selector + type + dates
├── components/
│   └── guards/
│       └── RoleGuard.tsx               # EXISTING — reused for OWNER/ADMIN form routes
├── config/
│   └── permissions.ts                  # EXISTING — subscriptions/exceptions nav already present
├── lib/
│   └── constants.ts                    # EXISTING — EXCEPTION_TYPES already present
└── App.tsx                             # MODIFIED — register 6 new routes with guards
```

**Structure Decision**: Option 2 (web application) — all changes are additive inside the existing `frontend/src/` structure. Backend `app/` untouched. Reuses existing UI primitives (DataTable, Badge, Select, Input, Button, ConfirmDialog, PageHeader, LoadingSpinner, EmptyState) and existing guards.

## Complexity Tracking

No constitution violations to justify. The feature is a standard CRUD-page addition that follows the exact patterns established in Phases 1–2 of the parent feature. No new architecture, libraries, or backend changes.

## Phase 3 Design Notes (post-design re-check)

- List endpoints return **plain arrays** (verified: `app/routers/subscriptions.py` → `list[SubscriptionListResponse]`, `app/routers/delivery_exceptions.py` → `list[DeliveryExceptionListResponse]`). API modules type these directly as arrays; DataTable renders full array with client-side sorting.
- `SubscriptionCreate` accepts `status` (default "ACTIVE"); `start_date`/`end_date` are **response-only** — the form must not send them.
- Edit form uses `GET /subscriptions/{id}` (`SubscriptionDetailResponse`, nested customer/milk_type) and `GET /delivery-exceptions/{id}` (`DeliveryExceptionDetailResponse`, nested subscription).
- Filters: subscriptions by customer via `GET /subscriptions/customer/{id}`; exceptions by subscription via `GET /delivery-exceptions/subscription/{id}`; route-level filters done client-side (known backend gap).
- CHECKER read-only (T082/T083): list routes allowed for CHECKER; create/edit routes wrapped in `RoleGuard roles={["OWNER","ADMIN"]}`; action buttons/links hidden when `user.role === "CHECKER"`.
