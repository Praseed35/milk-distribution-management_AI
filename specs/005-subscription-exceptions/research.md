# Research: Subscription & Exceptions Pages

> Phase 0 output for `specs/005-subscription-exceptions`. Consolidates decisions on the unknowns and technology choices for this feature. Derived from verification against the live backend (2026-07-31) and the parent feature `004-react-frontend` plan artifacts.

## Technology Decisions

### Reuse established frontend stack
- **Decision**: No new libraries. Use the existing React 19 / Vite 8 / TypeScript 6 / Tailwind 4 / TanStack Query v5 / axios / react-hot-toast stack already installed in `frontend/package.json`.
- **Rationale**: Phases 1–2 of the parent feature established working patterns (types → api → hooks → pages) with these libraries. Introducing anything new would violate the constitution's tech-stack gate.
- **Alternatives considered**: A component library (shadcn/Radix) — rejected; parent spec resolved pure Tailwind primitives.

### Response handling — plain array lists
- **Decision**: `GET /subscriptions/` and `GET /delivery-exceptions/` are typed as direct arrays (`SubscriptionListResponse[]`, `DeliveryExceptionListResponse[]`) in the API modules and rendered in full by the existing DataTable.
- **Rationale**: Verified `response_model=list[...]` in `app/routers/subscriptions.py` and `app/routers/delivery_exceptions.py`. There is no `total`/`page`/`page_size` envelope, so no pagination wiring.
- **Alternatives considered**: Treating lists as `PaginatedResponse` — rejected (fields do not exist); client-side pagination — rejected (expected volume < 2,000, spec EC-10 allows plain lists).

### Subscription create/update field sets
- **Decision**: `SubscriptionCreate` sends `customer_id`, `milk_type_id`, `morning_quantity`, `evening_quantity`, `status` (optional, defaults ACTIVE), `remarks` (optional). `SubscriptionUpdate` sends `morning_quantity`, `evening_quantity`, `status`, `remarks` only. **`start_date`/`end_date` are never sent** — the backend assigns them (response-only).
- **Rationale**: Verified against `app/schemas/subscription.py`. `morning_quantity`/`evening_quantity` accept 0 with `ge=0`.
- **Alternatives considered**: Sending `start_date`/`end_date` on create — rejected; would produce 422 (unknown fields).

### List vs Detail DTO split
- **Decision**: Two interface shapes per module. List shape = flat joined fields (`customer_code`, `customer_name`, `route_name`, `milk_type_name`, `milk_type_volume` for subscriptions; `customer_id`, `customer_code`, `customer_name`, `route_name` for exceptions). Detail shape = nested objects (`customer: CustomerSummaryResponse`, `milk_type: MilkTypeSummaryResponse`; `subscription: SubscriptionSummaryResponse`).
- **Rationale**: The backend defines distinct `*ListResponse` and `*DetailResponse` schemas. The table renders the list DTO; the edit form hydrates from the detail endpoint.
- **Alternatives considered**: One unified interface with all-optional fields — rejected (loses type safety, contradicts Schema-Driven Contracts).

### Exception fields
- **Decision**: `DeliveryExceptionCreate` sends `subscription_id`, `exception_type` (VACATION | NO_MILK | HOLIDAY), `shift` (optional — MORNING | EVENING, `null`/omitted = whole day), `start_date` (required), `end_date` (optional), `reason` (optional). `DeliveryExceptionUpdate` also allows `status` and supports clearing `shift` back to whole day.
- **Rationale**: Verified against `app/schemas/delivery_exception.py`. The `EXCEPTION_TYPES` constant already exists in `frontend/src/lib/constants.ts`. `shift` was added end-to-end (Alembic migration `a1b2c3d4e5f6` + model/schema/service + frontend) so exceptions can be scoped to one delivery shift; overlap logic is shift-aware (whole-day conflicts with all, same-shift conflicts with same/whole-day). Shift is validated server-side against the `Shift` enum.
- **Alternatives considered**: Requiring `end_date` — rejected (backend defaults to None). Free-form `shift` string — rejected in favor of `Shift` enum validation.

### Filtering strategy
- **Decision**: Customer filter on subscriptions uses the dedicated `GET /subscriptions/customer/{id}` endpoint; subscription filter on exceptions uses `GET /delivery-exceptions/subscription/{id}`. Route-level filters (and cross-customer search) run client-side over the returned array using the flat `route_name`/`customer_name` fields.
- **Rationale**: The backend exposes only these two filtered endpoints; list endpoints accept no query params. Documented as a known backend gap (parent spec risk table).
- **Alternatives considered**: Adding backend query params — out of scope (no backend changes this phase).

### CHECKER read-only (RBAC)
- **Decision**: List routes registered for OWNER/ADMIN/CHECKER; create/edit routes wrapped in `RoleGuard` with `roles=["OWNER","ADMIN"]`. Action buttons and edit/delete links conditionally rendered only when `user.role !== "CHECKER"`.
- **Rationale**: Parent spec BR-2 / FR-4.2: CHECKER views master/operational data read-only. Server enforces authorization regardless; the UI guards are UX.
- **Alternatives considered**: Only hiding buttons without route guards — rejected (spec T082 requires blocked access to create/edit screens).

## Edge Cases from Spec

| Edge Case | Approach |
|-----------|----------|
| Overlapping exception date range | Backend 400; surface as error toast; form remains open so the user can correct |
| Exception start after end date | Client-side inline validation on the form; backend also rejects |
| Exception on inactive subscription | Backend 400; toast + form error; prevent submission from a stale selector |
| Empty lists | Existing `EmptyState` component ("No records found") with Create button when permitted |
| Deactivated records | INACTIVE badge via existing `Badge`/`getStatusColor`; soft-delete only |
| CHECKER reaches create/edit URL directly | `RoleGuard` renders `ForbiddenPage` (403) |
| Negative/empty quantities | Inline validation (>= 0) in the form |
| Backend unavailable | TanStack Query retries (default 3), then error toast per parent spec NFR-3 |
