---

description: "Task list for Reports and Analytics Module implementation"

---

# Tasks: Reports and Analytics Module

**Input**: Design documents from `specs/003-reports-analytics-module/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/report-endpoints.md, quickstart.md

**Tests**: Included per Constitution Principle III (Test-First Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project at repository root: `app/`, `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the report module directory structure and register the router.

- [X] T001 Create `app/services/reports/` package with empty `__init__.py`
- [X] T002 [P] Register reports router in `app/main.py` — add `from app.routers.reports import router as reports_router` and `app.include_router(reports_router)`
- [X] T003 Add report seed data factories in `tests/conftest.py` — fixture helpers for creating sessions, deliveries, payments, bills, token books for test scenarios

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schemas and service utilities that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Create `app/schemas/reports.py` with shared schemas: `ReportEnvelope`, `DateRangeFilter` (with preset resolution logic: today, yesterday, this_week, last_week, this_month, last_month, this_year), and `ReportPagination` — following existing schema patterns with `model_config = ConfigDict(from_attributes=True)`
- [X] T005 [P] Create `app/services/reports/common.py` with shared helpers: `resolve_date_range()` (converts preset+from_date+to_date to `(date_from, date_to)`), `get_role_restricted_routes()` (filters routes by user role for RBAC), and `generate_csv_response()` (converts list of dicts to CSV `StreamingResponse`)
- [X] T006 [P] Create `app/services/reports/cache.py` with simple in-memory report cache: `ReportCache` class with `get(key)`, `set(key, data, ttl=300)`, and `invalidate(pattern=None)` methods — cache key is `f"{report_type}:{hash(frozenset(params.items()))}"`, supports `?refresh=true` bypass

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Route-Wise Reports (Priority: P1) 🎯 MVP

**Goal**: Business owner can view delivery performance per route — loaded vs delivered vs cash collected vs shortages.

**Independent Test**: Create a session for a known route with 3 customers (2 DELIVERED, 1 CASH_SALE, 6L loaded), call `GET /reports/route-delivery?preset=today&route_id=1`, verify response shows correct quantities and is_balanced=true.

- [X] T007 [P] [US1] Create `RouteDeliveryItem` and `RouteDeliveryReport` response schemas in `app/schemas/reports.py` as defined in data-model.md Section 1
- [X] T008 [US1] Implement `get_route_delivery_report()` in `app/services/reports/route_delivery.py`: query `delivery_sessions` filtered by route_id, delivery_date range, and shift; aggregate `daily_deliveries` by status; compute loaded/delivered/cash/returned/shortage; respect soft deletes; return list of `RouteDeliveryItem`-compatible dicts
- [X] T009 [US1] Implement `GET /reports/route-delivery` endpoint in `app/routers/reports.py`: accepts route_id, preset, from_date, to_date, shift, group_by, format, page, page_size as `Query()` params; calls service; applies RBAC (OWNER/ADMIN/CHECKER all routes, DELIVERY_PARTNER own route only); wraps in `ReportEnvelope`; supports `?format=csv` via `generate_csv_response()`
- [X] T010 [US1] Write tests in `tests/test_reports.py`: test successful route report (single route, all routes, date range, shift filter), test empty data returns zeros, test 401 without auth, test 403 for DELIVERY_PARTNER accessing wrong route, test CSV content-type header

**Checkpoint**: User Story 1 (Route Reports) fully functional and independently testable — this is the MVP.

---

## Phase 4: User Story 2 — Revenue Reports (Priority: P1)

**Goal**: Business owner can view revenue trends broken down by source, payment mode, route, or milk type.

**Independent Test**: Create 2 token book payments (5000 INR) and 3 customer bill payments (3000 INR), call `GET /reports/revenue?preset=this_month`, verify total_revenue=8000 with correct breakdown percentages.

- [X] T011 [P] [US2] Create `RevenueBreakdown` and `RevenueReport` response schemas in `app/schemas/reports.py` as defined in data-model.md Section 2
- [X] T012 [US2] Implement `get_revenue_report()` in `app/services/reports/revenue.py`: union query across `token_book_payments` and `customer_payments` filtered by date range; group by source, payment_mode, route, milk_type via joins through `token_identities`/`subscriptions`/`customers`; compute totals and percentages; return dict matching `RevenueReport` structure
- [X] T013 [US2] Implement `GET /reports/revenue` endpoint in `app/routers/reports.py`: accepts preset, from_date, to_date, route_id, milk_type_id, payment_mode, group_by, format, page, page_size; restricts to OWNER role only (403 for non-OWNER); wraps in `ReportEnvelope`; supports CSV export
- [X] T014 [US2] Write tests in `tests/test_reports.py`: test successful revenue report with multiple sources, test breakdown percentages sum to 100%, test empty date range returns zeros, test 403 for ADMIN/CHECKER accessing revenue, test 401 without auth, test CSV export

**Checkpoint**: User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 — Collection Efficiency Reports (Priority: P2)

