---

description: "Task list for Payment Management Pages (Phase 6 React SPA, frontend-only)"

---

# Tasks: Payment Management Pages

**Input**: Design documents from `/specs/008-payment-management-pages/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/payments-api.md, quickstart.md

**Tests**: No backend tests — this phase adds zero backend code (Sprint 6 backend already has 5 test files). Frontend verification is `cd frontend && npx tsc -b && npm run lint` per task checkpoint, plus the Playwright E2E suite (`frontend/e2e/payments.spec.ts`) in the final phase, consistent with the green Phase 1–5 suite (32 specs).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Frontend: `frontend/src/...` (React SPA — `types → api → hooks → pages`)
- E2E: `frontend/e2e/...`
- Mirror existing conventions from Phase 4 (`useTokenBooks.ts`, `api/token-books.ts`, token-book pages) and Phase 5 (delivery pages)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline verification plus the shared type/constants layer. No project initialization needed (existing Vite React SPA). `PAYMENT_MODES` already exists in `frontend/src/lib/constants.ts`.

- [x] T001 Verify frontend baseline: run `cd frontend && npx tsc -b && npm run lint` — must be clean before feature work starts
- [x] T002 [P] Add `PAYMENT_TYPES = ["ADVANCE","BILL_PAYMENT"]` and `BILL_STATUS` (`PENDING`/`PARTIAL`/`PAID`/`OVERDUE`/`CANCELLED` with labels/colors) to `frontend/src/lib/constants.ts` and merge `BILL_STATUS` into `STATUS_BADGE_MAP` (mirror the existing `PAYMENT_STATUS` pattern)
- [x] T003 [P] Create `frontend/src/types/payment.ts` — interfaces mirroring `app/schemas/payment.py` + `contracts/payments-api.md` exactly (snake_case): `PaymentMode`/`PaymentType`/`BillStatus` unions, `CustomerPaymentCreate`, `CustomerPaymentResponse`, `CustomerPaymentListResponse` (`customer_code`, `customer_name`), `BillGenerateRequest`, `CustomerBillResponse` (incl. `items: BillItem[]`, `paid_amount`, `balance_amount`), `CustomerBillListResponse`, `CustomerBillItemResponse`, `OutstandingBalanceResponse`

**Checkpoint**: Types are the single source of truth for all API calls (Principle V).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared API and hook modules every payment page consumes. **⚠️ CRITICAL**: No user story can work end-to-end until these complete.

- [x] T004 Create `frontend/src/api/payments.ts` — `listPayments(params?: { customer_id?; payment_mode?; payment_type?; from_date?; to_date? })` (GET `/payments/`, `{ params }`), `createPayment(data: CustomerPaymentCreate)` (POST `/payments/`), `generateBill(data: BillGenerateRequest)` (POST `/payments/bills/generate`), `listBills(params?: { customer_id?; status?; from_date?; to_date? })` (GET `/payments/bills/`), `getBill(id)` (GET `/payments/bills/{id}`), `updateBillStatus(id, status)` (PUT `/payments/bills/{id}/status`), `getOutstanding(customerId)` (GET `/payments/outstanding/{customerId}`) — return `response.data`, types from `types/payment.ts`, mirror `api/token-books.ts` style
- [x] T005 Create `frontend/src/hooks/usePayments.ts` — queries `usePayments(params?)` (key `["payments", params]`), `useBills(params?)` (key `["bills", params]`), `useBill(id)` (key `["bills", id]`, `enabled: !!id`), `useOutstanding(customerId)` (key `["outstanding", customerId]`, `enabled: !!customerId`); mutations `useCreatePayment` (invalidate `["payments"]`, `["bills"]`, `["outstanding"]` — a BILL_PAYMENT changes bill totals), `useGenerateBill` (invalidate `["bills"]`), `useUpdateBillStatus` (invalidate `["bills"]`, `["bills", id]`, `["outstanding"]`) — follow `useTokenBooks.ts` pattern: `onSuccess` → `toast.success` + `qc.invalidateQueries`, `onError` → `toast.error(err.response?.data?.detail || "Failed to ...")`

**Checkpoint**: `cd frontend && npx tsc -b` passes with the new modules; user story implementation can begin.

---

## Phase 3: User Story 1 - Record Customer Payments (Priority: P1) 🎯 MVP

**Goal**: Owner/Admin records a customer payment as ADVANCE or BILL_PAYMENT (mode, amount, reference, remarks) and sees it in a history list.

**Independent Test**: Open Payments → Create Payment, record an ADVANCE payment (customer/amount/mode), save → redirected; the payment appears in the history with system date and no linked bill. Record a BILL_PAYMENT against an unpaid bill → bill paid/balance/status update. BILL_PAYMENT without a bill is blocked; a PAID/CANCELLED bill is rejected.

### Implementation for User Story 1

- [x] T006 [US1] Create `frontend/src/pages/payments/PaymentListPage.tsx` — `usePayments()`; `PageHeader` "Create Payment" action → `/payments/new`; `DataTable` columns customer (code + name), payment date (`formatDate`), amount (`formatCurrency`), mode, type, reference number, linked bill; read-only (NO edit/delete actions — immutability FR-008/SC-007); `LoadingSpinner` while loading, `EmptyState` when none (mirror `TokenBookPaymentListPage.tsx`)
- [x] T007 [US1] Create `frontend/src/pages/payments/PaymentFormPage.tsx` — `noValidate` form per convention: customer `Select` (`useCustomers`), payment type `Select` (`PAYMENT_TYPES`, default `ADVANCE`), amount `Input` (number > 0), payment mode `Select` (`PAYMENT_MODES`), reference `Input` (optional), remarks `Textarea`; when type = `BILL_PAYMENT` show a bill `Select` filtered to the chosen customer's non-PAID/non-CANCELLED bills (`useBills({ customer_id })`) with the bill's `balance_amount` displayed (FR-004/FR-005); `validate()` errors per field; `useCreatePayment` → `toast` + navigate `/payments`; surface backend 400/404 details (FR-005)
- [x] T008 [US1] Register `/payments` (PaymentListPage) and `/payments/new` (PaymentFormPage) in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>` (pattern matches token-book routes; nav entry already exists in `config/permissions.ts`)

