---

description: "Task list for Token Book Pages implementation"
---

# Tasks: Token Book Pages

**Input**: Design documents from `/specs/006-token-books/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks — frontend testing is deferred to Phase 8 of the parent feature (`004-react-frontend`). Verification is via `npm run build` and the quickstart.md scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Task IDs here supersede parent-feature task IDs; the cross-reference (parent T084–T099) is listed in each task description.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/` — this feature is frontend-only; the backend `app/` is untouched.
- All existing infra (API client, UI primitives, guards, constants, nav) comes from parent Phases 1–2 and is reused as-is. `frontend/src/pages/token-books/` exists but is empty.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the shared frontend infrastructure from parent Phases 1–2 is present and clean before adding feature code.

- [X] T001 Run `npm run build` in `frontend/` to confirm a clean baseline (no TypeScript errors) before any changes
- [X] T002 [P] Add `BOOK_ISSUE_STATUS` (`WAITING`, `ACTIVE`, `COMPLETED` with labels/colors) to `frontend/src/lib/constants.ts` and spread it into `STATUS_BADGE_MAP` (needed for token book issue rows)
- [X] T003 [P] Verify `TOKEN_PAYMENT_MODES` (`PREPAID`, `POSTPAID`) and `PAYMENT_STATUS` (`PAID`, `PARTIAL`, `PENDING`) exist in `frontend/src/lib/constants.ts`; add if missing
- [X] T004 [P] Verify nav entries for `/token-identities`, `/token-book-issues`, `/token-book-payments` exist under Operations in `frontend/src/config/permissions.ts` (CHECKER role for identities/issues is added later in US4)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared pieces that must exist before ANY user story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Verify shared UI primitives and guards exist in `frontend/src/components/` (ui/DataTable.tsx, ui/Badge.tsx, ui/Select.tsx, ui/Input.tsx, ui/Button.tsx, ui/ConfirmDialog.tsx, ui/PageHeader.tsx, ui/LoadingSpinner.tsx, ui/EmptyState.tsx, guards/RoleGuard.tsx) and that `useAuth()` is exported from `frontend/src/providers/AuthProvider.tsx`; no changes expected

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Create and manage token identities (Priority: P1) 🎯 MVP

**Goal**: OWNER/ADMIN can list, create, edit (token number), and deactivate token identities (customer + milk type + token number) with customer and milk-type filters.

**Independent Test**: Create an identity for a customer + milk type with token number 100, see it in the list, attempt a duplicate (customer + milk + number) and see it rejected, edit the token number, deactivate it, and filter by customer — all on `/token-identities`.

**Cross-reference**: Parent tasks T084–T088.

### Implementation for User Story 1

- [X] T006 [P] [US1] Create `TokenIdentityCreate`, `TokenIdentityUpdate` (token_number only), `TokenIdentityListResponse`, `TokenIdentityDetailResponse`, `TokenIdentityResponse`, `TokenIdentitySummaryResponse` interfaces in `frontend/src/types/token-identity.ts` per `data-model.md` (import `CustomerSummaryResponse` from `./customer` and `MilkTypeSummaryResponse` from `./milk-type`)
- [X] T007 [US1] Create API functions `getTokenIdentities`, `getTokenIdentity(id)`, `createTokenIdentity`, `updateTokenIdentity(id, data)`, `deleteTokenIdentity(id)` in `frontend/src/api/token-books.ts` using the existing `client` from `./client` (paths `/token-books/identities`, `/token-books/identities/{id}`; list returns plain array — type as `TokenIdentityListResponse[]`)
- [X] T008 [US1] Create TanStack Query hooks `useTokenIdentities`, `useTokenIdentity(id)`, `useCreateTokenIdentity`, `useUpdateTokenIdentity`, `useDeleteTokenIdentity` in `frontend/src/hooks/useTokenBooks.ts` (pattern: `frontend/src/hooks/useSubscriptions.ts`; invalidate `["token-identities"]` and toast on success/error)
- [X] T009 [US1] Create `frontend/src/pages/token-books/TokenIdentityListPage.tsx` with `PageHeader` (Create Identity), `DataTable` columns (customer_code, customer_name, milk_type_name + volume, token_number, Actions), customer filter and milk-type filter (dropdowns from `useCustomers`/`useMilkTypes`, client-side filtering), and Edit/Delete actions with `ConfirmDialog`; loading/empty/error states per `frontend/src/pages/subscriptions/SubscriptionListPage.tsx`
- [X] T010 [P] [US1] Create `frontend/src/pages/token-books/TokenIdentityFormPage.tsx` with customer dropdown (`useCustomers`), milk-type dropdown (`useMilkTypes`, both disabled on edit), token number input; validate token_number > 0; create/edit modes via `useParams().id`; hydrate edit from `useTokenIdentity(id)`; navigate to `/token-identities` after submit
- [X] T011 [US1] Register `/token-identities` (list), `/token-identities/new`, `/token-identities/:id/edit` in `frontend/src/App.tsx` (pattern: subscription routes; wrap the two form routes in `RoleGuard roles={["OWNER", "ADMIN"]}`)

