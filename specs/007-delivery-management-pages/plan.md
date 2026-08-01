# Implementation Plan: Delivery Management Pages

**Branch**: `007-delivery-management-pages` | **Date**: 2026-07-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-delivery-management-pages/spec.md`

## Summary

Build the **Phase 5 React SPA pages** that let the Checker run the full daily delivery workflow — create a delivery session (route/date/shift/partner), record dispatch, register each customer's delivery status and token sheet (with warning acknowledgment), reconcile loaded vs token vs cash vs returned milk, and close the session only when balanced — plus an Owner-only reopen/edit flow with a required reason and an audit trail. The feature consumes the existing FastAPI delivery endpoints and adds **three small, justified backend fixes** (approved by the user during planning) to reach the parent 002 design, which is currently unreachable:

1. **Auto-generate the planned checklist on session create** — `generate_delivery_list()` (which already exists but is dead *and broken*: it references non-existent columns `Subscription.quantity` and `DeliveryException.exception_date`) is fixed (shift-aware quantities, correct exception window) and invoked from `create_session`.
2. **Add `POST /deliveries/sessions/{id}/complete`** — the parent state machine defines PLANNED→STARTED→COMPLETED→CLOSED, but no endpoint ever transitions STARTED→COMPLETED, so `close` (which requires COMPLETED) is unreachable. Quickstart 002 scenario 1 expects this to work.
3. **Server-side OWNER check** on `PUT /deliveries/{id}/edit` and `POST /deliveries/session/{id}/reopen` — the spec requires OWNER-only edit/reopen, but the backend currently accepts any authenticated user (constitution Principle II).

Frontend layout follows the established `types → api → hooks → pages` convention: two types modules, two API modules, two hook modules, three pages (list, create, all-in-one detail, plus an owner edit page), routes under `/delivery/sessions*`, and reuse of existing constants (SESSION_STATUS/DELIVERY_STATUS/RECONCILIATION_STATUS/SHIFTS already exist), badge colors, and UI primitives — no new component library.

## Technical Context

**Language/Version**: TypeScript 5.6 (tsc `~6.0.2`); React 19; react-router 7; TanStack Query v5; Vite 8; Tailwind v4. Backend (small fixes only): Python + FastAPI 0.138.x, SQLAlchemy 2.0.

**Primary Dependencies**: axios (`frontend/src/api/client.ts`, baseURL `/api/v1`, bearer token from `localStorage.auth_token`, 401 → redirect login); `@tanstack/react-query` (staleTime 30s, retry 3, refetchOnWindowFocus false); `react-hot-toast`; existing UI primitives `components/ui/*` (DataTable, Badge, Select, Input, Textarea, Button, ConfirmDialog, PageHeader, LoadingSpinner, EmptyState) and `components/guards/RoleGuard`.

**Storage**: PostgreSQL via the existing backend — **no schema changes**. The DailyDelivery rows are generated at session create (backend fix 1).

**Testing**: Backend — pytest, additions to `tests/test_daily_delivery.py` (checklist generation, complete endpoint, close-after-complete) and RBAC 403 tests for edit/reopen. Frontend — `npm run build` (`tsc -b && vite build`) + `npm run lint` (oxlint); **there is no frontend unit-test runner in this repo**; verification is build + lint + manual quickstart scenarios.

**Target Platform**: Browser SPA (Vite dev server, `http://localhost:5173`) proxying the FastAPI backend at `/api/v1`.

**Project Type**: Web application (React SPA + FastAPI backend).

**Performance Goals**: Session list paginated at `PAGE_SIZE = 50` (backend `limit ≤ 1000`); the checklist table renders expected customers without virtual scrolling (per parent spec EC-10); SC-001 full workflow under 5 minutes, dispatch under 2 minutes — the detail page loads session, deliveries, checklist, and reconciliation in parallel so the Checker never waits on sequential round-trips.

**Constraints**: Mirror backend snake_case contracts exactly; every form/mutation must surface `detail` from FastAPI error responses via toast; role-gate every form route; no new component library; token sheet warnings must be acknowledged before `register-token` proceeds; close only when `BALANCED`.

**Scale/Scope**: 4 new pages + 2 new API/hook modules + 2 types modules; ~3 backend touch points (service + router + tests). Routes: `/delivery/sessions`, `/delivery/sessions/new`, `/delivery/sessions/:id`, `/delivery/sessions/:id/edit`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: Frontend code in `types/api/hooks/pages`; the small backend fixes keep business logic in `delivery_service` (list generation, complete transition) and only add a dependency + endpoint in the routers. No business logic added to routers.
- [x] **RBAC**: Edit/reopen become **server-side OWNER-only** (fix 3) — improves compliance with Principle II. Frontend additionally gates via `RoleGuard`. DELIVERY_PARTNER gets no access to any delivery management page (spec FR-022).
- [x] **Schema-Driven Contracts**: TypeScript interfaces mirror the existing Pydantic v2 response schemas exactly (`delivery_session.py`, `daily_delivery.py`, `delivery_edit.py`). No new backend schemas required for fixes 1–2 (reuse `DeliverySessionDispatch`-style body or empty body; new `complete` uses no body). `DailyDeliveryUpdate` already exists.
- [x] **Soft Deletes**: No new entities; sessions/deliveries already use `is_active`. Cash-sale removal soft-deletes the delivery.
- [x] **Tech Stack**: Unchanged stack; no new libraries.
- [x] **Testing**: New pytest coverage for generate-on-create (planned rows, shift quantities, exceptions excluded, duplicate session still blocked), complete endpoint (happy path + invalid status), close-after-complete, and 403 for non-OWNER edit/reopen. Frontend verified by `npm run build` + `npm run lint` (no FE test runner exists — noted in research.md).
- [x] **Security**: No new credentials/secrets. OWNER enforcement moves to the server.
- [x] **Migrations**: None — no schema changes.

**Gate result: PASS** (one justified deviation — the "frontend-only, no backend changes" assumption in the spec is factually unreachable; see Complexity Tracking).

## Project Structure

### Documentation (this feature)

```text
specs/007-delivery-management-pages/
├── plan.md              # This file
├── research.md          # Phase 0 — decisions, rationale, alternatives
├── data-model.md        # Phase 1 — entities, fields, state machine
├── quickstart.md        # Phase 1 — validation/run guide
├── contracts/
│   ├── sessions.md      # Delivery session + reconciliation + report endpoints
│   └── deliveries.md    # Delivery registration/edit/reopen/token endpoints
├── checklists/requirements.md
├── spec.md
└── tasks.md             # Created by /speckit.tasks (NOT this command)
```

### Source Code (repository root)

```text
frontend/src/
├── types/
│   ├── delivery-session.ts    # NEW — session + reconciliation + report types
│   └── delivery.ts            # NEW — daily delivery + token + edit types
├── api/
│   ├── delivery-sessions.ts   # NEW — session lifecycle + reconciliation API
│   └── deliveries.ts          # NEW — registration/token/edit/reopen API
├── hooks/
│   ├── useDeliverySessions.ts # NEW — session/reconciliation queries + mutations
│   └── useDeliveries.ts       # NEW — delivery/token/edit mutations
├── pages/delivery/
│   ├── SessionListPage.tsx    # NEW — filterable, paginated list
│   ├── SessionCreatePage.tsx  # NEW — route/date/shift/partner form
│   ├── SessionDetailPage.tsx  # NEW — all-in-one scrollable workflow page
│   └── DeliveryEditPage.tsx   # NEW — OWNER edit/reopen page
└── App.tsx                    # EDIT — register /delivery/sessions* routes
```

Backend touch points (small, reviewed):

```text
app/services/delivery_service.py    # EDIT — fix generate_delivery_list; call it in create_session; add complete_session
app/routers/deliveries.py           # EDIT — add POST /{session_id}/complete
app/routers/delivery_edit.py        # EDIT — require_role(["OWNER"]) on edit_delivery + reopen_session
tests/test_daily_delivery.py        # EDIT — new tests (see Testing)
tests/test_delivery_edit.py         # NEW — 403/OWNER tests for edit + reopen
```

**Structure Decision**: The single-project frontend layout under `frontend/src` is extended exactly along the existing per-feature convention (mirror of Phase 3/4 token-books + subscriptions). Backend edits are confined to the three files above so the "frontend feature" remains reviewable as one change set. The all-in-one `SessionDetailPage` replaces the parent route-table's separate `/dispatch`, `/checklist`, `/register`, `/reconciliation` pages — that deviation was already resolved in the parent spec (open question Q4) and is codified by tasks T108–T119.

## Scope & Decisions (resolved during Phase 0)

1. **Planned checklist is generated server-side at session create** (not in the SPA). Rationale: FR-007 requires planned quantities/statuses that only the backend can derive; the parent 002 README already documents "Create session (generate list)". The broken `generate_delivery_list` is rewritten (shift-aware, exception window) and called from `create_session`.
2. **A new `complete` step (STARTED→COMPLETED) precedes close in the UI.** The Reconciliation section shows "Complete session" once validation passes; then "Close session" appears. Matches the documented state machine; the quickstart's implicit STARTED→close assumption is corrected.
3. **Edit/reopen is OWNER-only enforced server-side**, UI additionally hidden behind `RoleGuard roles={["OWNER"]}`.
4. **Session detail data flow**: session header from `GET /deliveries/sessions/{id}`; the registration checklist rows from `GET /deliveries/session/{id}` (the **15-field** `DailyDeliveryResponse`); read-only "expected customers" header from `GET /deliveries/sessions/{id}/checklist`. The 8-field `DailyDeliveryResponse` variant returned by the detail endpoint is **not** used for editing (missing `version`, `cash_amount`, `milk_type_id`).
5. **`route_name` / `delivery_partner_name` / `customer_name` / `milk_type_name` serialize as `null`** from the backend. The SPA joins display names client-side: routes via `useRoutes()`, partners via `useEmployees()` (filter `role === "DELIVERY_PARTNER"`, fall back to all employees), customer/milk-type names via checklist + `useMilkTypes()`/delivery rows.
6. **`submit_reconciliation` and `add_cash_sale` take QUERY parameters** (not JSON bodies) — the SPA must call them with `params` even for POST.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Backend changes in a spec'd "frontend-only" feature | The parent 002 workflow is unreachable as-is: `generate_delivery_list` is dead and crashes on non-existent columns, no endpoint transitions STARTED→COMPLETED (close is impossible), and edit/reopen bypass server-side RBAC. FR-007/FR-016/FR-018 and the spec's own assumption ("checklist generated by the backend") require these fixes. | Pure frontend workarounds degrade semantics (planned rows forced through `/unplanned` → `delivery_source=UNPLANNED`, `planned_quantity=0`, no NOT_DELIVERED/CANCELLED) and leave a constitution Principle II violation server-side. |