**Checkpoint**: US1 independently testable — payment record + history visible (SC-001: record under 1 minute on first use).

---

## Phase 4: User Story 2 - Generate Customer Bills (Priority: P1)

**Goal**: Owner/Admin generates bills for one or more customers over a date range and sees them in a filterable Bills list.

**Independent Test**: Generate a bill for a customer with DELIVERED deliveries in the period → bill appears with correct line items and total; a customer with no deliveries in the period gets no bill and the page explains why; bills list filters by customer/status/date.

### Implementation for User Story 2

- [x] T009 [US2] Create `frontend/src/pages/payments/BillListPage.tsx` — `useBills(params)`; filters customer `Select` (`useCustomers`), status `Select` (`BILL_STATUS` keys), date range (from/to date inputs); `DataTable` columns customer, bill date, period, total/paid/balance (`formatCurrency`), status `Badge` (`STATUS_BADGE_MAP`), due date; `PageHeader` "Generate Bill" action → `/payments/bills/generate`; `onRowClick` → `/payments/bills/:id`; LoadingSpinner/EmptyState
- [x] T010 [US2] Create `frontend/src/pages/payments/BillGeneratePage.tsx` — multi-select customers (checkbox list from `useCustomers`), bill period start/end date inputs (required), optional due date + remarks; before generating, warn if `useBills({ customer_id, from_date, to_date })` already returns a bill for any selected customer/period (FR-013); on Generate, loop `generateBill` sequentially (`mutateAsync` per customer) and show per-customer results — success (bill id/total) or failure explanation e.g. no deliveries in period (FR-011/FR-012); `Button loading` while running
- [x] T011 [US2] Register `/payments/bills` (BillListPage) and `/payments/bills/generate` (BillGeneratePage) in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>`

**Checkpoint**: US2 independently testable — bill generation + list verified (SC-003: no-delivery attempts create no bill; SC-004: generate + verify under 3 minutes).

---

## Phase 5: User Story 3 - View Outstanding Balances (Priority: P1)

**Goal**: Owner/Admin sees each customer's outstanding balance (billed, paid, balance, last bill/last payment dates).

**Independent Test**: Record a payment settling part of a bill, open Outstanding → the customer's balance equals billed − paid and last bill/payment dates are correct; a customer with no activity shows a zero balance.

### Implementation for User Story 3

- [x] T012 [US3] Create `frontend/src/pages/payments/OutstandingPage.tsx` — `useCustomers()`; for each active customer call `useOutstanding(customer.id)` (build a `useQueries` array so all resolve in one pass); `DataTable` columns customer (code + name), total billed, total paid, balance (`formatCurrency`), last bill date, last payment date; customer filter `Select` to narrow (FR-017); zero-balance customers still shown (Edge Cases); refresh button / rely on `["outstanding"]` invalidation from payment mutations
- [x] T013 [US3] Register `/payments/outstanding` (OutstandingPage) in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>`