**Checkpoint**: Token identity lifecycle fully functional for OWNER/ADMIN — independently testable via quickstart V1–V2.

---

## Phase 4: User Story 2 - Issue token books with issue numbers (Priority: P1)

**Goal**: OWNER/ADMIN can list, create, update (status/current sheet/completion date/remarks), and deactivate token book issues with customer/identity filters.

**Independent Test**: Create an issue for an identity (issue number 5), see it in the list as WAITING with current sheet 0, update its status to ACTIVE and current sheet to 10, then verify a second issue for the same identity is rejected — all on `/token-book-issues`.

**Cross-reference**: Parent tasks T089–T093.

### Implementation for User Story 2

- [X] T012 [US2] Add `BookIssueStatus`, `TokenBookIssueCreate`, `TokenBookIssueUpdate`, `TokenBookIssueListResponse`, `TokenBookIssueDetailResponse`, `TokenBookIssueResponse`, `TokenBookIssueSummaryResponse` interfaces to `frontend/src/types/token-book.ts` per `data-model.md` (import `TokenIdentitySummaryResponse` from `./token-identity`; do NOT send `issue_date`/`current_sheet`/`status` on create — backend assigns them)
- [X] T013 [US2] Add API functions `getTokenBookIssues`, `getTokenBookIssue(id)`, `createTokenBookIssue`, `updateTokenBookIssue(id, data)`, `deleteTokenBookIssue(id)` to `frontend/src/api/token-books.ts` (paths `/token-books/issues`, `/token-books/issues/{id}`; list returns plain array — type as `TokenBookIssueListResponse[]`)
- [X] T014 [US2] Add TanStack Query hooks `useTokenBookIssues`, `useTokenBookIssue(id)`, `useCreateTokenBookIssue`, `useUpdateTokenBookIssue`, `useDeleteTokenBookIssue` to `frontend/src/hooks/useTokenBooks.ts` (invalidate `["token-book-issues"]`)
- [X] T015 [US2] Create `frontend/src/pages/token-books/TokenBookIssueListPage.tsx` with `PageHeader` (Create Issue), `DataTable` columns (customer_code, customer_name, milk_type_name, token_number, issue_number, issue_date, current_sheet, status badge via `BOOK_ISSUE_STATUS`, Actions), customer filter and identity filter (dropdowns from `useCustomers`/`useTokenIdentities`, client-side), Edit/Delete actions with `ConfirmDialog`; loading/empty/error states
- [X] T016 [P] [US2] Create `frontend/src/pages/token-books/TokenBookIssueFormPage.tsx` with identity selector (from `useTokenIdentities`, offering only identities with no issue in ACTIVE status — compute from `useTokenBookIssues` per clarification Q3), issue number input, remarks; on edit also expose status dropdown (`BOOK_ISSUE_STATUS`), current sheet number, and completion date; validate issue_number > 0; create/edit via `useParams().id`; hydrate edit from `useTokenBookIssue(id)`; navigate to `/token-book-issues` after submit
- [X] T017 [US2] Register `/token-book-issues` (list), `/token-book-issues/new`, `/token-book-issues/:id/edit` in `frontend/src/App.tsx` (wrap the two form routes in `RoleGuard roles={["OWNER", "ADMIN"]}`)

**Checkpoint**: Token book issue lifecycle fully functional — independently testable via quickstart V3.

---

## Phase 5: User Story 3 - Record token book payments (Priority: P2)

**Goal**: OWNER/ADMIN can list, create, update (mode/price/amount/remarks), and deactivate token book payments with computed balance and server-side payment status (display-only).

**Independent Test**: Create a PREPAID payment for an issue (book price 100, amount paid 100), see balance 0 / status PAID; create a partial (40 → balance 60, PARTIAL); attempt amount 150 and see it rejected; edit to full amount and see balance recompute — all on `/token-book-payments`.

