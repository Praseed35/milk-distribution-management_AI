# Implementation Plan: Payment Management Pages

**Branch**: `008-payment-management-pages` | **Date**: 2026-08-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-payment-management-pages/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Frontend-only Phase 6: build the Payment Management pages that consume the already-complete, tested Sprint 6 backend (`app/routers/payments.py` + `app/services/payment_service.py`, 14 endpoints, 5 test files). Deliver five page surfaces under the existing **Finance** navigation for OWNER/ADMIN:

1. **Payments** list (history + filters) and **Payment Form** (record ADVANCE or BILL_PAYMENT).
2. **Bills** list (filters), **Bill Generate** (multi-customer + date range), and **Bill Detail** (line items + applied payments + status management).
3. **Outstanding** balances view.

Implementation follows the established `types → api → hooks → pages` layering, reuses the existing UI kit (`DataTable`, `Badge`, `Select`, `Input`, `Button`, `ConfirmDialog`, `PageHeader`, `LoadingSpinner`, `EmptyState`), and adds Playwright E2E coverage (`payments.spec.ts`) consistent with the green Phase 1–5 suite. No backend changes; no schema/migration changes.

## Technical Context

**Language/Version**: TypeScript, React 18, Vite (existing `frontend/` app). No backend code changes.

**Primary Dependencies**: Existing stack only — `react-router-dom`, `@tanstack/react-query`, `axios` (`frontend/src/api/client.ts`, baseURL `/api/v1`), `react-hot-toast`, Tailwind CSS, and the shared UI kit (`frontend/src/components/ui/*`, `frontend/src/lib/{constants,utils}.ts`). No new libraries.

**Storage**: N/A on the frontend — consumes the existing PostgreSQL-backed API (`/api/v1/payments/...`). No migrations.

**Testing**: Playwright E2E (`frontend/playwright.config.ts`, isolated `milk_management_e2e` DB reseeded per run) + `npx tsc -b` + `oxlint`. No new pytest (no backend endpoints added).

**Target Platform**: Browser (Vite dev server, port 5174 in E2E; 5173 for manual dev).

**Project Type**: Web application (React SPA).

**Performance Goals**: Standard interactive latency; lists render immediately after the existing queries resolve. No pagination (backend returns full active lists; ~15 seeded customers).

**Constraints**: Reuse established patterns verbatim (page structure, hook/mutation + toast conventions, `noValidate` forms, `RoleGuard`); do not introduce new dependencies; payment history is immutable (no edit/delete UI for payments).

**Scale/Scope**: 5 page surfaces, ~7 new frontend files + 1 E2E spec; small dataset (15 customers).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Frontend code placed in the correct layer (`types` → `api` → `hooks` → `pages`); zero backend changes (no routers/services/models/schemas touched).
- [x] **RBAC**: All five payment routes wrapped in `RoleGuard roles={["OWNER", "ADMIN"]}` in `App.tsx`; Finance nav already restricted to OWNER/ADMIN in `permissions.ts`. *Known pre-existing backend gap (out of scope): `/payments/*` router lacks an auth dependency — see Assumptions in spec.md; client guards are the sole enforcement this phase.*
- [x] **Schema-Driven Contracts**: TypeScript interfaces in `types/payment.ts` mirror the existing Pydantic schemas exactly (`CustomerPaymentCreate/Response/ListResponse`, `BillGenerateRequest`, `CustomerBillResponse/ListResponse`, `CustomerBillItemResponse`, `OutstandingBalanceResponse`).
- [x] **Soft Deletes**: No new entities; backend soft-deletes and filters `is_active`; frontend only renders what the API returns.
- [x] **Tech Stack**: Existing stack only — no new libraries.
- [x] **Testing**: Playwright E2E `payments.spec.ts` covers record-advance, record-bill-payment + bill status update, generate bill, outstanding, and role denial (CHECKER blocked). Backend already has 5 test files for this domain.
- [x] **Security**: No new credentials/secrets; no new auth surface. Backend RBAC gap is documented and tracked separately.
- [x] **Migrations**: None required (no schema changes).

## Project Structure

### Documentation (this feature)

```text
specs/008-payment-management-pages/
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
│   └── payment.ts                    # T123 — CustomerPayment, CustomerBill, BillItem, Outstanding interfaces
├── api/
│   └── payments.ts                   # T124 — list/create payment, generate/list/get bill, update bill status, get outstanding
├── hooks/
│   └── usePayments.ts                # T125 — useQuery/useMutation hooks + toast + invalidation
├── pages/
│   └── payments/
│       ├── PaymentListPage.tsx       # T126 — history table + filters (customer/mode/type/date)
│       ├── PaymentFormPage.tsx       # T127 — ADVANCE | BILL_PAYMENT form
│       ├── BillListPage.tsx          # T128 — bills table + filters (customer/status/date)
│       ├── BillGeneratePage.tsx      # T129 — multi-customer + date range generation
│       ├── BillDetailPage.tsx        # NEW (spec FR-014/015/016) — line items + applied payments + status update w/ confirm
│       └── OutstandingPage.tsx       # T130 — per-customer billed/paid/balance/last dates
├── lib/
│   └── constants.ts                  # add BILL_STATUS + PAYMENT_TYPES maps (PAYMENT_MODES already exists)
└── App.tsx                           # T131 — register 6 routes with RoleGuard OWNER/ADMIN

frontend/e2e/
└── payments.spec.ts                  # NEW — E2E coverage (uses delivery pages to create sessions w/ DELIVERED deliveries first)
```

**Structure Decision**: Single existing React app under `frontend/`; this phase only adds files inside the established `types`/`api`/`hooks`/`pages` layers plus one E2E spec. No new top-level directories.

## Complexity Tracking

> No Constitution Check violations to justify — this section intentionally empty.