**Checkpoint**: US3 independently testable — outstanding equals billed − paid for every customer (SC-005).

---

## Phase 6: User Story 4 - Payment History and Filters (Priority: P2)

**Goal**: Owner/Admin filters payment history by customer, payment mode, payment type, and date range.

**Independent Test**: Record payments of different types/modes, then filter by each dimension and confirm only matching rows show; no edit/delete control exists on any row.

### Implementation for User Story 4

- [x] T014 [US4] Add filter controls to `frontend/src/pages/payments/PaymentListPage.tsx` — customer `Select` (`useCustomers`), payment mode `Select` (`PAYMENT_MODES`), payment type `Select` (`PAYMENT_TYPES`), from/to date `Input`s; wire to `usePayments(filters)` (pass `{ customer_id, payment_mode, payment_type, from_date, to_date }`, omitting empty values); ensure list stays read-only (FR-002, FR-008)

**Checkpoint**: US4 independently testable — all four filter dimensions work; no edit/delete on payment rows.

---

## Phase 7: User Story 5 - Manage Bill Status (Priority: P2)

**Goal**: Owner/Admin views a bill's detail (line items + applied payments) and updates its status (PENDING/PARTIAL/PAID/OVERDUE/CANCELLED) with confirmation.

**Independent Test**: Open a bill detail → line items and totals shown; change status to OVERDUE with confirmation → list reflects it; cancelling a bill that has payments warns first and requires acknowledgment.

### Implementation for User Story 5

