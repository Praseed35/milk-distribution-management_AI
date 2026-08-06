---

description: "Task list for AI Insights Module (backend + frontend, hybrid predictive + LLM)"

---

# Tasks: AI Insights Module

**Input**: Design documents from `/specs/010-ai-insights-module/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/ai-endpoints.md, quickstart.md

**Tests**: Backend `pytest` (`tests/test_ai.py` new; constitution Principle III requires auth/401/403/422/404 coverage). Frontend `cd frontend && npm run build && npm run lint` per checkpoint, plus `frontend/e2e/ai.spec.ts` Playwright coverage (runs with `AI_LLM_DISABLED=1` — no test ever hits the network).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## ⚠️ Phase Reordering Note

The spec lists US1 (AI narrative, P1) first, but per `plan.md` + `contracts/ai-endpoints.md` the `/ai/insights` response **aggregates** the forecast, anomaly, and churn-risk outputs. US1 is therefore phased **after** US2/US3/US4 so each story stays independently implementable and testable. Execution order: **US2 → US3 → US4 → US1 → US5**. Story labels ([US1]…[US5]) still map to the spec stories for traceability. MVP slice = **US2 (demand forecast)**.

## Path Conventions

- Backend: `app/routers/`, `app/services/ai/`, `app/schemas/`, `app/exceptions/`, `app/core/`
- Frontend: `frontend/src/...` (React SPA — `types → api → hooks → pages`)
- Mirror existing conventions: reports module (`app/services/reports/*`, `app/routers/reports.py`, `tests/test_reports.py`), payments frontend (`types/payment.ts`, `api/payments.ts`, `hooks/usePayments.ts`)
- No DB schema changes — **no Alembic migration**

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Baseline verification and cross-cutting config/exceptions. No project initialization needed.

- [x] T001 Verify backend baseline: run `pytest` from repo root — all 379 existing tests must pass before feature work starts
- [x] T002 [P] Add AI settings to `app/core/config.py` — call `load_dotenv()` and read env vars: `NVIDIA_BASE_URL` (default `https://integrate.api.nvidia.com/v1`), `NVIDIA_API_KEY` (from `.env`), `NVIDIA_MODEL` (default `meta/llama-3.3-70b-instruct`), `AI_ENABLED` (default `true`), `AI_CHAT_MAX_TOKENS` (default `700`), `AI_CHAT_MAX_REQUESTS_PER_MINUTE` (default `20`), `AI_LLM_DISABLED` (`1` forces LLM off, mirrors `REPORT_CACHE_DISABLED`) (research R3)
- [x] T003 [P] Create `app/exceptions/ai.py` — `AIUnavailableError` (503), `AIRateLimitError` (429), `AIInsufficientDataError` (422) extending `BusinessException` with `self.status_code`, mirroring the `app/exceptions/delivery_edit.py` pattern (research R13)

**Checkpoint**: `pytest` green; config exposes AI settings; exception classes importable.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared backend AI plumbing (LLM client, payload builder, schemas, router scaffold) and frontend foundation (types/api/hooks/page/route). **⚠️ CRITICAL**: No user story can work until this phase completes.

- [x] T004 [P] Create `app/services/ai/__init__.py` and `app/services/ai/client.py` — `httpx`-based NVIDIA NIM client: `chat_completion(messages: list[dict], max_tokens: int | None = None) -> str` POSTing to `NVIDIA_BASE_URL + "/chat/completions"` with `Authorization: Bearer <NVIDIA_API_KEY>`, `model=NVIDIA_MODEL`, `temperature=0.2`; `timeout=30`; returns `choices[0].message.content`; raises `AIUnavailableError` on timeout/connection error/non-2xx; `is_available() -> bool` honoring `AI_LLM_DISABLED`/missing key (research R1/R2/R10)
- [x] T005 [P] Create `app/services/ai/llm_payload.py` — `build_insights_context(...)` and `build_chat_context(...)` returning plain dicts of **aggregated** data only; MUST strip `Customer.primary_phone`, `alternate_phone`, `address` before serialization; MUST inject the `data_range` into the system prompt and instruct out-of-scope questions to answer "I cannot answer that from the available data" (research R11)
- [x] T006 [P] Create `app/schemas/ai.py` — Pydantic v2 schemas matching `data-model.md` exactly: `DataRange`, `ForecastDay`, `DemandForecast`, `AnomalyItem`, `AnomalyReport`, `ChurnRiskItem`, `ChurnRiskReport`, `AIInsightsResponse`, `ChatMessage`, `ChatRequest` (with `Field(min_length=1, max_length=2000)` on `message`, `history` ≤ 8), `ChatResponse` (Principle V)
- [x] T007 [P] Create `app/routers/ai.py` — `router = APIRouter(prefix="/ai", tags=["AI"])` plus a module helper `_cache_key(report_type, params)` wrapping `report_cache._make_key` (research R7); register the router in `app/main.py` under the `api_v1` umbrella ONLY (no legacy root duplicate, per `plan.md`); endpoints are added in later story phases
- [x] T008 [P] Create `frontend/src/types/ai.ts` — interfaces mirroring `app/schemas/ai.py` exactly (snake_case): `DataRange`, `ForecastDay`, `DemandForecast`, `AnomalyItem`, `AnomalyReport`, `ChurnRiskItem`, `ChurnRiskReport`, `AIInsightsResponse`, `ChatMessage`, `ChatRequest`, `ChatResponse`; plus params interfaces `ForecastParams` (`route_id?`, `milk_type_id?`, `horizon_days?`, `refresh?`), `AnomalyParams` (`route_id?`, `days_back?`, `refresh?`), `ChurnRiskParams` (`route_id?`, `limit?`, `refresh?`), `InsightsParams` (`preset?`, `from_date?`, `to_date?`, `refresh?`); reuse `ReportPreset` from `types/reports.ts`
- [x] T009 [P] Create `frontend/src/api/ai.ts` — fetchers returning `response.data`, mirroring `api/reports.ts`: `getForecast(params?)` (GET `/ai/forecast`), `getAnomalies(params?)` (GET `/ai/anomalies`), `getChurnRisk(params?)` (GET `/ai/churn-risk`), `getInsights(params?)` (GET `/ai/insights`), `sendChatMessage(body)` (POST `/ai/chat`)
- [x] T010 Create `frontend/src/hooks/useAI.ts` — TanStack Query hooks mirroring `useReports.ts`: `useForecast(params?)`, `useAnomalies(params?)`, `useChurnRisk(params?)`, `useInsights(params?)` (each key includes params so `refresh` re-fetches), and `useChat()` as a `useMutation` that surfaces the API error detail (429/503 message) to the UI
- [x] T011 Create `frontend/src/pages/reports/AIInsightsPage.tsx` — `PageHeader` "AI Insights" + placeholder section containers (forecast, anomalies, churn, narrative, chat) that will render per-story components; `LoadingSpinner`/`EmptyState` handling; register `/reports/ai` in `frontend/src/App.tsx` wrapped in `<RoleGuard roles={["OWNER","ADMIN"]}>`; add nav item `{ label: "AI Insights", path: "/reports/ai", roles: ["OWNER","ADMIN"] }` under the Reports menu in `frontend/src/config/permissions.ts`

**Checkpoint**: `cd frontend && npx tsc -b` passes; backend imports cleanly; `/api/v1/ai` router registered; user story implementation can begin.

---

## Phase 3: User Story 2 - Demand Forecasting (Priority: P1) 🎯 MVP

**Goal**: Owner views next-7-day milk demand forecast per route (and overall) with expected total and a low–high range (spec US2; FR-002/FR-003).

**Independent Test**: Seed 4+ weeks of known `daily_deliveries.delivered_quantity` for a route; `GET /api/v1/ai/forecast?route_id=<id>` returns 7 `items`, `total_expected`, `low_range`, `high_range`; with <14 days history it returns `is_sufficient_history=false` + message. Frontend `/reports/ai` shows the forecast section with bars.

### Implementation for User Story 2

- [x] T012 [US2] Implement `app/services/ai/forecast.py` — query `DeliverySession.delivery_date` + `DailyDelivery.delivered_quantity` (join, `is_active=True`, `delivery_status IN ("DELIVERED","CASH_SALE")`, optional `route_id`/`milk_type_id`, `delivery_date >= today-90`) aggregated per date; compute per-day prediction for next `horizon_days` (default 7, 1–30): same-weekday average over last 4 occurrences blended (0.3) with 14-day trailing average, plus capped linear-trend term (±25%), interval ±1.28σ of recent residuals (80%); `<14` historical days → `is_sufficient_history=false` with message and available average (research R4)
- [x] T013 [US2] Implement `GET /ai/forecast` in `app/routers/ai.py` — query params `route_id?`, `milk_type_id?`, `horizon_days` (ge=1 le=30, default 7), `refresh`; `Depends(require_role(["OWNER","ADMIN"]))`; `report_cache` 300s keyed by user+filters; `milk_type_id` that doesn't exist → 404 (mirror delivery_edit `MilkTypeNotFoundError`); return `DemandForecast`
- [x] T014 [US2] Add tests in `tests/test_ai.py` (class `TestForecast`) — deterministic forecast values with a seeded 4-week weekly-seasonal series; insufficient-history path; route/milk-type filtering; 401 (no token), 403 (CHECKER + DELIVERY_PARTNER headers from conftest), 422 (`horizon_days=0` and `=31`)
- [x] T015 [US2] Create `frontend/src/components/ai/ForecastSection.tsx` — route `Select` (`useRoutes`, All routes) + horizon `Input` (1–30, default 7); `useForecast(params)`; 7-day bar list reusing the `UtilizationBar` visual language (bar width ∝ predicted quantity), `total_expected`/`low_range`/`high_range` summary line, insufficient-history notice; wire into the forecast container on `AIInsightsPage`

**Checkpoint**: US2 independently testable — forecast endpoint returns exact seeded math; frontend renders bars (SC-002).

---

## Phase 4: User Story 3 - Anomaly and Exception Alerts (Priority: P2)

**Goal**: Owner sees prioritized anomaly alerts with severity, expected-vs-actual, and suggested action (spec US3; FR-004).

**Independent Test**: Seed a session with `reconciliation_status="UNBALANCED"`, a past unclosed session, and a customer with a >25% consumption drop; `GET /api/v1/ai/anomalies` returns matching items with correct `severity`/`expected`/`actual`/`suggested_action`; empty state when none exist.

### Implementation for User Story 3

- [x] T016 [US3] Implement `app/services/ai/anomaly.py` — rule + z-score checks per research R5: `RECONCILIATION_SHORTAGE` (HIGH, today `reconciliation_status=="UNBALANCED"`), `UNCLOSED_SESSION` (MEDIUM, `delivery_date<today` and `status!="CLOSED"`), `DELIVERY_SHORTFALL` (MEDIUM, route daily delivered <75% of subscription-expected within `days_back`, exceptions excluded), `CONSUMPTION_DROP` (LOW/MEDIUM, customer recent-7 avg <75% of prior-21 avg reusing the `consumption.py` trend pattern), `PAYMENT_SPIKE` (LOW, per-customer z-score >3 on `customer_payments`/`token_book_payments` amounts), `UNPLANNED_OVERAGE` (LOW); each returns an `AnomalyItem` dict; module-level thresholds; optional `route_id` filter + `days_back` window (1–30)
- [x] T017 [US3] Implement `GET /ai/anomalies` in `app/routers/ai.py` — query params `route_id?`, `days_back` (ge=1 le=30, default 7), `refresh`; `Depends(require_role(["OWNER","ADMIN"]))`; `report_cache` 300s; items sorted HIGH→MEDIUM→LOW then date desc; return `AnomalyReport`
- [x] T018 [US3] Add tests in `tests/test_ai.py` (class `TestAnomalies`) — each of the six anomaly types fires with correct severity + numeric expected/actual; empty state (`count=0`); route filter; 401/403/422 (`days_back=0`/`=31`)
- [x] T019 [US3] Create `frontend/src/components/ai/AnomalyList.tsx` — severity badges (HIGH red / MEDIUM amber / LOW blue using `getStatusColor`-style classes), title, expected-vs-actual, `suggested_action`, empty state "No anomalies detected"; wire into the anomalies container on `AIInsightsPage`

**Checkpoint**: US3 independently testable — seeded anomalies surface with correct severity/numbers (SC-003).

---

## Phase 5: User Story 4 - Customer Churn Risk (Priority: P2)

**Goal**: Owner sees a churn-risk list with score (0–100), level, contributing factors, and suggested action (spec US4; FR-005).

**Independent Test**: Seed a declining-consumption customer (>25% drop), a customer with repeated exceptions/missed deliveries, and a steady customer; `GET /api/v1/ai/churn-risk` ranks them with factors consistent with history.

### Implementation for User Story 4

- [x] T020 [US4] Implement `app/services/ai/churn.py` — weighted rule score per research R6: declining consumption trend (30%), delivery-exception frequency (20%), NOT_DELIVERED/CANCELLED rate (20%), payment recency (15%), outstanding aging from `customer_bills.balance_amount`/`due_date` (15%); risk level LOW <40 / MEDIUM 40–69 / HIGH ≥70; per-customer `factors` list (`factor`, `weight`, `contribution`) + `suggested_action`; optional `route_id` filter, `limit` (1–100, default 20); excludes inactive customers
- [x] T021 [US4] Implement `GET /ai/churn-risk` in `app/routers/ai.py` — query params `route_id?`, `limit` (ge=1 le=100, default 20), `refresh`; `Depends(require_role(["OWNER","ADMIN"]))`; `report_cache` 300s; items sorted by `risk_score` desc; return `ChurnRiskReport`
- [x] T022 [US4] Add tests in `tests/test_ai.py` (class `TestChurnRisk`) — declining-consumption customer scores HIGH with `declining_consumption` factor; exception/missed-delivery customer elevated; aging factor present; steady customer LOW; route filter + limit; 401/403/422 (`limit=0`/`=101`)
- [x] T023 [US4] Create `frontend/src/components/ai/ChurnRiskTable.tsx` — customer (code + name), route, `risk_score` bar (reuse `UtilizationBar`), `risk_level` badge, factors list, `suggested_action`; empty state "No customers at risk"; wire into the churn container on `AIInsightsPage`

**Checkpoint**: US4 independently testable — churn list ranks seeded customers correctly (SC-004).

---

## Phase 6: User Story 1 - AI-Generated Business Insights (Priority: P1)

**Goal**: Owner sees a plain-language AI narrative of the business plus today's operational stats and the aggregated forecast/anomaly/churn sections; degrades to `stats_only=true` when the LLM is unavailable (spec US1; FR-001/FR-007/FR-009). **Depends on US2/US3/US4 service modules** (created above).

**Independent Test**: With LLM mocked, `GET /api/v1/ai/insights` returns a narrative referencing seeded totals + `stats_only=false`; with `AI_LLM_DISABLED=1` it returns `stats_only=true`, `narrative=null`, sections still populated.

### Implementation for User Story 1

- [x] T024 [US1] Implement `app/services/ai/insights.py` — orchestration: gather `dashboard.get_operational_dashboard`, `revenue.get_revenue_report`, `route_delivery.get_route_delivery_report` (existing services) plus `forecast.forecast_demand`, `anomaly.get_anomalies`, `churn.get_churn_risk` (US2–US4); call `llm_payload.build_insights_context` → `client.chat_completion` → `narrative`; on `AIUnavailableError`/`AI_LLM_DISABLED` return `stats_only=true`, `narrative=null` with all sections intact (research R9/R10/R11)
- [x] T025 [US1] Implement `GET /ai/insights` in `app/routers/ai.py` — query params `preset?`, `from_date?`, `to_date?`, `refresh`; `Depends(require_role(["OWNER"]))` (revenue in narrative); `resolve_date_range` from `app/services/reports/common.py`; `report_cache` 300s keyed by user+filters; returns `AIInsightsResponse` (200 even in stats-only mode)
- [x] T026 [US1] Add tests in `tests/test_ai.py` (class `TestInsights`) — monkeypatch `client.chat_completion` → narrative present, `stats_only=false`; force `AIUnavailableError`/`AI_LLM_DISABLED` → `stats_only=true`, `narrative=null`, HTTP 200; capture the payload passed to the mocked client and assert it contains NO phone/address values (PII check, FR-009); OWNER 200, ADMIN 403, CHECKER 403, unauthenticated 401; 422 on invalid date
- [x] T027 [US1] Create `frontend/src/components/ai/InsightNarrative.tsx` — renders `narrative` as plain paragraphs (no markdown lib), a `data_range` badge ("Aug 1–5, 2026"), and when `stats_only=true` a clear "AI explanations unavailable — showing statistics" notice; wire into the narrative container on `AIInsightsPage`

**Checkpoint**: US1 independently testable — narrative renders for OWNER with real seeded figures; stats-only fallback verified (SC-001, SC-005).

---

## Phase 7: User Story 5 - Conversational Q&A (Priority: P3)

**Goal**: Owner asks plain-language questions and receives answers derived from system data with a stated data range; rate-limited; graceful 503 when LLM down (spec US5; FR-006/FR-010).

**Independent Test**: With client mocked, `POST /api/v1/ai/chat` answers a question about a seeded route's cash collection and returns `data_range` + `sources`; 20+ rapid requests → 429; LLM down → 503.

### Implementation for User Story 5

- [x] T028 [US5] Implement `app/services/ai/chat.py` — in-memory sliding-window `RateLimiter` (per user, `AI_CHAT_MAX_REQUESTS_PER_MINUTE` default 20 → `AIRateLimitError` 429) + `answer_question(db, user_id, message, history)` that maps the question to relevant report context (revenue by route, route_delivery, collection efficiency), truncates `history` to last 8 turns, calls `llm_payload.build_chat_context` → `client.chat_completion` (capped at `AI_CHAT_MAX_TOKENS`), returns reply + `data_range` + `sources`; raises `AIUnavailableError` on LLM failure (research R8)
- [x] T029 [US5] Implement `POST /ai/chat` in `app/routers/ai.py` — `ChatRequest` body; `Depends(require_role(["OWNER"]))`; rate-limit check → 429; `AIUnavailableError` → 503 with clear message; `ChatResponse`; never cached
- [x] T030 [US5] Add tests in `tests/test_ai.py` (class `TestChat`) — mocked client: correct reply + `data_range` + `sources`; rate limit exceeded → 429; LLM unavailable → 503; 422 (empty message, message >2000 chars, history >8 turns); 401/403
- [x] T031 [US5] Create `frontend/src/components/ai/ChatPanel.tsx` — message list (user/assistant), input + send (disabled while pending), keeps local conversation history sent via `ChatRequest.history`, error toast on 429/503 using the existing toast pattern; wire into the chat container on `AIInsightsPage`

**Checkpoint**: US5 independently testable — chat answers with sources; 429/503 handled (SC-006).

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: RBAC/nav verification, regression gates, E2E coverage, docs, and quickstart validation across all five stories.

- [x] T032 Verify RBAC + nav matrix: `frontend/src/config/permissions.ts` hides "AI Insights" for CHECKER/DELIVERY_PARTNER; `App.tsx` RoleGuard (`OWNER`,`ADMIN`) matches backend `require_role` on forecast/anomalies/churn and OWNER-only on insights/chat; confirm 403 behavior end-to-end
- [x] T033 Run `pytest` from repo root — full suite green (379 existing + new `tests/test_ai.py`). Note: 432 passed incl. all `tests/test_ai.py` (53); the only failures are pre-existing `scripts/test_subscriptions.py` connection errors (require a live server; fail identically on clean baseline)
- [x] T034 [P] Run `cd frontend && npm run build && npm run lint` — must pass clean (tsc -b + vite build + oxlint warning-free)
- [x] T035 Create `frontend/e2e/ai.spec.ts` — Playwright E2E booting the isolated backend via `scripts/e2e_backend.py` (add `AI_LLM_DISABLED=1` alongside its existing `REPORT_CACHE_DISABLED=1`): forecast section renders seeded bars, anomalies/churn render, narrative section shows stats-only notice, chat shows 503 error state, CHECKER sees no nav item and is denied at `/reports/ai`; run with `cd frontend && npm run test:e2e`
- [x] T036 Validate `specs/010-ai-insights-module/quickstart.md` scenarios 1–6 (statistical endpoints, RBAC, degradation, live LLM smoke, frontend page, regression); run `python -m scripts.seed` afterward to restore seed data
- [x] T037 Update `.ai/` docs — `TODO.md` (mark Sprint 8 AI BI started/complete), `PROJECT_CONTEXT.md`, `API_REFERENCE.md` (add 5 endpoints), `current_state.md`, `TECH_DEBT.md` (note `AI_LLM_DISABLED` env; cache-invalidation caveat for AI endpoints)

**Checkpoint**: All five stories working; build/lint/pytest/E2E green; quickstart validated; docs updated.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–7)**: All depend on Foundational; each independently testable
- **Polish (Phase 8)**: Depends on all user stories

### User Story Dependencies

- **US2 (P1)**: Foundational only — no other story dependency (**MVP slice**)
- **US3 (P2)**: Foundational only — no other story dependency
- **US4 (P2)**: Foundational only — no other story dependency
- **US1 (P1)**: Foundational **+ US2/US3/US4** service modules (insights response aggregates them) — phased after them per the reordering note
- **US5 (P3)**: Foundational only — no other story dependency

### Within Each User Story

- Service module before its router endpoint (same `app/routers/ai.py` file across stories — sequential, no [P])
- Tests in `tests/test_ai.py` after the endpoint exists (same file across stories — sequential)
- Frontend component after backend endpoint, then wired into `AIInsightsPage.tsx`

### Parallel Opportunities

- T002/T003 (config + exceptions) run in parallel
- T004–T009 (client, payload, schemas, router scaffold, frontend types, frontend api) are different files — run in parallel
- T010 (hooks) and T011 (page + App.tsx route + permissions.ts) sequential after T008/T009
- After Foundational, the statistical services T012/T016/T020 (different files) can run in parallel; their router endpoints T013/T017/T021 all edit `app/routers/ai.py` — sequential
- T024 (insights.py) can start as soon as US2–US4 service modules land
- T034 (build/lint) can run parallel to T033/T035; T036/T037 last

---

## Parallel Example: Statistical Services After Foundational

```bash
Task: "Implement app/services/ai/forecast.py (US2)"
Task: "Implement app/services/ai/anomaly.py (US3)"
Task: "Implement app/services/ai/churn.py (US4)"
Task: "Create frontend/src/types/ai.ts + frontend/src/api/ai.ts + frontend/src/hooks/useAI.ts (US2-5 foundation)"
```

---

## Implementation Strategy

### MVP First (User Story 2 Only)

1. Complete Phase 1: Setup (config + exceptions)
2. Complete Phase 2: Foundational (client, payload, schemas, router, frontend types/api/hooks/page) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 2 (demand forecast backend + frontend section)
4. **STOP and VALIDATE**: `pytest tests/test_ai.py` + `cd frontend && npm run build` + quickstart Scenario 1
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → AI plumbing ready
2. Add US2 → test independently (forecast) → demo (MVP!)
3. Add US3 → test independently (anomalies) → demo
4. Add US4 → test independently (churn) → demo
5. Add US1 → test independently (narrative + stats-only fallback) → demo
6. Add US5 → test independently (chat) → demo
7. Final: RBAC/nav check, pytest, build/lint, E2E, quickstart, `.ai/` docs

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (config, client, payload, schemas, router, frontend foundation are the critical path)
2. Developer A: US2 (forecast) → US1 (insights narrative, after US2–US4 modules land)
3. Developer B: US3 (anomalies) → US4 (churn)
4. Developer C: frontend foundation (types/api/hooks/page/route) → per-story components → ChatPanel (US5)
5. Developer D: `app/routers/ai.py` endpoint additions (sequential) + Phase 8 polish

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to the spec user story for traceability
- Each user story is independently completable and testable
- All `app/routers/ai.py` and `tests/test_ai.py` tasks MUST be sequential (same file)
- `app/main.py` registered once (T007) — do not add legacy root duplicates for AI
- No Alembic migration — read-only feature over existing tables
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