**Cross-reference**: Parent tasks T094–T098.

### Implementation for User Story 3

- [X] T018 [US3] Add `BookPaymentStatus`, `TokenPaymentMode`, `TokenBookPaymentCreate`, `TokenBookPaymentUpdate`, `TokenBookPaymentListResponse`, `TokenBookPaymentDetailResponse`, `TokenBookPaymentResponse` interfaces to `frontend/src/types/token-book.ts` per `data-model.md` (do NOT send `payment_status`/`balance_amount` on create — computed server-side; `amount_paid` >= 0 and <= `book_price`)
- [X] T019 [US3] Add API functions `getTokenBookPayments`, `getTokenBookPayment(id)`, `createTokenBookPayment`, `updateTokenBookPayment(id, data)`, `deleteTokenBookPayment(id)` to `frontend/src/api/token-books.ts` (paths `/token-books/payments`, `/token-books/payments/{id}`; list returns plain array — type as `TokenBookPaymentListResponse[]`)
- [X] T020 [US3] Add TanStack Query hooks `useTokenBookPayments`, `useTokenBookPayment(id)`, `useCreateTokenBookPayment`, `useUpdateTokenBookPayment`, `useDeleteTokenBookPayment` to `frontend/src/hooks/useTokenBooks.ts` (invalidate `["token-book-payments"]`)
- [X] T021 [US3] Create `frontend/src/pages/token-books/TokenBookPaymentListPage.tsx` with `PageHeader` (Create Payment), `DataTable` columns (customer_code, customer_name, payment_mode, book_price, amount_paid, balance_amount, payment_status badge via `PAYMENT_STATUS`, payment_date, Actions), issue filter (dropdown from `useTokenBookIssues`, client-side by `token_book_issue_id`), Edit/Delete actions with `ConfirmDialog`; loading/empty/error states
- [X] T022 [P] [US3] Create `frontend/src/pages/token-books/TokenBookPaymentFormPage.tsx` with issue selector (from `useTokenBookIssues`), payment mode dropdown (`TOKEN_PAYMENT_MODES` from `lib/constants.ts`), book price and amount paid inputs, remarks; validate book_price > 0 and 0 <= amount_paid <= book_price; payment status is display-only (per clarification Q4); create/edit via `useParams().id`; hydrate edit from `useTokenBookPayment(id)`; navigate to `/token-book-payments` after submit
- [X] T023 [US3] Register `/token-book-payments` (list), `/token-book-payments/new`, `/token-book-payments/:id/edit` in `frontend/src/App.tsx` (wrap the two form routes in `RoleGuard roles={["OWNER", "ADMIN"]}`)

**Checkpoint**: Token book payment lifecycle fully functional — independently testable via quickstart V4.

---

## Phase 6: User Story 4 - Read-only access for Checker (Priority: P3)

**Goal**: CHECKER can view all three token lists and perform full operations on token identities and token book issues, but token payments remain read-only for CHECKER (no create/edit/delete actions and no reachable form screens).

**Independent Test**: Log in as a CHECKER, open all three lists via the sidebar (identity/issue lists show full actions; payments show none), and navigate directly to `/token-book-payments/new` → ForbiddenPage renders, while `/token-identities/new` and `/token-book-issues/new` render normally.

**Cross-reference**: Parent task T099.

### Implementation for User Story 4

- [X] T024 [P] [US4] Update `frontend/src/config/permissions.ts`: add `"CHECKER"` to the roles of the `/token-identities` and `/token-book-issues` nav items under Operations (Token Payments already includes CHECKER)
- [X] T025 [P] [US4] `frontend/src/pages/token-books/TokenIdentityListPage.tsx` shows full create/edit/delete actions for OWNER/ADMIN/CHECKER (no role gating)
- [X] T026 [P] [US4] `frontend/src/pages/token-books/TokenBookIssueListPage.tsx` shows full create/edit/delete actions for OWNER/ADMIN/CHECKER (no role gating)
- [X] T027 [P] [US4] `frontend/src/pages/token-books/TokenBookPaymentListPage.tsx` hides the Create button and all Edit/Delete actions when `useAuth().user?.role === "CHECKER"` (payments stay read-only for CHECKER)
- [X] T028 [US4] Verify RBAC end-to-end: CHECKER role opens all three list routes (nav + direct URL); token identity/issue forms (`/new`, `/:id/edit`) render via `RoleGuard roles={["OWNER", "ADMIN", "CHECKER"]}`; token payment forms stay `RoleGuard roles={["OWNER", "ADMIN"]}` and render `ForbiddenPage` for CHECKER; DELIVERY_PARTNER has no nav access to any token page