- [x] T015 [US5] Create `frontend/src/pages/payments/BillDetailPage.tsx` — `useBill(id)`; header (customer, bill date, period, status `Badge`, totals); line items `DataTable` (milk name, quantity, unit price, amount) plus total/paid/balance footer; applied-payments list (customer payments with `bill_id` — reuse `usePayments({ bill_id })` requires bill filter support: add optional `bill_id` param to `listPayments`/`usePayments` in `api/payments.ts`/`usePayments.ts` or render the bill's payments via `CustomerBillResponse` if the API provides them; fall back to `getBill` response only); status `Select` + "Update Status" `Button` with `ConfirmDialog` (FR-015); if bill has applied payments and target status is `CANCELLED`, show the extra warning that payments remain recorded (FR-016) — use `useUpdateBillStatus`
- [x] T016 [US5] Register `/payments/bills/:id` (BillDetailPage) in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>` — completes the BillListPage row-click navigation (T009)

**Checkpoint**: US5 independently testable — bill detail + status management verified with confirmation.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Access-control verification and full-suite validation of the complete feature.

- [x] T017 [P] Create `frontend/e2e/payments.spec.ts` — follow `delivery.spec.ts`/`token-books.spec.ts` helpers (`ownerAuth`, seeded `milk_management_e2e` DB): (1) setup a delivery session and mark deliveries DELIVERED via the Delivery pages so bill generation has data; (2) record an ADVANCE payment → row appears in history; (3) generate a bill → appears in Bills list with expected total; (4) record BILL_PAYMENT → bill shows PAID and Outstanding reflects it; (5) update bill status to OVERDUE with confirmation; (6) negatives: BILL_PAYMENT without a bill blocked; no-delivery generation creates no bill and explains; (7) CHECKER cannot reach `/payments` (role guard)
- [x] T018 Verify access control (FR-019/SC-006): CHECKER and DELIVERY_PARTNER see no Finance nav and are blocked by RoleGuard on all six payment routes; manual spot-check on `/payments`, `/payments/bills`, `/payments/outstanding`
- [x] T019 Run full verification: `cd frontend && npx tsc -b && npm run lint` + `npx playwright test` (E2E backend on 8001, DB `milk_management_e2e`) — all specs including the existing 32 must pass; fix any regressions
- [x] T020 Run `quickstart.md` flows 1–5 end-to-end; update `quickstart.md`/`contracts/payments-api.md` if observed behavior differs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T003 types, T002 constants); **BLOCKS all user stories**
- **User Stories (Phase 3+)**: All depend on Foundational (T004 API + T005 hooks)
  - US1 → US2 → US3 can be developed in parallel after Foundational (different files); route-registration tasks edit `App.tsx` and MUST run sequentially (T008 → T011 → T013 → T016)
  - US4 (P2) depends on US1 (extends `PaymentListPage.tsx`)
  - US5 (P2) depends on US2 (its detail page is the BillListPage row-click target)
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Foundational T004/T005 — no other story dependency (MVP)
- **User Story 2 (P1)**: Foundational T004/T005 — no other story dependency
- **User Story 3 (P1)**: Foundational T004/T005 — no other story dependency
- **User Story 4 (P2)**: Depends on US1 (same `PaymentListPage.tsx` file)
- **User Story 5 (P2)**: Depends on US2 (navigation target); file itself is independent

### Within Each User Story

- Types before API before hooks before pages (within Phases 1–2)
- Page scaffold before its filters/actions
- Core implementation before integration

### Parallel Opportunities

- T002/T003 (constants + types) run in parallel
- After Foundational, US1 (T006/T007), US2 (T009/T010), US3 (T012) and US5 (T015) page scaffolds are different files and run in parallel
- Route registrations (T008/T011/T013/T016) all edit `App.tsx` — sequential, no [P]
- T017 (E2E spec, new file) runs in parallel with T018

---

## Parallel Example: Payment Pages After Foundational

```bash
Task: "Create PaymentListPage in frontend/src/pages/payments/PaymentListPage.tsx"
Task: "Create BillListPage in frontend/src/pages/payments/BillListPage.tsx"
Task: "Create OutstandingPage in frontend/src/pages/payments/OutstandingPage.tsx"
Task: "Create BillDetailPage in frontend/src/pages/payments/BillDetailPage.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (types + constants)
2. Complete Phase 2: Foundational (API + hooks) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (record payment + history)
4. **STOP and VALIDATE**: `npx tsc -b` + `npm run lint` + manual record-advance/record-bill-payment (SC-001)
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → payment pages can call the backend
2. Add US1 → test independently (record payment + history) → demo (MVP!)
3. Add US2 → test independently (generate + list bills) → demo
4. Add US3 → test independently (outstanding balances) → demo
5. Add US4 → test independently (history filters) → demo
6. Add US5 → test independently (bill detail + status) → demo
7. Final: E2E spec + full-suite verification

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (types, constants, API, hooks are the critical path)
2. Developer A: US1 (PaymentList + PaymentForm + routes)
3. Developer B: US2 (BillList + BillGenerate + routes)
4. Developer C: US3 (Outstanding) then US4 (filters)
5. Developer D: US5 (BillDetail + routes) then E2E spec

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same-file conflicts (all `App.tsx` route tasks and all `PaymentListPage.tsx` tasks MUST be sequential), cross-story dependencies that break independence
