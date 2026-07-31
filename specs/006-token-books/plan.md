# Implementation Plan: Token Book Pages

**Branch**: `006-token-books` | **Date**: 2026-07-31 | **Spec**: `specs/006-token-books/spec.md`

**Input**: Feature specification from `/specs/006-token-books/spec.md`

## Summary

Add token book management pages to the existing React SPA frontend: token identities (customer + milk type + token number), token book issues (physical book tracking with issue numbers and current sheet), and token book payments (prepaid/postpaid with balance tracking). All three modules are read-only for CHECKER. The backend already exposes the complete `/token-books/` API (identities, issues, payments) — this phase adds **frontend only**: types, API modules, hooks, six pages, and route/nav/constant registration. No backend or database changes.

## Technical Context

**Language/Version**: TypeScript 6.x, React 19.x (verified from `frontend/package.json`)

**Primary Dependencies**: Vite 8, React Router v7 (v6-style `Routes`/`Route` API), Axios, TanStack Query v5, Tailwind CSS 4, react-hot-toast — all already installed; **no new dependencies**

**Storage**: N/A (frontend only — all data via existing `/api/v1/token-books/*` endpoints)

**Testing**: `npm run build` must pass (TypeScript). Vitest + RTL deferred to parent Phase 8. No backend changes → no pytest additions.

**Target Platform**: Browser (Chrome, Firefox, Edge, Safari — last 2 versions)

**Project Type**: SPA / Web Application (React single-page app)

**Performance Goals**: Page transitions < 1s; three token lists render within 1 second on a standard office connection

**Constraints**: 30-min JWT expiry (existing flow), no offline support, no PWA

**Scale/Scope**: 3 new type modules, 1 API module, 1 hooks module, 6 page files, plus registration in `App.tsx`, `config/permissions.ts`, and `lib/constants.ts`

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design — all green.*

- [x] **Layered Architecture**: N/A at backend (no backend changes). Frontend follows established layers: `types/` (contracts), `api/` (data access), `hooks/` (query/mutation), `pages/` (presentation).
- [x] **RBAC**: Create/edit routes wrapped in `RoleGuard roles=["OWNER","ADMIN"]`; list routes open to OWNER/ADMIN/CHECKER with action buttons hidden for CHECKER; DELIVERY_PARTNER has no nav/routes. Nav roles updated so CHECKER sees all three token lists read-only.
- [x] **Schema-Driven Contracts**: TypeScript interfaces in `src/types/token-identity.ts` and `src/types/token-book.ts` mirror backend Pydantic schemas exactly (Create/Update/Response/List/Detail), excluding sensitive fields (none present).
- [x] **Soft Deletes**: N/A at UI layer — backend handles soft delete; the deactivate buttons call DELETE which sets `is_active=false`.
- [x] **Tech Stack**: Existing React/Vite/TS stack only; no new libraries.
- [x] **Testing**: `npm run build` gate; backend suite (352 tests) unaffected. Vitest deferred per parent plan.
- [x] **Security**: Existing JWT flow reused; no new secrets or credentials.
- [x] **Migrations**: No schema changes → no Alembic.

## Project Structure

### Documentation (this feature)

```text
specs/006-token-books/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/src/
├── types/
│   ├── token-identity.ts     # NEW — identity Create/Update/Response/List/Detail/Summary interfaces
│   └── token-book.ts         # NEW — issue + payment Create/Update/Response/List/Detail interfaces
├── api/
│   └── token-books.ts        # NEW — identity CRUD + issue CRUD + payment CRUD API functions
├── hooks/
│   └── useTokenBooks.ts      # NEW — useTokenIdentities/useTokenIdentity/useCreateIdentity/useUpdateIdentity/
│                             #        useDeleteIdentity + issue + payment hooks (React Query v5)
├── pages/
│   └── token-books/          # NEW — 6 files (dir exists, empty)
│       ├── TokenIdentityListPage.tsx
│       ├── TokenIdentityFormPage.tsx
│       ├── TokenBookIssueListPage.tsx
│       ├── TokenBookIssueFormPage.tsx
│       ├── TokenBookPaymentListPage.tsx
│       └── TokenBookPaymentFormPage.tsx
├── config/
│   └── permissions.ts        # EDIT — add CHECKER to Token Identities + Token Book Issues nav roles
├── lib/
│   └── constants.ts          # EDIT — add BOOK_ISSUE_STATUS (WAITING/ACTIVE/COMPLETED) into STATUS_BADGE_MAP
└── App.tsx                   # EDIT — register 6 routes (/token-identities, /token-book-issues, /token-book-payments + /new + /:id/edit)
```

**Structure Decision**: Single-project SPA following the exact pattern established in Phases 1–3 of the parent feature. New files mirror `types/subscription.ts` → `api/subscriptions.ts` → `hooks/useSubscriptions.ts` → `pages/subscriptions/*`. The empty `pages/token-books/` scaffold already exists and is populated. `Header.tsx` page titles already include the three routes (no change).

## Complexity Tracking

None — the Constitution Check passes with no violations. This phase is a direct, low-risk extension of the established three-layer (types → api/hooks → pages) pattern with no new infrastructure.
