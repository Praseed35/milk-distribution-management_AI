# Research: Delivery Management Pages (Phase 5)

**Feature**: 007-delivery-management-pages
**Date**: 2026-07-31
**Status**: Complete — all NEEDS CLARIFICATION resolved

## 1. Backend contract verification

Verified directly against `app/routers/deliveries.py`, `app/routers/delivery_edit.py`, `app/schemas/delivery_session.py`, `app/schemas/daily_delivery.py`, `app/schemas/delivery_edit.py`, and the delivery models. Full details in [contracts/sessions.md](./contracts/sessions.md) and [contracts/deliveries.md](./contracts/deliveries.md).

Key findings:

- **Two `DailyDeliveryResponse` shapes exist.** `app/schemas/delivery_session.py` defines an 8-field variant (no `session_id`, `milk_type_id`, `cash_amount`, `version`); `app/schemas/daily_delivery.py` defines the full 15-field variant. The session-detail endpoint returns the 8-field variant; the update/unplanned/session-deliveries endpoints return the 15-field variant.
- **`route_name`, `delivery_partner_name`, `customer_name`, `milk_type_name` always serialize as `null`** — these are declarative-only fields with `from_attributes=True` and no matching ORM attributes.
- **`submit_reconciliation` and `add_cash_sale` read QUERY parameters**, not JSON bodies.
- **`generate_delivery_list` exists but is never called** and references two non-existent columns: `Subscription.quantity` (model has `morning_quantity`/`evening_quantity`) and `DeliveryException.exception_date` (model has `start_date`/`end_date`/`shift`). It would raise `AttributeError`.
- **No endpoint transitions a session to COMPLETED.** `close_session` requires COMPLETED (delivery_service.py:259) but only `reopen_session` ever sets COMPLETED. Tests seed the DB directly (`tests/test_daily_delivery.py:77`). Parent tasks T073/T075 (quickstart validation, state-transition tests) are unchecked.
- **`edit_delivery` and `reopen_session` require any valid token** — `OwnerRequiredError` exists but is never raised. Parent 002 spec FR and 007 spec FR-018/FR-022 require OWNER-only.
- Parent quickstart 002 scenario 1 documents `POST /deliveries/sessions/` as "Create session (generate list)" and expects close to work after submit — the design intent behind fixes 1 and 2.

## Decisions

### D1 — Planned checklist is generated server-side at session create

- **Decision**: Rewrite `generate_delivery_list()` (shift-aware, correct exception filtering) and call it from `create_session()` after the session is persisted.
- **Rationale**: FR-007 (expected customers from active subscriptions minus exceptions) requires planned `DailyDelivery` rows with correct per-shift quantities and PLANNED status; only the backend can compute this. This matches the parent 002 README contract table ("POST /deliveries/sessions/ — Create session (generate list)") and the user-approved plan option.
- **Alternatives considered**: (a) A new `POST /deliveries/sessions/{id}/generate-checklist` endpoint + explicit SPA call — rejected, adds a UI step and an endpoint for behavior the parent documented as part of create; (b) SPA-side derivation from subscriptions+exceptions with registration forced through `/deliveries/unplanned` — rejected, produces `delivery_source=UNPLANNED`, `planned_quantity=0`, and cannot set NOT_DELIVERED/CANCELLED for planned rows, breaking reconciliation and FR-007.
- **Implementation notes** (for tasks): quantity = `morning_quantity` for MORNING, `evening_quantity` for EVENING; skip subscriptions whose shift quantity is 0 or whose customer has an active exception for the session date (exception `status=ACTIVE`, `is_active=true`, `start_date ≤ date ≤ COALESCE(end_date,∞)`, and `shift IS NULL OR shift = session.shift`); `delivery_status="PLANNED"`, `delivery_source="PLANNED"`, `delivered_quantity=0`. Duplicate-session check must run before generation. Generation failures must not create a half-committed session.

### D2 — Complete step (STARTED→COMPLETED) added to the API

- **Decision**: Add `POST /deliveries/sessions/{id}/complete` (body-less; 400 if not STARTED; returns `DeliverySessionResponse`) and a matching `complete_session` service function.
- **Rationale**: `close_session` requires COMPLETED, but no endpoint reaches COMPLETED; the UI close flow would be impossible. The transition is already declared in `VALID_SESSION_TRANSITIONS` (delivery_service.py:31) and the parent research state machine.
- **Alternatives considered**: (a) Let `close` accept STARTED directly — rejected, skips the documented COMPLETED stage and would diverge from the dashboard's `completed_not_closed` reporting concept; (b) fold complete into reconciliation submit — rejected, mixes concerns and hides a state transition inside a data submission.
- **Implementation notes**: In the SPA the Reconciliation section shows "Complete session" (enabled when STARTED and validation passes) then "Close session" (enabled when COMPLETED and balanced), each with a ConfirmDialog.