**Goal**: Business owner can track billed vs paid vs outstanding per customer with aging breakdown.

**Independent Test**: Create a bill for Customer A (1000 INR) and record a payment (600 INR), call `GET /reports/collection-efficiency?customer_id=1`, verify 60% collection, 400 INR outstanding.

- [X] T015 [P] [US3] Create `CustomerCollectionItem` and `CollectionEfficiencyReport` response schemas in `app/schemas/reports.py` as defined in data-model.md Section 3
- [X] T016 [US3] Implement `get_collection_efficiency_report()` in `app/services/reports/collection.py`: query `customer_bills` grouped by customer summing total_amount; query `customer_payments` (excluding ADVANCE type) grouped by customer summing amount; compute balance, percentage, aging buckets based on due_date vs today; join with `customers` and `routes` for names; respect soft deletes
- [X] T017 [US3] Implement `GET /reports/collection-efficiency` endpoint in `app/routers/reports.py`: accepts preset, from_date, to_date, route_id, min_outstanding, format, page, page_size; roles OWNER/ADMIN; wraps in `ReportEnvelope`; supports CSV
- [X] T018 [US3] Write tests in `tests/test_reports.py`: test successful collection report with partial payment, test 100% and 0% collection scenarios, test aging bucket calculation, test min_outstanding filter, test route filter, test 403 for CHECKER/DELIVERY_PARTNER

**Checkpoint**: User Stories 1-3 independently functional.

---

## Phase 6: User Story 4 — Customer Consumption Reports (Priority: P2)

**Goal**: Owner/admin can see a customer's consumption history with trend detection.

**Independent Test**: Create a customer with a subscription for 2L/day, record 30 days of 2L deliveries, call `GET /reports/customer/1/consumption?preset=this_month`, verify 60L total, 2.0 avg, 30 days with data.

- [X] T019 [P] [US4] Create `ConsumptionDay`, `ConsumptionTrend`, and `CustomerConsumptionReport` response schemas in `app/schemas/reports.py` as defined in data-model.md Section 4
- [X] T020 [US4] Implement `get_customer_consumption_report()` in `app/services/reports/consumption.py`: join `daily_deliveries` to `delivery_sessions` for date; filter by customer_id and date range; group by date/week/month summing delivered_quantity per milk_type; compute total, avg, days_with_data; compute trend by comparing last 7 days avg vs preceding 21 days avg (requires 14+ days data); raise not-found if customer invalid
- [X] T021 [US4] Implement `GET /reports/customer/{customer_id}/consumption` endpoint in `app/routers/reports.py`: path param customer_id, query params preset, from_date, to_date, group_by, format, page, page_size; roles OWNER/ADMIN/CHECKER; wraps in `ReportEnvelope`; supports CSV
- [X] T022 [US4] Write tests in `tests/test_reports.py`: test successful consumption with daily data, test trend detection (increasing/declining/stable), test insufficient data for trend (<14 days), test customer not found (404), test empty date range

**Checkpoint**: User Stories 1-4 independently functional.

---

## Phase 7: User Story 5 — Token Book Utilization Reports (Priority: P3)

**Goal**: Business owner can see token book usage and identify books needing replacement.

**Independent Test**: Create a customer with a token identity, issue a 30-sheet book, record 20 used sheets, call `GET /reports/token-utilization`, verify 20 used, 10 remaining, 66.67% utilization.

- [X] T023 [P] [US5] Create `TokenUtilizationItem` and `TokenUtilizationReport` response schemas in `app/schemas/reports.py` as defined in data-model.md Section 5
- [X] T024 [US5] Implement `get_token_utilization_report()` in `app/services/reports/token_utilization.py`: query `token_identities` joined with `token_book_issues`; compute used sheets from `current_sheet`, remaining from `total_sheets - current_sheet`, utilization %; group by customer; count books below threshold; join with `customers` and `routes` for names; respect soft deletes
- [X] T025 [US5] Implement `GET /reports/token-utilization` endpoint in `app/routers/reports.py`: accepts route_id, customer_id, low_threshold (default 20), format, page, page_size; roles OWNER/ADMIN; wraps in `ReportEnvelope`; supports CSV
- [X] T026 [US5] Write tests in `tests/test_reports.py`: test successful utilization report with mixed book statuses, test low_threshold filter, test empty token books shows zeros, test route filter, test 403 for CHECKER/DELIVERY_PARTNER

**Checkpoint**: User Stories 1-5 independently functional.

---

## Phase 8: User Story 6 — Operational Dashboard (Priority: P3)

**Goal**: Owner gets a single-page overview of today's operations with flagged issues.

**Independent Test**: Create 3 sessions today (2 CLOSED, 1 STARTED) with 20 deliveries (15 DELIVERED, 3 CASH_SALE, 2 PENDING_TOKEN) and 1 unclosed session from yesterday, call `GET /reports/dashboard`, verify session count=3, unclosed=1, deliveries_by_status matches.

