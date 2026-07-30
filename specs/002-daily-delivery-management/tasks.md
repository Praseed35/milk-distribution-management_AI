# Tasks: Daily Delivery Management

**Input**: Design documents from `/specs/002-daily-delivery-management/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in feature specification. Skipping test task generation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create delivery domain model files: app/models/delivery_session.py, app/models/daily_delivery.py, app/models/session_edit.py, app/models/token_sheet_warning.py
- [x] T002 Create Pydantic schemas: app/schemas/delivery_session.py, app/schemas/daily_delivery.py, app/schemas/delivery_edit.py
- [x] T003 Create service layer files: app/services/delivery_service.py, app/services/delivery_registration.py, app/services/delivery_reconciliation.py, app/services/delivery_edit_service.py
- [x] T004 Create router files: app/routers/deliveries.py, app/routers/delivery_edit.py
- [x] T005 Create exception files: app/exceptions/delivery.py, app/exceptions/delivery_edit.py
- [x] T006 Add new status constants to app/constants/statuses.py (SessionStatus, DeliveryStatus, DeliverySource, WarningCode)
- [x] T007 Create Alembic migration: alembic/versions/XXXX_create_delivery_tables.py (delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Implement DeliverySession model with all fields, relationships, indexes per data-model.md (app/models/delivery_session.py)
- [x] T009 Implement DailyDelivery model with all fields, relationships, indexes per data-model.md (app/models/daily_delivery.py)
- [x] T010 Implement SessionEdit model with all fields, relationships per data-model.md (app/models/session_edit.py)
- [x] T011 Implement TokenSheetWarning model with all fields, relationships per data-model.md (app/models/token_sheet_warning.py)
- [x] T012 Create Pydantic schemas for DeliverySession (Create, Update, Response) per contracts/sessions.md (app/schemas/delivery_session.py)
- [x] T013 Create Pydantic schemas for DailyDelivery (Create, Update, Response) per contracts/deliveries.md (app/schemas/daily_delivery.py)
- [x] T014 Create Pydantic schemas for SessionEdit and TokenSheetWarning (app/schemas/delivery_edit.py)
- [x] T015 Create domain-specific exceptions: SessionNotFoundError, SessionAlreadyClosedError, SessionNotBalancedError, DispatchAlreadyRecordedError, OwnerRequiredError, ConcurrentEditError, InvalidTokenSheetError, SheetAlreadyUsedError (app/exceptions/delivery.py, app/exceptions/delivery_edit.py)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Daily Delivery List (Priority: P1) 🎯 MVP

**Goal**: System automatically generates delivery lists for each route based on customer subscriptions and exceptions

**Independent Test**: Create subscriptions for customers on a route, add delivery exceptions, verify system generates correct delivery lists for morning/evening shifts

### Implementation for User Story 1

- [x] T016 [US1] Implement DeliveryService.create_session() - creates delivery session with status PLANNED (app/services/delivery_service.py)
- [x] T017 [US1] Implement DeliveryService.generate_delivery_list() - queries active subscriptions minus exceptions for route/shift/date (app/services/delivery_service.py)
- [x] T018 [US1] Implement session validation logic - route_id, employee_id, shift, date constraints (app/services/delivery_service.py)
- [x] T019 [US1] Implement POST /deliveries/sessions endpoint - create session with RBAC (OWNER, CHECKER) (app/routers/deliveries.py)
- [x] T020 [US1] Implement GET /deliveries/sessions endpoint - list sessions with filters (app/routers/deliveries.py)
- [x] T021 [US1] Implement GET /deliveries/sessions/{id} endpoint - get session detail with deliveries (app/routers/deliveries.py)
- [x] T022 [US1] Implement POST /deliveries/sessions/{id}/checklist endpoint - get delivery checklist for partner (app/routers/deliveries.py)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Record Milk Dispatch (Priority: P1)

**Goal**: Record milk dispatched to each delivery partner for each route

**Independent Test**: Create delivery session, record dispatch quantities, verify session status changes from PLANNED to STARTED

### Implementation for User Story 2

- [x] T023 [US2] Implement DeliveryService.record_dispatch() - updates total_milk_loaded and transitions to STARTED status (app/services/delivery_service.py)
- [x] T024 [US2] Add state transition validation - PLANNED → STARTED only (app/services/delivery_service.py)
- [x] T025 [US2] Implement POST /deliveries/sessions/{id}/start endpoint - record dispatch with RBAC (app/routers/deliveries.py)
- [x] T026 [US2] Implement POST /deliveries/sessions/{id}/dispatch endpoint - alternative dispatch recording (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Register Token Sheets During Delivery (Priority: P1)

**Goal**: Register token sheets collected from customers during delivery

**Independent Test**: Register token sheets for delivered customers and verify token book issue's current_sheet count increments correctly

### Implementation for User Story 3

- [x] T027 [US3] Implement DeliveryRegistration.register_token() - validates customer, book, sheet number, registers token (app/services/delivery_registration.py)
- [x] T028 [US3] Implement token sheet validation chain - customer exists, milk type matches, active book exists, sheet within range, not duplicate (app/services/delivery_registration.py)
- [x] T029 [US3] Implement DeliveryRegistration.update_delivery_status() - handles DELIVERED, PENDING_TOKEN, CASH_SALE statuses (app/services/delivery_registration.py)
- [x] T030 [US3] Implement POST /deliveries endpoint - record delivery with token registration (app/routers/deliveries.py)
- [x] T031 [US3] Implement PUT /deliveries/{id} endpoint - update delivery status (app/routers/deliveries.py)
- [x] T032 [US3] Implement POST /deliveries/{id}/register-token endpoint - register token sheet (app/routers/deliveries.py)
- [x] T033 [US3] Implement POST /deliveries/validate-token endpoint - validate token before registration (app/routers/deliveries.py)
- [x] T034 [US3] Implement GET /deliveries/customer/{id}/token-status endpoint - get customer token book status (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Handle Unplanned Deliveries (Priority: P2)

**Goal**: Add customers who weren't on today's schedule but received milk anyway

**Independent Test**: Add unplanned delivery for customer not on schedule and verify it appears in reconciliation

### Implementation for User Story 4

- [x] T035 [US4] Implement DeliveryRegistration.add_unplanned() - creates delivery with source UNPLANNED (app/services/delivery_registration.py)
- [x] T036 [US4] Add validation for unplanned deliveries - customer must exist, session must be active (app/services/delivery_registration.py)
- [x] T037 [US4] Implement POST /deliveries/unplanned endpoint - add unplanned delivery with RBAC (CHECKER) (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Perform Route Reconciliation (Priority: P1)

**Goal**: Reconcile each delivery route by entering cash sales and returned milk

**Independent Test**: Enter cash sales and returned milk amounts, verify system calculates whether route is balanced

### Implementation for User Story 5

- [x] T038 [US5] Implement DeliveryReconciliation.calculate() - computes loaded = token + cash + returned (app/services/delivery_reconciliation.py)
- [x] T039 [US5] Implement DeliveryReconciliation.submit() - accepts cash sales, returned milk, token sheets (app/services/delivery_reconciliation.py)
- [x] T040 [US5] Implement DeliveryReconciliation.validate() - checks if route can be closed (app/services/delivery_reconciliation.py)
- [x] T041 [US5] Implement POST /deliveries/sessions/{id}/reconciliation/submit endpoint - submit reconciliation (app/routers/deliveries.py)
- [x] T042 [US5] Implement GET /deliveries/sessions/{id}/reconciliation endpoint - get current reconciliation (app/routers/deliveries.py)
- [x] T043 [US5] Implement GET /deliveries/sessions/{id}/reconciliation/summary endpoint - get session summary (app/routers/deliveries.py)
- [x] T044 [US5] Implement GET /deliveries/sessions/{id}/reconciliation/customers endpoint - get all customer status (app/routers/deliveries.py)
- [x] T045 [US5] Implement POST /deliveries/sessions/{id}/reconciliation/validate endpoint - validate reconciliation (app/routers/deliveries.py)
- [x] T046 [US5] Implement POST /deliveries/sessions/{id}/reconciliation/cash-sales endpoint - add cash sale (app/routers/deliveries.py)
- [x] T047 [US5] Implement DELETE /deliveries/sessions/{id}/reconciliation/cash-sales/{id} endpoint - remove cash sale (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - Close Delivery Route (Priority: P1)

**Goal**: Close delivery route after reconciliation is balanced and finalize records

**Independent Test**: Verify balanced route can be closed and becomes read-only, unbalanced route cannot be closed

### Implementation for User Story 6

- [x] T048 [US6] Implement DeliveryService.close_session() - validates reconciliation balanced, transitions to CLOSED (app/services/delivery_service.py)
- [x] T049 [US6] Add state transition validation - COMPLETED → CLOSED only if balanced (app/services/delivery_service.py)
- [x] T050 [US6] Implement POST /deliveries/sessions/{id}/close endpoint - close session with RBAC (app/routers/deliveries.py)
- [x] T051 [US6] Implement GET /deliveries/sessions/{id}/report endpoint - generate session report (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1-6 should all work independently (MVP complete!)

---

## Phase 9: User Story 7 - Edit Previous Delivery Session (Priority: P2)

**Goal**: Owner can reopen and edit previous delivery sessions to correct mistakes

**Independent Test**: Close route, reopen it, edit delivery record, return token sheet, verify token book's current_sheet decrements

### Implementation for User Story 7

- [x] T052 [US7] Implement DeliveryEditService.reopen_session() - transitions CLOSED → COMPLETED, increments reopen_count (app/services/delivery_edit_service.py)
- [x] T053 [US7] Implement DeliveryEditService.edit_delivery() - updates delivery with optimistic locking (app/services/delivery_edit_service.py)
- [x] T054 [US7] Implement DeliveryEditService.return_token_sheet() - returns token, decrements current_sheet (app/services/delivery_edit_service.py)
- [x] T055 [US7] Implement session audit logging - creates SessionEdit records for all changes (app/services/delivery_edit_service.py)
- [x] T056 [US7] Implement optimistic locking check - version comparison before update (app/services/delivery_edit_service.py)
- [x] T057 [US7] Implement POST /deliveries/sessions/{id}/reopen endpoint - reopen session with RBAC (OWNER only) (app/routers/delivery_edit.py)
- [x] T058 [US7] Implement PUT /deliveries/{id}/edit endpoint - edit previous delivery with RBAC (OWNER only) (app/routers/delivery_edit.py)
- [x] T059 [US7] Implement GET /deliveries/sessions/{id}/edit-history endpoint - get edit history (app/routers/delivery_edit.py)

**Checkpoint**: At this point, User Stories 1-7 should all work independently

---

## Phase 10: User Story 8 - Handle Non-Sequential Token Sheets (Priority: P2)

**Goal**: Register token sheets not in sequential order with appropriate warnings

**Independent Test**: Register Sheet #5 when #4 hasn't been used yet, verify warning is displayed but registration proceeds

### Implementation for User Story 8

- [x] T060 [US8] Implement non-sequential sheet detection logic - compare current_sheet vs provided sheet (app/services/delivery_registration.py)
- [x] T061 [US8] Implement warning logging - creates TokenSheetWarning records (app/services/delivery_registration.py)
- [x] T062 [US8] Update token registration to accept acknowledged_warnings parameter (app/services/delivery_registration.py)
- [x] T063 [US8] Implement GET /deliveries/{id}/warnings endpoint - get delivery warnings (app/routers/deliveries.py)

**Checkpoint**: At this point, User Stories 1-8 should all work independently

---

## Phase 11: User Story 9 - Handle New Book Before Old Finishes (Priority: P3)

**Goal**: Notify when customer uses new token book while old book still has unused sheets

**Independent Test**: Have two active books for customer, register sheet from new book, verify warning about old book's remaining sheets

### Implementation for User Story 9

- [x] T064 [US9] Implement new book detection logic - check for active old books with remaining sheets (app/services/delivery_registration.py)
- [x] T065 [US9] Implement NEW_BOOK_BEFORE_OLD_FINISHED warning type (app/services/delivery_registration.py)
- [x] T066 [US9] Update customer token status endpoint to show all active books (app/routers/deliveries.py)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T067 [P] Update app/models/__init__.py to import all new delivery models
- [x] T068 [P] Update app/services/__init__.py to import all new delivery services
- [x] T069 [P] Create comprehensive error message constants in app/exceptions/delivery.py
- [x] T070 Add logging throughout delivery services for audit trail
- [x] T071 Verify all endpoints have proper RBAC checks per Constitution Principle II
- [ ] T072 Verify all entities use soft deletes per Constitution Principle IV
- [ ] T073 Run quickstart.md validation scenarios to verify complete workflow

---

## Phase 13: Testing (CRITICAL - Constitution Principle III requires tests for all features)

**Purpose**: Unit tests for all delivery management services (Constitution Principle III)

### Delivery Service Tests
- [ ] T074 Create test_delivery_service.py - test create_session, record_dispatch, close_session
- [ ] T075 Add state transition validation tests - PLANNED→STARTED→COMPLETED→CLOSED
- [ ] T076 Add session validation tests - route, employee, shift, date constraints

### Delivery Registration Tests
- [ ] T077 Create test_delivery_registration.py - test register_token, update_delivery_status, add_unplanned
- [ ] T078 Add token validation chain tests - customer exists, milk type matches, active book, sheet range, not duplicate
- [ ] T079 Add non-sequential sheet warning tests
- [ ] T080 Add new book detection warning tests

### Delivery Reconciliation Tests
- [ ] T081 Create test_delivery_reconciliation.py - test calculate, submit, validate
- [ ] T082 Add balance equation tests - loaded = token + cash + returned
- [ ] T083 Add validation gate tests - route can only close when balanced

### Delivery Edit Tests
- [ ] T084 Create test_delivery_edit_service.py - test reopen_session, edit_delivery, return_token_sheet
- [ ] T085 Add optimistic locking tests - version comparison, ConcurrentEditError
- [ ] T086 Add audit logging tests - SessionEdit records created for all changes

### Router/Endpoint Tests
- [ ] T087 Create test_deliveries_router.py - test all session endpoints (US1-US6)
- [ ] T088 Create test_delivery_edit_router.py - test edit endpoints (US7)
- [ ] T089 Add RBAC enforcement tests - verify 403 for unauthorized roles

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on US3 for token registration
- **User Story 5 (P1)**: Can start after Foundational (Phase 2) - Depends on US2/US3 for delivery data
- **User Story 6 (P1)**: Can start after Foundational (Phase 2) - Depends on US5 for reconciliation
- **User Story 7 (P2)**: Can start after Foundational (Phase 2) - Depends on US6 for session closing
- **User Story 8 (P2)**: Can start after Foundational (Phase 2) - Extends US3 token registration
- **User Story 9 (P3)**: Can start after Foundational (Phase 2) - Extends US3 token registration

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Implement DeliverySession model in app/models/delivery_session.py"
Task: "Implement DailyDelivery model in app/models/daily_delivery.py"

# Launch all endpoints for User Story 1 together:
Task: "Implement POST /deliveries/sessions endpoint in app/routers/deliveries.py"
Task: "Implement GET /deliveries/sessions endpoint in app/routers/deliveries.py"
Task: "Implement GET /deliveries/sessions/{id} endpoint in app/routers/deliveries.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo (Full lifecycle!)
8. Add User Story 7 → Test independently → Deploy/Demo (Edit capability!)
9. Add User Story 8 → Test independently → Deploy/Demo (Edge cases!)
10. Add User Story 9 → Test independently → Deploy/Demo (Complete!)
11. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2
   - Developer B: User Story 3 + User Story 4
   - Developer C: User Story 5 + User Story 6
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Phase 14: Convergence

**Purpose**: Remediate constitution violations and remaining gaps identified during convergence assessment

- [ ] T090 CRITICAL Add `is_active` Boolean column to `app/models/session_edit.py` and create Alembic migration per Constitution IV (Soft Deletes) (contradicts)
- [ ] T091 CRITICAL Add `is_active` Boolean column to `app/models/token_sheet_warning.py` and create Alembic migration per Constitution IV (Soft Deletes) (contradicts)
- [ ] T092 CRITICAL Add `get_current_user` and `require_role` RBAC protection to all endpoints in `app/routers/deliveries.py` matching auth specs in `contracts/sessions.md` and per Constitution II (contradicts)
- [ ] T093 HIGH Write comprehensive delivery test suite across `tests/test_delivery_service.py`, `tests/test_delivery_registration.py`, `tests/test_delivery_reconciliation.py`, `tests/test_delivery_edit_service.py`, `tests/test_deliveries_router.py`, and `tests/test_delivery_edit_router.py` per Constitution III and existing unchecked tasks T074–T089 (missing)
- [ ] T094 MEDIUM Move `SECRET_KEY` from hardcoded value in `app/core/config.py` to environment variable with fallback per Constitution security requirements (contradicts)
- [ ] T095 MEDIUM Run or automate quickstart.md validation scenarios to verify complete delivery workflow per T073 (missing)
