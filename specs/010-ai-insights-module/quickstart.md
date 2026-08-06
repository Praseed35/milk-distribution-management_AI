# Quickstart: AI Insights Module

**Date**: 2026-08-05 | **Phase**: Phase 1 (Design & Contracts)

This guide proves the feature works end-to-end. It references the [API contracts](contracts/ai-endpoints.md) and [data model](data-model.md) instead of duplicating them. Implementation details live in `tasks.md` and the implementation phase.

## Prerequisites

- Backend dependencies installed: `pip install -r requirements.txt`
- Frontend dependencies installed: `cd frontend && npm install`
- Database migrated and seeded: `alembic upgrade head && python -m scripts.seed`
- `.env` contains `NVIDIA_API_KEY=nvapi-...` (already present; optional for statistical-only validation)

## Scenario 1 — Statistical endpoints (no network required)

**Setup**: with the seeded database, log in as the OWNER test user to get a token:

```powershell
$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login" -ContentType "application/json" -Body '{"username":"<owner>","password":"<password>"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
```

**Validate**:

```powershell
# Demand forecast (whole business, next 7 days)
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/forecast?horizon_days=7" -Headers $headers

# Anomaly alerts (last 7 days)
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/anomalies" -Headers $headers

# Churn risk (top 20)
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/churn-risk" -Headers $headers
```

**Expected outcomes**:

- `/forecast` returns `method: "weekday_seasonal_moving_average"`, `horizon_days: 7`, an `items` array with 7 entries, and `total_expected` populated when the seed data has ≥ 14 historical days (otherwise `is_sufficient_history=false` with a `message`).
- `/anomalies` returns any seeded unbalanced/unclosed sessions or consumption drops with `severity`, `expected`, `actual`, and `suggested_action`.
- `/churn-risk` returns customers ordered by `risk_score` descending with `factors`.

## Scenario 2 — RBAC enforcement

**Validate**:

```powershell
# Login as CHECKER, then call the same endpoints
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/ai/forecast" -Headers $checkerHeaders -SkipHttpErrorCheck
```

**Expected outcomes**: HTTP **403** for CHECKER and DELIVERY_PARTNER on all `/ai/*` endpoints; HTTP **401** with no token; OWNER/ADMIN succeed on `forecast`/`anomalies`/`churn-risk`; only OWNER succeeds on `/ai/insights` and `/ai/chat` (ADMIN gets **403** there).

## Scenario 3 — Graceful degradation (no LLM)

**Setup**: stop the LLM path by setting the env var (mirrors `REPORT_CACHE_DISABLED`):

```powershell
$env:AI_LLM_DISABLED = "1"
uvicorn app.main:app --reload --port 8000
```

**Validate**:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/insights" -Headers $headers
Invoke-WebRequest -Method Post -Uri "http://localhost:8000/api/v1/ai/chat" -Headers $headers -ContentType "application/json" -Body '{"message":"Which route collected the most cash?"}' -SkipHttpErrorCheck
```

**Expected outcomes**:

- `/ai/insights` returns HTTP **200** with `stats_only=true` and `narrative=null`, while `operational`, `forecast`, `anomalies`, and `churn_risk` are still populated.
- `/ai/chat` returns HTTP **503** with a clear message.

## Scenario 4 — Live LLM narrative and chat (manual smoke test)

> Requires a reachable NVIDIA endpoint and valid key. Never run in automated CI (tests mock the client and set `AI_LLM_DISABLED=1`).

**Setup**: ensure `NVIDIA_API_KEY` is in the environment and `AI_LLM_DISABLED` is unset. Restart uvicorn.

**Validate**:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/insights?refresh=true" -Headers $headers
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/ai/chat" -Headers $headers -ContentType "application/json" -Body '{"message":"Which route collected the most cash this month?"}'
```

**Expected outcomes**:

- `/ai/insights` returns `stats_only=false` with a non-empty `narrative` that references real seeded figures and the data range.
- `/ai/chat` returns a `reply` naming the correct route/amount and a `data_range`; an out-of-scope question yields a reply stating it cannot be answered from available data.

## Scenario 5 — Frontend page

**Setup**: `cd frontend && npm run dev` (backend on :8000). Log in as OWNER.

**Validate**:

1. Open `http://localhost:5173/reports/ai` (via sidebar: Reports → AI Insights).
2. Confirm the page shows the forecast section (route selector + 7-day bars), anomaly list, churn-risk table, and (when LLM enabled) the AI narrative.
3. Confirm the chat panel answers a question and shows a clear error message when the LLM is disabled.
4. Log in as CHECKER and confirm the AI Insights nav item is hidden and `/reports/ai` redirects/denies access.

**Expected outcomes**: page renders all sections without console errors; RBAC hides the menu item for unauthorized roles.

## Scenario 6 — Automated regression

```powershell
pytest tests/test_ai.py            # new backend tests (statistical, RBAC, degradation, rate limit)
pytest                             # full backend suite stays green
cd frontend
npm run lint                       # oxlint clean
npx playwright test e2e/ai.spec.ts # new E2E (boots isolated :8001 backend, AI_LLM_DISABLED=1)
```

**Expected outcomes**: all new and existing tests pass; no test touches the network.

## Reset after validation

```powershell
python -m scripts.seed             # restore seed data after test runs
```