**Checkpoint**: All user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification, documentation sync, and final quality.

- [X] T029 Run `npm run build` in `frontend/` and fix any TypeScript errors introduced by this feature
- [ ] T030 Execute `specs/006-token-books/quickstart.md` scenarios V1–V6 and fix any failures
- [X] T031 [P] Mark parent-feature tasks T084–T099 as complete in `specs/004-react-frontend/tasks.md`
- [X] T032 [P] Update parent-feature implementation status in `specs/004-react-frontend/plan.md` (mark Phase 4 complete)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational completion; sequential in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — no dependencies on other stories (**MVP**)
- **User Story 2 (P1)**: Can start after Foundational — no dependency on US1 (US1's `useTokenIdentities` is consumed by the US2 form's identity selector, but US2 works standalone if US1 is not yet present)
- **User Story 3 (P2)**: Depends on US2's issue list only for its form selector/filter (uses `useTokenBookIssues`); independently testable once issues exist
- **User Story 4 (P3)**: Depends on US1–US3 (modifies all three list pages and verifies shared guards)

### Within Each User Story

- Types before API modules before hooks before pages
- Pages before route registration in `App.tsx`
- Story complete before moving to the next story

### Parallel Opportunities

- Setup T002/T003/T004 touch different files — fully parallel
- US1: T006 (types) is independent; T010 (form page) can run in parallel with T009 (list page) once T007/T008 are done
- US2: T012 and T013 are sequential (both `frontend/src/types/token-book.ts` / `frontend/src/api/token-books.ts`); T016 (form) can run in parallel with T015 (list) once T013/T014 are done
- US3: T018 depends on T012 being merged (same file `frontend/src/types/token-book.ts`); T022 (form) can run in parallel with T021 (list) once T019/T020 are done
- US4: T024/T025/T026/T027 touch different files — fully parallel
- Polish: T031/T032 touch different parent-feature docs — fully parallel
- **Same-file constraints** (must run sequentially, never in parallel):
  - `frontend/src/api/token-books.ts`: T007 → T013 → T019
  - `frontend/src/hooks/useTokenBooks.ts`: T008 → T014 → T020
  - `frontend/src/types/token-book.ts`: T012 → T018
  - `frontend/src/App.tsx`: T011 → T017 → T023

---

## Parallel Example: User Story 1

```bash
# Types (independent — safe to launch alone):
Task: "Create frontend/src/types/token-identity.ts per data-model.md"

# After types + api + hooks are done, list and form pages in parallel:
Task: "Create frontend/src/pages/token-books/TokenIdentityListPage.tsx"
Task: "Create frontend/src/pages/token-books/TokenIdentityFormPage.tsx"

# Last, wire routes (must follow page creation):
Task: "Register token identity routes in frontend/src/App.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `npm run build` + quickstart V1–V2
5. Deploy/demo the token identity management MVP

### Incremental Delivery

1. Setup + Foundational → foundation verified
2. Add User Story 1 → build + quickstart V1–V2 → MVP
3. Add User Story 2 → build + quickstart V3
4. Add User Story 3 → build + quickstart V4
5. Add User Story 4 → build + quickstart V5 (RBAC) + V6 (states)
6. Polish: full build + all quickstart scenarios + parent docs sync

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Developer A: User Story 1; Developer B: User Story 2 (both after Foundation)
3. After US1+US2: Developer A: User Story 3; Developer B: User Story 4
4. Note the same-file constraints (api/token-books.ts, hooks/useTokenBooks.ts, types/token-book.ts, App.tsx) — coordinate edits or keep stories strictly sequential

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to the spec user story for traceability
- Each user story is independently completable and testable via quickstart scenarios
- API contracts are fixed — the backend is unchanged; do not alter request/response shapes
- Do NOT send `issue_date`/`current_sheet`/`status` in issue create, nor `payment_status`/`balance_amount` in payment create (422 or overwritten otherwise)
- Payment status is display-only (server computes PAID/PARTIAL/PENDING); `amount_paid` must be 0 <= amount <= book_price
- An identity blocks a new issue only when it has an issue with status ACTIVE (clarification Q3)
- Deactivated records disappear from lists — the backend returns only `is_active=true` rows (clarification Q2)
- Commit after each task or logical group
