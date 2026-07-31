---

description: "Task list for Subscription & Exceptions Pages implementation"
---

# Tasks: Subscription & Exceptions Pages

**Input**: Design documents from `/specs/005-subscription-exceptions/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks — frontend testing is deferred to Phase 8 of the parent feature (`004-react-frontend`). Verification is via `npm run build` and the quickstart.md scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Task IDs here supersede parent-feature task IDs; the cross-reference (parent T070–T083) is listed in each task description.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` — this feature is frontend-only; the backend `app/` is untouched.
- All existing infra (API client, UI primitives, guards, constants, nav) comes from parent Phases 1–2 and is reused as-is.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the shared frontend infrastructure from parent Phases 1–2 is present and clean before adding feature code.

- [X] T001 Run `npm run build` in `frontend/` to confirm a clean baseline (no TypeScript errors) before any changes
- [X] T002 [P] Verify `EXCEPTION_TYPES` (`VACATION`, `NO_MILK`, `HOLIDAY`) and `STATUS_BADGE_MAP` (ACTIVE/INACTIVE) exist in `frontend/src/lib/constants.ts`; add if missing
- [X] T003 [P] Verify Subscriptions (`/subscriptions`) and Exceptions (`/delivery-exceptions`) nav entries exist under Operations with CHECKER in roles in `frontend/src/config/permissions.ts`; add if missing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared pieces that must exist before ANY user story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Verify shared UI primitives and guards exist in `frontend/src/components/` (ui/DataTable.tsx, ui/Badge.tsx, ui/Select.tsx, ui/Input.tsx, ui/Button.tsx, ui/ConfirmDialog.tsx, ui/PageHeader.tsx, ui/LoadingSpinner.tsx, ui/EmptyState.tsx, guards/RoleGuard.tsx) and that `useAuth()` is exported from `frontend/src/providers/AuthProvider.tsx`; no changes expected

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Create and manage customer subscriptions (Priority: P1) 🎯 MVP

**Goal**: OWNER/ADMIN can list, create, edit, and deactivate customer subscriptions with customer/milk-type/route context and a customer filter.

**Independent Test**: Create a subscription for a customer (morning 2 / evening 1), see it in the list as ACTIVE, edit its quantity, deactivate it, and filter by customer — all on `/subscriptions`.

**Cross-reference**: Parent tasks T070–T075.

### Implementation for User Story 1

- [X] T005 [P] [US1] Create `SubscriptionCreate`, `SubscriptionUpdate`, `SubscriptionListResponse`, `SubscriptionDetailResponse`, `SubscriptionResponse` interfaces in `frontend/src/types/subscription.ts` per `data-model.md` (do NOT include `start_date`/`end_date` on create/update; import `CustomerSummaryResponse` from `./customer` and `MilkTypeSummaryResponse` from `./milk-type`)
- [X] T006 [US1] Create API functions `getSubscriptions`, `getSubscription(id)`, `getSubscriptionsByCustomer(customerId)`, `createSubscription`, `updateSubscription(id, data)`, `deleteSubscription(id)` in `frontend/src/api/subscriptions.ts` using the existing `client` from `./client` (paths `/subscriptions`, `/subscriptions/customer/{id}`; list returns plain array — type as `SubscriptionListResponse[]`)
- [X] T007 [US1] Create TanStack Query hooks `useSubscriptions`, `useSubscription(id)`, `useCreateSubscription`, `useUpdateSubscription`, `useDeleteSubscription` in `frontend/src/hooks/useSubscriptions.ts` (pattern: `frontend/src/hooks/useCustomers.ts`; invalidate `["subscriptions"]` and toast on success/error)
- [X] T008 [US1] Create `frontend/src/pages/subscriptions/SubscriptionListPage.tsx` with `PageHeader` (Create Subscription), `DataTable` columns (customer_code, customer_name, route_name, milk_type_name + volume, morning_quantity, evening_quantity, status badge, Actions), customer filter (dropdown from `useCustomers`), and Edit/Delete actions with `ConfirmDialog`; loading/empty/error states per `frontend/src/pages/customers/CustomerListPage.tsx`
- [X] T009 [P] [US1] Create `frontend/src/pages/subscriptions/SubscriptionFormPage.tsx` with customer dropdown (`useCustomers`), milk-type dropdown (`useMilkTypes`), morning/evening quantity inputs, optional remarks; validate quantities >= 0; create/edit modes via `useParams().id`; hydrate edit from `useSubscription(id)`; navigate to `/subscriptions` after submit
- [X] T010 [US1] Register `/subscriptions` (list), `/subscriptions/new`, `/subscriptions/:id/edit` in `frontend/src/App.tsx` (pattern: existing routes; wrap the two form routes in `RoleGuard roles={["OWNER", "ADMIN"]}`)