- [X] T027 [P] [US6] Create `OperationalDashboard` response schema in `app/schemas/reports.py` as defined in data-model.md Section 6
- [X] T028 [US6] Implement `get_operational_dashboard()` in `app/services/reports/dashboard.py`: count today's sessions; sum loaded milk from today's sessions; aggregate daily_deliveries by status for today; count unclosed sessions from previous days (status != CLOSED and delivery_date < today); identify unbalanced sessions (sessions with reconciliation diff != 0); return dict matching `OperationalDashboard`
- [X] T029 [US6] Implement `GET /reports/dashboard` endpoint in `app/routers/reports.py`: no query params (always today); roles OWNER/ADMIN/CHECKER/DELIVERY_PARTNER; returns `OperationalDashboard` directly (no envelope — single object)
- [X] T030 [US6] Write tests in `tests/test_reports.py`: test successful dashboard with mixed session states, test unclosed session detection, test unbalanced session flagging, test empty day (no sessions) returns zeros, test 401 without auth

**Checkpoint**: All 6 user stories independently functional.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Finalize CSV export, cache integration, database indexes, and validation.

- [X] T031 [P] Add missing database indexes for report performance: create Alembic migration adding indexes on `daily_deliveries.delivery_status`, `customer_payments.payment_date`, and `customer_bills.bill_period_start` if they don't exist
- [X] T032 [P] Integrate report cache (`app/services/reports/cache.py`) into all report endpoint functions — wrap each endpoint with cache check before DB query; respect `?refresh=true` bypass; use TTL of 300s for dashboard/revenue, 60s for others
- [X] T033 Run `pytest tests/test_reports.py -v --tb=short` and fix any failures; verify all ~48-64 tests pass — 24 tests pass
- [ ] T034 Run quickstart.md validation (curl commands against running server with seed data) — requires running server, skipped for automated testing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational completion
  - US1, US2 can proceed in parallel (independent data sources)
  - US3 depends on payment/bill data — no code dependency on US1/US2
  - US4 depends on delivery data — no code dependency on US1/US2
  - US5 depends on token book data — no code dependency on other stories
  - US6 depends on delivery session data — no code dependency
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Route Reports - P1)**: Can start after Foundational — No code dependency on other stories
- **US2 (Revenue - P1)**: Can start after Foundational — No code dependency on other stories
- **US3 (Collection - P2)**: Can start after Foundational — No code dependency
- **US4 (Consumption - P2)**: Can start after Foundational — No code dependency
- **US5 (Token Utilization - P3)**: Can start after Foundational — No code dependency
- **US6 (Dashboard - P3)**: Can start after Foundational — No code dependency

**Key insight**: All 6 user stories are data-independent from each other. They query different primary tables and don't share any mutable state. They all depend only on Phase 2 (shared schemas and helpers).

### Within Each User Story

- Schemas before services
- Services before router endpoints
- Tests alongside implementation (Constitution Principle III)

### Parallel Opportunities

- T001-T002 can run in parallel (different files)
- T004-T006 can run in parallel (schemas, common helpers, cache — different files)
- T007-T010 (US1) can run in parallel with T011-T014 (US2) — completely independent
- All user story phases (Phase 3-8) can run in parallel with different implementers
- T031-T032 can run in parallel (migration, cache integration)

---

## Parallel Example: User Story 1

```bash
# Launch all schemas for User Story 1 together:
Task: "T007 [P] [US1] Create RouteDeliveryItem and RouteDeliveryReport schemas"
Task: "T008 [US1] Implement get_route_delivery_report() in route_delivery.py"

# Then launch endpoint + tests:
Task: "T009 [US1] Implement GET /reports/route-delivery endpoint"
Task: "T010 [US1] Write tests in test_reports.py"
```

## Parallel Example: User Stories 1 + 2 Together

```bash
# Developer A:
Task: "US1: T007 → T008 → T009 → T010"

# Developer B:
Task: "US2: T011 → T012 → T013 → T014"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (Route Reports)
4. **STOP and VALIDATE**: Run `python -m pytest tests/test_reports.py -k "route" -v`
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Route Reports) → Test independently → Deploy (MVP!)
3. Add US2 (Revenue Reports) → Test independently → Deploy
4. Add US3 (Collection Efficiency) → Test independently → Deploy
5. Add US4 (Customer Consumption) → Test independently → Deploy
6. Add US5 (Token Utilization) → Test independently → Deploy
7. Add US6 (Dashboard) → Test independently → Deploy
8. Polish → Final validation with quickstart.md

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done (Phase 2 checkpoint):
   - Developer A: US1 + US4 (route delivery + customer consumption)
   - Developer B: US2 + US3 (revenue + collection efficiency)
   - Developer C: US5 + US6 (token utilization + dashboard)
3. All stories complete and integrate independently since they query different tables

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- No new database tables needed — all reports query existing tables
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Run `pytest tests/test_reports.py` after each phase before moving on
