# Research: Payment Management Pages

**Date**: 2026-08-01
**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

All technical unknowns were resolved against the existing, fully-tested Sprint 6 backend and the established frontend conventions (Phases 1–5). No `[NEEDS CLARIFICATION]` markers remain in the spec. Decisions below are recorded as `Decision / Rationale / Alternatives considered`.

## 1. Backend contract — consume as-is

- **Decision**: Consume the existing `/api/v1/payments/*` router (14 endpoints) unchanged. Frontend mirrors the Pydantic schemas exactly.
- **Rationale**: Sprint 6 backend is complete and tested (5 test files, 14 endpoints); the phase is defined as frontend-only. Changing it would violate the phase boundary and risk regressions.
- **Alternatives considered**: Extending the backend (e.g., multi-customer bill batch endpoint, all-customers outstanding endpoint) — rejected to keep the phase frontend-only; the page compensates by looping (one request per customer).

## 2. Payment date is server-assigned

- **Decision**: The payment form does not capture a date. `payment_date` is `server_default=func.now()` on the model and absent from `CustomerPaymentCreate`. Date filters in the history page apply to the server-assigned date.
- **Rationale**: The backend schema has no date input; adding one would require a backend change.
- **Alternatives considered**: Adding `payment_date` to the create schema — rejected (backend change, out of scope).

## 3. Payment history immutability

- **Decision**: No edit/delete controls for recorded payments, even though the backend exposes `PUT /payments/{id}` and `DELETE /payments/{id}`.
- **Rationale**: Documented business rule — "Payment history is immutable" (`.ai/12_business_workflows.md`, `BUSINESS_RULES.md` §18). Immutability is a domain rule, not a capability gap.
- **Alternatives considered**: Exposing edit/delete to allow corrections — rejected on domain-rule grounds; a future Owner-only correction flow (like delivery reopen) would be a separate feature.

## 4. Bill generation is one customer per request

- **Decision**: `BillGeneratePage` lets the user multi-select customers; the page issues one `POST /payments/bills/generate` per selected customer and aggregates results.
- **Rationale**: `BillGenerateRequest` is single-customer; there is no batch endpoint. With ~15 active customers the loop cost is negligible.
- **Alternatives considered**: Adding a batch backend endpoint — rejected (out of scope).

## 5. Outstanding view iterates per-customer endpoint

- **Decision**: `OutstandingPage` fetches `GET /payments/outstanding/{customer_id}` for the active customers (reusing `useCustomers`) and renders a table; also supports narrowing to a single customer.
- **Rationale**: The outstanding endpoint is per-customer only; dataset is small.
- **Alternatives considered**: New aggregate endpoint — rejected (out of scope).

## 6. Bill status management is a page-level addition beyond T131

- **Decision**: Add `BillDetailPage` (not in the original T123–T131 list) to satisfy spec FR-014/015/016: show line items, applied payments, and update status (PENDING/PARTIAL/PAID/OVERDUE/CANCELLED) via `PUT /payments/bills/{bill_id}/status`, with a confirmation and a specific warning when cancelling a bill that has applied payments.
- **Rationale**: The backend endpoint exists and the spec's User Story 5 requires it; omitting it would leave FR-014–016 unimplemented.
- **Alternatives considered**: Restricting to only the T123–T131 surface and dropping status management — rejected (spec requires it).

## 7. Overpayment / duplicate-bill guards

- **Decision**: The form surfaces the selected bill's remaining balance while recording; amounts that fully pay (or exceed) the balance are allowed and the bill becomes PAID (balance never shown negative). The generate page warns before re-generating a period that already has a bill for the same customer (backend does not dedupe).
- **Rationale**: Backend permits both; guards are advisory UI behavior, not new backend rules.
- **Alternatives considered**: Blocking overpayment client-side — rejected (backend allows partial->overpay transitions; a hard block could reject legitimate full settlements after floating-point rounding).

## 8. E2E data dependency

- **Decision**: `payments.spec.ts` first creates a delivery session (via the existing Delivery pages) and marks deliveries DELIVERED, because the seed contains no sessions/deliveries/bills/payments. Bills require DELIVERED/CASH_SALE deliveries in the period.
- **Rationale**: Bill generation has no data to aggregate otherwise; reuse of the Phase 5 E2E flow (already proven) is the cheapest reliable setup.
- **Alternatives considered**: Extending `scripts/seed.py` to seed sessions/deliveries — rejected (seed is idempotent master-data only; delivery state is workflow-generated).

## 9. Known pre-existing backend RBAC gap

- **Decision**: Frontend restricts access via `RoleGuard` and navigation (OWNER/ADMIN only). The backend `/payments/*` router (like most routers) currently has **no** `get_current_user` dependency — only `reports.py` and `auth.py` do. This is tracked separately, out of scope here.
- **Rationale**: Fixing backend-wide RBAC is a cross-cutting security item that spans all domains and all prior sprints; it must not be smuggled into a frontend-only phase.
- **Alternatives considered**: Fixing RBAC as part of this phase — rejected (scope/risk; affects every router, needs its own plan, tests, and migration of the E2E suite which currently relies on unauthenticated calls).