**Checkpoint**: Subscription lifecycle fully functional for OWNER/ADMIN — independently testable via quickstart V1–V2.

---

## Phase 4: User Story 2 - Create and manage delivery exceptions (Priority: P1)

**Goal**: OWNER/ADMIN can list, create, edit, and deactivate delivery exceptions (vacation/no-milk/holiday) with customer/route context and a subscription filter.

**Independent Test**: Create a VACATION exception for a subscription, see it in the list, edit its end date, deactivate it, and filter by subscription — all on `/delivery-exceptions`.

**Cross-reference**: Parent tasks T076–T081.

### Implementation for User Story 2

- [X] T011 [P] [US2] Create `ExceptionType`, `DeliveryExceptionCreate`, `DeliveryExceptionUpdate`, `DeliveryExceptionListResponse`, `DeliveryExceptionResponse`, `DeliveryExceptionDetailResponse`, `SubscriptionSummaryResponse` interfaces in `frontend/src/types/delivery-exception.ts` per `data-model.md` (import `CustomerSummaryResponse` from `./customer`)
- [X] T012 [US2] Create API functions `getDeliveryExceptions`, `getDeliveryException(id)`, `getDeliveryExceptionsBySubscription(subscriptionId)`, `createDeliveryException`, `updateDeliveryException(id, data)`, `deleteDeliveryException(id)` in `frontend/src/api/delivery-exceptions.ts` (paths `/delivery-exceptions`, `/delivery-exceptions/subscription/{id}`; list returns plain array — type as `DeliveryExceptionListResponse[]`)
- [X] T013 [US2] Create TanStack Query hooks `useDeliveryExceptions`, `useDeliveryException(id)`, `useCreateDeliveryException`, `useUpdateDeliveryException`, `useDeleteDeliveryException` in `frontend/src/hooks/useDeliveryExceptions.ts` (invalidate `["delivery-exceptions"]`)
- [X] T014 [US2] Create `frontend/src/pages/delivery-exceptions/ExceptionListPage.tsx` with `PageHeader` (Create Exception), `DataTable` columns (customer_code, customer_name, route_name, exception_type, start_date, end_date, status badge, Actions), subscription filter (dropdown from `useSubscriptions`), Edit/Delete actions with `ConfirmDialog`; loading/empty/error states
- [X] T015 [P] [US2] Create `frontend/src/pages/delivery-exceptions/ExceptionFormPage.tsx` with subscription selector (from `useSubscriptions`), exception type dropdown (`EXCEPTION_TYPES` from `lib/constants.ts`), start/end date inputs, optional reason; validate end >= start; create/edit modes via `useParams().id`; hydrate edit from `useDeliveryException(id)`
- [X] T016 [US2] Register `/delivery-exceptions` (list), `/delivery-exceptions/new` in `frontend/src/App.tsx` (wrap the form route in `RoleGuard roles={["OWNER", "ADMIN"]}`)

**Checkpoint**: Exception lifecycle fully functional — independently testable via quickstart V3.

---

## Phase 5: User Story 3 - Read-only access for Checker (Priority: P2)

**Goal**: CHECKER can view both lists read-only with no create/edit/delete actions and no reachable form screens.

**Independent Test**: Log in as a CHECKER, open both lists (no action buttons visible), and navigate directly to `/subscriptions/new` and `/delivery-exceptions/new` → ForbiddenPage renders.

