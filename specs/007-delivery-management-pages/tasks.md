---

description: "Task list for Delivery Management Pages (Phase 5 React SPA + small backend fixes)"

---

# Tasks: Delivery Management Pages

**Input**: Design documents from `/specs/007-delivery-management-pages/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/sessions.md, contracts/deliveries.md, quickstart.md

**Tests**: Backend pytest tasks are included because the feature ships three backend changes (constitution Principle III requires router tests). Frontend has no unit-test runner in this repo — FE verification is `npm run build` + `npm run lint` per task checkpoint.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend: `frontend/src/...` (React SPA — `types → api → hooks → pages`)
- Backend (small fixes only): `app/services/`, `app/routers/`, `tests/`
- Mirror existing conventions from Phase 3/4 (`useTokenBooks.ts`, `api/token-books.ts`, token-book pages)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline verification and the shared type layer for the delivery feature. No project initialization needed (existing Vite React SPA); no new constants/colors needed — `SESSION_STATUS`, `DELIVERY_STATUS`, `RECONCILIATION_STATUS`, `SHIFTS`, `STATUS_BADGE_MAP`, `getStatusColor` in `frontend/src/lib/constants.ts` + `frontend/src/lib/utils.ts` already contain every value.

- [X] T001 Verify frontend baseline: run `cd frontend && npm run build && npm run lint` — must be clean before feature work starts
- [X] T002 [P] Create `frontend/src/types/delivery-session.ts` — `DeliverySessionCreate`, `DeliverySessionDispatch`, `DeliverySessionReopen`, `DeliverySessionResponse`, `DeliverySessionDetailResponse`, `DeliverySessionListResponse` (`{ sessions, total }`), `ReconciliationResponse`, `SessionReportSummary`/`SessionReportMilkSummary`/`SessionReportResponse`, and `DeliverySessionStatus`/`Shift`/`ReconciliationStatus` unions — mirror `app/schemas/delivery_session.py` + `contracts/sessions.md` exactly (snake_case, `route_name`/`delivery_partner_name` as `string | null`)
- [X] T003 [P] Create `frontend/src/types/delivery.ts` — the 15-field `DailyDeliveryResponse` (incl. `session_id`, `milk_type_id`, `token_book_issue_id`, `cash_amount`, `version`), `DeliveryStatus` union (incl. `"PLANNED"` for generated rows), `DeliveryChecklistResponse` + `ChecklistCustomer`, `TokenValidationRequest/Response/Warning`, `TokenRegistrationRequest/Response`, `UnplannedDeliveryCreate`, `DailyDeliveryUpdate`, `DailyDeliveryEditRequest/Response`, `DeliveryWarning`/`DeliveryWarningsResponse`, `SessionEditResponse`, `CustomerTokenStatusResponse` + `TokenBookStatus`, and `SessionDeliveriesResponse` (`{ session_id, deliveries, total }`) — mirror `app/schemas/daily_delivery.py` + `app/schemas/delivery_edit.py` + `contracts/deliveries.md`

**Checkpoint**: Types are the single source of truth for all API calls (Principle V).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Three small backend fixes that make the parent 002 workflow reachable (auto-checklist on create, STARTED→COMPLETED endpoint, server-side OWNER RBAC) + shared API/hook modules. **⚠️ CRITICAL**: No user story can work end-to-end until these complete.

### Backend fixes

- [X] T004 Rewrite `generate_delivery_list` in `app/services/delivery_service.py` — replace `sub.quantity` (AttributeError — model has `morning_quantity`/`evening_quantity`) and the `DeliveryException.exception_date` filter (AttributeError — model has `start_date`/`end_date`/`shift`). New logic: planned_quantity = `morning_quantity` for MORNING / `evening_quantity` for EVENING, skip subscriptions with 0 for that shift; exclude customers with an exception where `status="ACTIVE"`, `is_active=true`, `start_date ≤ session.delivery_date ≤ COALESCE(end_date, session.delivery_date)`, and `shift IS NULL OR shift = session.shift`; keep `delivery_status="PLANNED"`, `delivery_source="PLANNED"`, `delivered_quantity=0`, `shift`/`delivery_date` from session
- [X] T005 Call `generate_delivery_list(db, session.id)` from `create_session` in `app/services/delivery_service.py` AFTER the session is committed so `session.id` exists; keep the duplicate-session 400 check before generation; ensure a generation failure cannot leave a half-committed session (single try/commit path)
- [X] T006 Add `complete_session(db, session_id)` to `app/services/delivery_service.py` — raises `SessionNotFoundError` / `InvalidSessionStatusError` (must be STARTED), sets `status=COMPLETED`, commits, returns the session (transition already declared in `VALID_SESSION_TRANSITIONS`; reuse `get_session`)
- [X] T007 [P] Add `POST /deliveries/sessions/{session_id}/complete` in `app/routers/deliveries.py` returning `DeliverySessionResponse` (200) — map `SessionNotFoundError`→404, `InvalidSessionStatusError`→400, matching the `start`/`dispatch` handler style
- [X] T008 [P] Add server-side OWNER enforcement to `edit_delivery` (PUT `/deliveries/{delivery_id}/edit`) and `reopen_session` (POST `/deliveries/session/{session_id}/reopen`) in `app/routers/delivery_edit.py` — import/use `require_role` with `["OWNER"]` so non-OWNER returns 403 (research D3; fix the existing frontend-only RBAC gap)
- [X] T009 [P] Backend tests in `tests/test_daily_delivery.py` — (a) create_session auto-generates checklist rows: correct shift quantity from `morning_quantity`/`evening_quantity`, zero-quantity subscription skipped, exception-excluded customer absent, `delivery_status="PLANNED"`; (b) duplicate session for same route+date+shift still returns 400; (c) `POST .../complete` transitions STARTED→COMPLETED and returns 400 when not STARTED; (d) `close` succeeds after `complete` when balanced and returns 400 `SessionNotBalancedError` when unbalanced (mirror existing fixture style in this file, e.g. seeding sessions)
- [X] T010 [P] Create `tests/test_delivery_edit.py` — OWNER RBAC: `edit_delivery` and `reopen_session` return 403 for ADMIN and CHECKER tokens and 200 for OWNER (mirror `conftest.py` auth fixtures and `tests/test_token_books.py` role-test style)

### Shared frontend API + hooks

- [X] T011 [P] Create `frontend/src/api/delivery-sessions.ts` — `createSession`, `listSessions(params)`, `getSession(id)`, `startSession(id, total)`, `dispatchSession(id, total)`, `completeSession(id)`, `closeSession(id)`, `getSessionChecklist(id)`, `getReconciliation(id)`, `getReconciliationSummary(id)`, `getReconciliationCustomers(id)`, `validateReconciliation(id)`, `submitReconciliation(id, params)` and `addCashSale(id, params)`/`removeCashSale(id, cashSaleId)` (⚠️ `submitReconciliation` and `addCashSale` are POST **query params** — call `client.post(url, null, { params })`), `getSessionReport(id)` — return `response.data`, types from `types/delivery-session.ts` + `types/delivery.ts`
- [X] T012 [P] Create `frontend/src/api/deliveries.ts` — `updateDelivery(id, data)` (PUT `/deliveries/{id}`), `addUnplannedDelivery(data)`, `registerToken(id, data)`, `validateToken(data)`, `getDeliveryWarnings(id)`, `getSessionDeliveries(sessionId, params?)`, `getCustomerTokenStatus(customerId)`, `reopenSession(sessionId, data)`, `editDelivery(id, data)` (PUT `/deliveries/{id}/edit`), `getEditHistory(sessionId)` — types from `types/delivery.ts`; note `getEditHistory` returns a **raw list** (no wrapper)
- [X] T013 Create `frontend/src/hooks/useDeliverySessions.ts` — queries `useDeliverySessions(params)` (key `["delivery-sessions"]`), `useDeliverySession(id)`, `useSessionChecklist(id)`, `useReconciliation(id)` (+summary/customers/report/edit-history variants); mutations `useCreateSession`, `useStartSession`, `useCompleteSession`, `useCloseSession`, `useSubmitReconciliation`, `useAddCashSale`, `useRemoveCashSale` — follow `useTokenBooks.ts` pattern: `onSuccess` → `qc.invalidateQueries` on `["delivery-sessions"]` + `["session-detail", id]` + `["reconciliation", id]`, `toast.success`; `onError` → `toast.error(err.response?.data?.detail || "Failed to ...")`
- [X] T014 Create `frontend/src/hooks/useDeliveries.ts` — queries `useSessionDeliveries(sessionId)` (key `["session-deliveries", sessionId]`), `useDeliveryWarnings(id)`, `useCustomerTokenStatus(customerId)`; mutations `useUpdateDelivery`, `useRegisterToken`, `useValidateToken`, `useAddUnplannedDelivery`, `useEditDelivery`, `useReopenSession` — invalidate `["session-deliveries", ...]`, `["reconciliation", ...]`, `["session-detail", ...]` (research: detail-page data must stay live across PLANNED→STARTED→COMPLETED→CLOSED)

**Checkpoint**: `python -m pytest tests/test_daily_delivery.py tests/test_delivery_edit.py -q` passes; backend fixes prove the workflow (checklist populated, complete works, OWNER enforced).

---

## Phase 3: User Story 1 - Manage Delivery Sessions (Priority: P1) 🎯 MVP

**Goal**: Checker/Owner/Admin can create a delivery session (route+date+shift+partner), see all sessions in a filterable list, and open a detail page that shows the Dispatch section and transitions PLANNED→STARTED.

**Independent Test**: Create a session for a route/date/shift/partner → it appears in the list with status PLANNED; duplicate route+date+shift shows an error; filters by date/route/status work; opening a PLANNED session shows the Dispatch section and recording dispatch flips the session to STARTED (Dispatch section then hides).

### Implementation for User Story 1

- [X] T015 [US1] Create `frontend/src/pages/delivery/SessionDetailPage.tsx` scaffold — `useParams` id; parallel queries `useDeliverySession(id)` (header), `useSessionChecklist(id)`, `useReconciliation(id)`; `PageHeader` with route/date/shift/partner names joined client-side (`useRoutes`, `useEmployees` filtered to `role === "DELIVERY_PARTNER"`), status `Badge`; render the five sections (Dispatch, Checklist/Registration, Reconciliation, Close, Summary) with enable/disable gating by `session.status`; LoadingSpinner while loading, error EmptyState on failure
- [X] T016 [US1] Dispatch section in `frontend/src/pages/delivery/SessionDetailPage.tsx` — `total_milk_loaded` input (number > 0), `useStartSession` mutation, visible only when `status="PLANNED"`; ConfirmDialog before dispatching; hides once started (dispatch-once, FR-006); 400 `Dispatch already recorded` surfaced via toast
- [X] T017 [P] [US1] Create `frontend/src/pages/delivery/SessionListPage.tsx` — filters (delivery date, route `Select`, status `Select`), `useDeliverySessions(params)`; `DataTable` columns route (client-joined), date, shift, partner (client-joined), status Badge, reconciliation status Badge, loaded milk; pagination via the `PaginatedResponse` envelope (first consumer — `totalPages = Math.ceil(total / PAGE_SIZE)`); `onRowClick` → `/delivery/sessions/:id`; LoadingSpinner/EmptyState early returns; "New Session" PageHeader action
- [X] T018 [P] [US1] Create `frontend/src/pages/delivery/SessionCreatePage.tsx` — plain `useState` form per convention: route `Select` (`useRoutes`), date input, shift `Select` (`SHIFTS`), delivery partner `Select` (`useEmployees`, default filter `role === "DELIVERY_PARTNER"`, fall back to all employees if none); `errors` + `validate()`; `useCreateSession` → toast + redirect to `/delivery/sessions/:id`; duplicate-session 400 surfaced as a clear error (FR-004)
- [X] T019 [US1] Register routes in `frontend/src/App.tsx` — `/delivery/sessions` (SessionListPage), `/delivery/sessions/new` (SessionCreatePage, `<RoleGuard roles={["OWNER","ADMIN","CHECKER"]}>`), `/delivery/sessions/:id` (SessionDetailPage, same RoleGuard) — pattern matches existing token-book routes; nav entry already exists in `config/permissions.ts`

**Checkpoint**: US1 independently testable — session create/list/filter/detail/dispatch all work (SC-005: dispatch under 2 minutes).

---

## Phase 4: User Story 2 - Register Deliveries and Token Sheets (Priority: P1)

**Goal**: The Checker sees the expected-customer checklist (from the auto-generated planned rows) and registers each row's delivery status and token sheet, with warning acknowledgment, plus unplanned deliveries.

**Independent Test**: Open a session's checklist (after dispatch); set rows to DELIVERED (with sheet → validation → warning acknowledgment), PENDING_TOKEN, CASH_SALE (amount), NOT_DELIVERED, CANCELLED; add an unplanned delivery; every mutation updates the row and reconciliation totals.

### Implementation for User Story 2

- [X] T020 [US2] Checklist/Registration section in `frontend/src/pages/delivery/SessionDetailPage.tsx` — rows from `useSessionDeliveries(id)` (15-field); join customer name/phone/address from `useSessionChecklist(id)` and milk-type name from `useMilkTypes`; columns: customer, phone, milk type, planned qty, status Badge, token sheet, actions; enabled when status is STARTED or COMPLETED, read-only when CLOSED; "PLANNED" delivery_status renders as unregistered
- [X] T021 [US2] Per-row status control in `frontend/src/pages/delivery/SessionDetailPage.tsx` — status dropdown (DELIVERED / PENDING_TOKEN / CASH_SALE / NOT_DELIVERED / CANCELLED) → `useUpdateDelivery` (PUT `/deliveries/{id}`) passing `version` from the row (409 conflict → toast "reload and retry"); CASH_SALE requires inline cash amount > 0 before save (FR-011); per-row loading state; invalidate row + reconciliation
- [X] T022 [US2] Token sheet flow in `frontend/src/pages/delivery/SessionDetailPage.tsx` — DELIVERED shows a sheet-number input → `useValidateToken` (customer_id + milk_type_id + sheet) → if `requires_acknowledgment`, show warnings modal (codes/messages, e.g. NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, NEW_BOOK_BEFORE_OLD_FINISHED) with acknowledgment checkbox (mandatory, FR-010) → `useRegisterToken` with `acknowledged_warnings` (+ optional reason); 400 errors (already used, out of range, no active book, completed book) surfaced via toast; no silent out-of-sequence registration (SC-003)
- [X] T023 [US2] "Add Unplanned Delivery" form in `frontend/src/pages/delivery/SessionDetailPage.tsx` — existing-customer select OR walk-in (name + 10-digit phone), milk type `Select`, quantity, delivery status (DELIVERED/PENDING_TOKEN/CASH_SALE), registration method, amount when CASH, `reason` required → `useAddUnplannedDelivery`; new row appears with source UNPLANNED and counts in reconciliation (FR-012)
- [X] T024 [US2] Wire states + invalidation in `frontend/src/pages/delivery/SessionDetailPage.tsx` — EmptyState when `deliveries` is empty (FR-021/edge case); loading/error states per section; every status/token/unplanned mutation invalidates `["session-deliveries", id]`, `["reconciliation", id]`, `["session-detail", id]`

**Checkpoint**: US1 + US2 — daily registration flows complete and independently verifiable.

---

## Phase 5: User Story 3 - Reconcile and Close Session (Priority: P1)

**Goal**: The Checker reviews loaded vs token vs cash vs returned, adjusts cash sales and returned milk, validates, completes, and closes the session only when balanced; a read-only summary appears after close.

**Independent Test**: With 5L loaded / 3L token / 1L cash / 1L returned the reconciliation shows BALANCED; unbalanced shows the difference and blocks close; close succeeds only after complete + balanced; after CLOSED all inputs are read-only and the summary renders.

### Implementation for User Story 3

- [X] T025 [US3] Reconciliation section in `frontend/src/pages/delivery/SessionDetailPage.tsx` — summary cards from `useReconciliation(id)`: loaded milk, token-registered, cash sales, returned, total accounted, difference, balance status Badge (BALANCED/UNBALANCED/PENDING); enabled when STARTED/COMPLETED
- [X] T026 [US3] Cash sales sub-section in `frontend/src/pages/delivery/SessionDetailPage.tsx` — add form (name, optional phone, milk type, quantity, amount) via `useAddCashSale` (**query params**), list of added cash sales with remove via `useRemoveCashSale` + ConfirmDialog (FR-014)
- [X] T027 [US3] Returned milk + validate in `frontend/src/pages/delivery/SessionDetailPage.tsx` — returned-milk input held locally and sent with submit; "Validate" button → `validateReconciliation` → show issues (RECONCILIATION_MISMATCH as red ERROR, PENDING_TOKENS as amber WARNING) (FR-015)
- [X] T028 [US3] Submit reconciliation in `frontend/src/pages/delivery/SessionDetailPage.tsx` — `useSubmitReconciliation` with `total_cash_collected`, `cash_sales`, `returned_milk`, `returned_reasons`, `token_sheets_collected`, `remarks` as **params**; refresh reconciliation queries
- [X] T029 [US3] Complete + Close in `frontend/src/pages/delivery/SessionDetailPage.tsx` — "Complete session" (enabled when STARTED) via `useCompleteSession`; "Close session" (enabled when COMPLETED) via `useCloseSession`, each behind ConfirmDialog (FR-023); unbalanced close blocked — the 400 difference message is displayed (FR-016, SC-002); after CLOSED all inputs become read-only (FR-016)
- [X] T030 [US3] Read-only Summary section in `frontend/src/pages/delivery/SessionDetailPage.tsx` — rendered when CLOSED (or from report) using `useSessionReport(id)` + reconciliation summary: customer counts by status and milk totals (FR-017)

**Checkpoint**: US1 + US2 + US3 — the full daily workflow create→dispatch→register→reconcile→complete→close works (SC-001, SC-002, SC-005).

---

## Phase 6: User Story 4 - Edit Previous Deliveries and Reopen Sessions (Priority: P2, OWNER only)

**Goal**: The Owner reopens closed sessions (with a required reason) and edits previous deliveries (status/token sheet) with an audit trail, then re-closes once balanced.

**Independent Test**: As OWNER, reopen a CLOSED session (reason required) → editable; edit a DELIVERED row to NOT_DELIVERED with `return_token_sheet: true` (reason required) → token sheet returned and edit logged; edit history shows the entries; reconcile + close again works. As CHECKER/ADMIN the flows are absent and the API returns 403.

### Implementation for User Story 4

- [X] T031 [US4] Reopen flow in `frontend/src/pages/delivery/SessionDetailPage.tsx` — OWNER-only (RoleGuard + `useAuth` role check); "Reopen" button on CLOSED sessions → reason modal (required, FR-018/FR-023) → `useReopenSession`; after reopen the session becomes editable again; `reopen_count` reflected in header
- [X] T032 [P] [US4] Create `frontend/src/pages/delivery/DeliveryEditPage.tsx` — route `/delivery/sessions/:id/edit` (`<RoleGuard roles={["OWNER"]}>` registered in `App.tsx`): select a delivery, change status (DELIVERED/PENDING_TOKEN/CASH_SALE/NOT_DELIVERED/CANCELLED), toggle `return_token_sheet`, required `reason` (1–500), pass `version` → `useEditDelivery`; show old/new status + token-sheet-return result; 403/409 surfaced via toast
- [X] T033 [US4] Edit history panel in `frontend/src/pages/delivery/SessionDetailPage.tsx` — OWNER-only, from `useEditHistory(id)` (raw list): render STATUS_CHANGE and SESSION_REOPEN entries with reason, editor, edited_at; refresh after reopen/edit (FR-019, SC-004)
- [X] T034 [US4] Reconcile-after-edit wiring in `frontend/src/pages/delivery/SessionDetailPage.tsx` — after edits, mutations invalidate `["reconciliation", id]` and `["session-deliveries", id]` so totals recalc; the session closes again only when balanced (FR-020); Summary reflects the re-closed state

**Checkpoint**: US1–US4 — Owner corrections fully work with audit trail (SC-004).

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Access-control verification and full validation of the complete feature.

- [X] T035 [P] Verify access control (FR-022): DELIVERY_PARTNER sees no `/delivery/sessions*` nav and is blocked by RoleGuard; edit/reopen UI hidden for non-OWNER
- [X] T036 Run full verification: `python -m pytest -q` (all backend tests) + `cd frontend && npm run build && npm run lint` — fix any regressions
- [X] T037 Run `quickstart.md` scenarios 1–4 end-to-end; update `quickstart.md`/contracts if observed behavior differs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T002–T003 types); **BLOCKS all user stories**
- **User Stories (Phase 3+)**: All depend on Foundational (backend fixes + API/hooks)
  - US1 → US2 → US3 are sequential (US2's checklist and US3's reconciliation build on the SessionDetailPage sections from US1; all three are P1)
  - US4 (P2) depends on US1–US3 (needs a CLOSED session to reopen)
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Foundational T011–T014 (API/hooks) — no other story dependency
- **User Story 2 (P1)**: Depends on US1 (SessionDetailPage scaffold + dispatch) and Foundational T012/T014
- **User Story 3 (P1)**: Depends on US2 (registration drives reconciliation totals) and Foundational backend `complete` endpoint (T006–T007)
- **User Story 4 (P2)**: Depends on US3 (a session must be closed to reopen) and Foundational OWNER RBAC (T008, T010)

### Within Each User Story

- Types before API before hooks before pages (within Foundational)
- Backend service → router → tests before frontend consumes it (within Foundational)
- SessionDetailPage scaffold before its sections
- Core implementation before integration

### Parallel Opportunities

- T002/T003 (types), T004/T008/T009/T010 (backend), T011/T012 (API) all run in parallel
- T007 [P] depends on T006; T009 depends on T005+T007; T010 depends on T008
- T017/T018 (list + create pages) run in parallel
- T032 (DeliveryEditPage, new file) runs in parallel with the US4 SessionDetailPage tasks

---

## Parallel Example: Foundational Backend Fixes

```bash
Task: "Rewrite generate_delivery_list in app/services/delivery_service.py"
Task: "Add OWNER require_role in app/routers/delivery_edit.py"
Task: "Backend tests in tests/test_daily_delivery.py"
Task: "Backend tests in tests/test_delivery_edit.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (types)
2. Complete Phase 2: Foundational (backend fixes + shared API/hooks) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (session create/list/detail/dispatch)
4. **STOP and VALIDATE**: `pytest` + `npm run build` + manual session create→dispatch (SC-005)
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → session create auto-generates the checklist (backend proven by tests)
2. Add US1 → test independently (session lifecycle) → demo (MVP!)
3. Add US2 → test independently (registration + token sheets) → demo
4. Add US3 → test independently (reconcile + close) → demo
5. Add US4 → test independently (OWNER reopen/edit) → demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (backend fixes and API/hooks are the critical path)
2. Developer A: US1 (SessionList/Create/Detail/Dispatch)
3. Developer B: US2 sections (registration + token sheets) — needs US1's detail scaffold first
4. Developer C: backend tests + OWNER RBAC, then US4

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts (all US2/US3 tasks are in `SessionDetailPage.tsx` and MUST be sequential), cross-story dependencies that break independence