### D3 — OWNER-only edit/reopen enforced server-side

- **Decision**: Add `require_role(["OWNER"])` (via `get_current_user` + role check) to `PUT /deliveries/{delivery_id}/edit` and `POST /deliveries/session/{session_id}/reopen`; return 403 for non-OWNER.
- **Rationale**: Constitution Principle II requires server-side role authorization; the spec (FR-018/FR-022) says OWNER-only. UI still gates via `RoleGuard roles={["OWNER"]}`.
- **Alternatives considered**: Frontend-only gating — rejected (documented security gap, violates Principle II; user approved the backend fix).

### D4 — Standardize SPA on the 15-field `DailyDeliveryResponse`

- **Decision**: Registration/edit forms read deliveries from `GET /deliveries/session/{session_id}` (15-field, includes `version` for optimistic locking, `cash_amount`, `milk_type_id`, `token_book_issue_id`). The 8-field variant on the session-detail response is ignored for editing.
- **Rationale**: `PUT /deliveries/{id}` and `PUT /deliveries/{id}/edit` both accept `version` for 409 conflict detection; the 8-field shape cannot supply it.
- **Alternatives considered**: Enriching the 8-field schema — rejected, touches backend schemas unnecessarily when the richer endpoint already exists.

### D5 — Client-side display-name joining

- **Decision**: Because `route_name`/`delivery_partner_name`/`customer_name`/`milk_type_name` serialize as null, the SPA maps IDs to names with existing hooks: `useRoutes()`, `useEmployees()` (partners filtered to `role === "DELIVERY_PARTNER"`, fallback to all employees when none), `useMilkTypes()`, and the checklist endpoint's customer names/phones/addresses.
- **Rationale**: Zero backend changes for display; consistent with how Phase 3/4 pages already join names.
- **Alternatives considered**: Backend joins in response schemas — rejected (declarative-only fields, larger scope).

### D6 — Query-parameter POSTs

- **Decision**: `submitReconciliation` and `addCashSale` call `client.post(url, null, { params: {...} })` (axios params), never a body.
- **Rationale**: The FastAPI handlers declare query parameters, not body models.

## Frontend conventions confirmed (mirror targets)

- Hook pattern (`useTokenBooks.ts`): `useQuery({ queryKey: ["<kebab-list>"], queryFn: api.x })`, mutations with `onSuccess` → `qc.invalidateQueries` + `toast.success`, `onError` → `toast.error(err.response?.data?.detail || "Failed to ...")`.
- API pattern (`api/token-books.ts`): `client.get/post/put/delete<T>` returning `response.data`; snake_case params.
- Types: `XxxCreate`, `XxxUpdate` (partial), `XxxResponse`, `XxxListResponse`/`XxxDetailResponse`, status string unions. `PaginatedResponse<T>` in `types/common.ts` already supports `sessions`/`deliveries`/`total` — session and session-deliveries lists are the first consumers of pagination (`totalPages = ceil(total/PAGE_SIZE)`).
- List page: `PageHeader` + filters (`<Select>`) + `DataTable` (`columns {key, header, render?}`, `keyExtractor`, `onRowClick`) + `LoadingSpinner`/`EmptyState` early returns.
- Form page: plain `useState` + `errors: Record<string,string>` + `validate()` + `handleSubmit(e: FormEvent)` + `<Button type="submit" loading>`; selects populated from existing hooks.
- Routing: routes in `App.tsx` inside `ProtectedRoute`+`AppLayout`, wrapped in `<RoleGuard roles={[...]}>`; header `pageTitles` already covers `/delivery/sessions` via `startsWith`.
- Constants/colors: `SESSION_STATUS`, `DELIVERY_STATUS` (no SKIPPED), `RECONCILIATION_STATUS`, `SHIFTS`, `STATUS_BADGE_MAP`, and `getStatusColor` already contain every needed value. No new UI primitive required (Textarea already exists from Phase 4).
- Nav: "Delivery → Sessions" exists at `/delivery/sessions` for OWNER/ADMIN/CHECKER (permissions.ts:45).
- No frontend unit-test runner exists (`package.json` has `build` = `tsc -b && vite build`, `lint` = `oxlint`). Verification is build + lint + manual scenarios.