**Cross-reference**: Parent tasks T082–T083.

### Implementation for User Story 3

- [X] T017 [P] [US3] Add role-aware action visibility to `frontend/src/pages/subscriptions/SubscriptionListPage.tsx`: hide the Create button and all Edit/Delete actions when `useAuth().user?.role === "CHECKER"`
- [X] T018 [P] [US3] Add role-aware action visibility to `frontend/src/pages/delivery-exceptions/ExceptionListPage.tsx`: hide the Create button and all Edit/Delete actions when `useAuth().user?.role === "CHECKER"`
- [X] T019 [US3] Verify RBAC end-to-end: CHECKER role opens both list routes (nav + direct URL) with read-only rendering; direct access to `/subscriptions/new`, `/subscriptions/:id/edit`, `/delivery-exceptions/new` renders `ForbiddenPage` via `RoleGuard`; confirm CHECKER is listed in `permissions.ts` nav roles for both items

**Checkpoint**: All user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verification, documentation sync, and final quality.

- [X] T020 Run `npm run build` in `frontend/` and fix any TypeScript errors introduced by this feature
- [X] T021 Execute `specs/005-subscription-exceptions/quickstart.md` scenarios V1–V5 and fix any failures
- [X] T022 [P] Mark parent-feature tasks T070–T083 as complete in `specs/004-react-frontend/tasks.md`
- [X] T023 [P] Update parent-feature implementation status in `specs/004-react-frontend/plan.md` (mark Phase 3 complete)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–5)**: All depend on Foundational completion; sequential in priority order (US1 → US2 → US3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on other stories (**MVP**)
- **User Story 2 (P1)**: Can start after Foundational — independent files; no dependency on US1 (US1's `useSubscriptions` is only consumed by the US2 form selector, so US2 works standalone with a list-only selector fallback)
- **User Story 3 (P2)**: Depends on US1 + US2 (modifies both list pages and verifies shared guards)

### Within Each User Story

- Types before API modules before hooks before pages
- Pages before route registration in `App.tsx`
- Story complete before moving to the next story

### Parallel Opportunities

- Setup T002/T003 can run in parallel
- US1: T005 (types) is independent; T009 (form page) can run in parallel with T008 (list page) once T006/T007 are done
- US2: T011 (types) is independent; T015 (form page) can run in parallel with T014 (list page) once T012/T013 are done
- US3: T017 and T018 modify different files — fully parallel
- Polish: T022/T023 touch different parent-feature docs — fully parallel
- **Same-file constraint**: T010 then T016 (both edit `frontend/src/App.tsx`) — must run sequentially

---

## Parallel Example: User Story 1

```bash
# Types (independent — safe to launch alone):
Task: "Create frontend/src/types/subscription.ts per data-model.md"

# After types + api + hooks are done, list and form pages in parallel:
Task: "Create frontend/src/pages/subscriptions/SubscriptionListPage.tsx"
Task: "Create frontend/src/pages/subscriptions/SubscriptionFormPage.tsx"

# Last, wire routes (must follow page creation):
Task: "Register subscription routes in frontend/src/App.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `npm run build` + quickstart V1–V2
5. Deploy/demo the subscription management MVP

### Incremental Delivery

1. Setup + Foundational → foundation verified
2. Add User Story 1 → build + quickstart V1–V2 → MVP
3. Add User Story 2 → build + quickstart V3
4. Add User Story 3 → build + quickstart V4 (RBAC) + V5 (states)
5. Polish: full build + all quickstart scenarios + parent docs sync

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Developer A: User Story 1; Developer B: User Story 2 (both after Foundation)
3. After US1+US2: Developer A: User Story 3; Developer B: Polish
4. Note the T010 → T016 same-file constraint on `App.tsx` — coordinate registration edits

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to the spec user story for traceability
- Each user story is independently completable and testable via quickstart scenarios
- API contracts are fixed — the backend is unchanged; do not alter request/response shapes
- Do NOT send `start_date`/`end_date` in subscription create/update bodies (422 otherwise)
- Commit after each task or logical group
