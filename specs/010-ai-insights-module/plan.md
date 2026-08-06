# Implementation Plan: AI Insights Module

**Branch**: `010-ai-insights-module` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/010-ai-insights-module/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

The owner gets an **AI Insights dashboard** in the existing reporting area that combines a deterministic statistical layer (7-day demand forecast per route, anomaly alerts, customer churn-risk scoring — all computed offline from existing tables) with an LLM layer (NVIDIA NIM hosted, OpenAI-compatible endpoint using the unused `NVIDIA_API_KEY` in `.env`) that produces plain-language business narratives and answers natural-language questions about the data. The backend adds an `app/services/ai/` package plus an `app/routers/ai.py` under `/api/v1/ai/*`; the frontend adds a new `/reports/ai` page following the existing `types → api → hooks → pages` pattern. LLM features degrade gracefully to statistical-only mode when the external service is unavailable; CHECKER/DELIVERY_PARTNER are denied; financial narratives and chat are OWNER-only. No new dependencies, no DB schema changes, no Alembic migration.

## Technical Context

**Language/Version**: Python 3.10+ (`str | None` syntax) — matches codebase; TypeScript 6.0 / React 19.2 frontend.

**Primary Dependencies**: FastAPI 0.138, SQLAlchemy 2.0.51, Pydantic 2.13 (v2 features). **No new pip/npm dependencies**: LLM calls use `httpx` 0.28.1 (already pinned); env loading uses `python-dotenv` 1.2.2 (already pinned). Frontend reuses TanStack Query v5, axios, Tailwind v4.

**Storage**: PostgreSQL (`milk_managemen_ai`) — **read-only**; no new tables, no migrations. Reads `delivery_sessions`, `daily_deliveries`, `subscriptions`, `delivery_exceptions`, `customers`, `routes`, `milk_types`, `customer_payments`, `token_book_payments`, `customer_bills`.

**Testing**: Backend `pytest` (379 existing tests; new `tests/test_ai.py`). Frontend Playwright E2E (45 existing specs; new `frontend/e2e/ai.spec.ts`). No AI test may hit the network — the LLM client is monkeypatched and `AI_LLM_DISABLED=1` is forced in E2E.

**Target Platform**: Local web app — FastAPI backend on `:8000`, Vite frontend on `:5173` (proxy `/api` → backend); Playwright E2E uses `scripts/e2e_backend.py` on `:8001` with isolated `milk_management_e2e` DB.

**Project Type**: web-service (FastAPI REST API) + SPA (React 19/Vite).

**Performance Goals**: AI summary narrative within 10s (spec SC-001); forecast within 5s (SC-002); chat answer within 15s (SC-006). Statistical endpoints cache 300s via the existing in-memory `report_cache`.

**Constraints**: External LLM may be unavailable → graceful degradation (spec FR-007/SC-005); never send customer contact PII to the LLM (FR-009); per-user chat rate limit + `max_tokens` cap (FR-010); no new libraries without justification (constitution).

**Scale/Scope**: Small single-business ERP (17 tables, ~85 existing endpoints). One new router with 5 endpoints, one new page, ~5 new components. Forecast horizon configurable (default 7 days).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Layered Architecture**: AI computation lives in `app/services/ai/`; `app/routers/ai.py` handles HTTP only; `app/schemas/ai.py` defines Pydantic contracts; `app/exceptions/ai.py` for domain errors; config in `app/core/config.py`. Frontend follows `types → api → hooks → pages`.
- [x] **RBAC**: All 5 endpoints behind `get_current_user` + `require_role`. Forecast/anomalies/churn → OWNER+ADMIN; insights narrative + chat → OWNER only; CHECKER/PARTNER → 403.
- [x] **Schema-Driven Contracts**: Dedicated request/response Pydantic v2 schemas in `app/schemas/ai.py` (`ConfigDict`, `Field` constraints); responses exclude contact fields.
- [x] **Soft Deletes**: All source queries filter `is_active == True`; no hard deletes involved (read-only feature).
- [x] **Tech Stack**: FastAPI/SQLAlchemy/Pydantic/PostgreSQL only; `httpx` + `python-dotenv` already pinned. No new dependencies.
- [x] **Testing**: `tests/test_ai.py` covers success, 401, 403 (role matrix), 422, rate-limit 429, and degradation paths; `frontend/e2e/ai.spec.ts` covers page render, RBAC nav, chat error state.
- [x] **Security**: API key and config externalized via env (`load_dotenv()` added to `config.py`); no credentials hardcoded; aggregated-only LLM payloads.
- [x] **Migrations**: No schema changes → no Alembic migration required.

## Project Structure

### Documentation (this feature)

```text
specs/010-ai-insights-module/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — design decisions R1–R13
├── data-model.md        # Phase 1 output — derived entities + source tables
├── quickstart.md        # Phase 1 output — validation guide
├── contracts/           # Phase 1 output — API contracts
│   └── ai-endpoints.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── core/
│   └── config.py            # [EDIT] add load_dotenv() + AI_* settings
├── exceptions/
│   └── ai.py                # [NEW] AIUnavailableError, AIRateLimitError, etc.
├── schemas/
│   └── ai.py                # [NEW] forecast/anomaly/churn/insight/chat schemas
├── services/
│   └── ai/                  # [NEW] mirrors app/services/reports/
│       ├── __init__.py
│       ├── client.py        # [NEW] httpx NVIDIA NIM client (R1, R2)
│       ├── forecast.py      # [NEW] R4 statistical forecast
│       ├── anomaly.py       # [NEW] R5 rule + z-score anomalies
│       ├── churn.py         # [NEW] R6 weighted risk scoring
│       ├── insights.py      # [NEW] R9/R10 orchestration + LLM narrative
│       ├── chat.py          # [NEW] R8 Q&A + rate limiter
│       └── llm_payload.py   # [NEW] R11 aggregated payload builder + PII strip
├── routers/
│   └── ai.py                # [NEW] /ai/* endpoints, RBAC, caching
└── main.py                  # [EDIT] register ai_router under api_v1 only

tests/
└── test_ai.py               # [NEW] statistical + RBAC + degradation tests

frontend/
├── e2e/
│   └── ai.spec.ts           # [NEW] Playwright E2E
└── src/
    ├── types/ai.ts          # [NEW]
    ├── api/ai.ts            # [NEW]
    ├── hooks/useAI.ts       # [NEW]
    ├── components/ai/       # [NEW]
    │   ├── ForecastSection.tsx
    │   ├── AnomalyList.tsx
    │   ├── ChurnRiskTable.tsx
    │   ├── InsightNarrative.tsx
    │   └── ChatPanel.tsx
    ├── pages/reports/AIInsightsPage.tsx  # [NEW]
    ├── App.tsx              # [EDIT] /reports/ai route + RoleGuard
    └── config/permissions.ts # [EDIT] nav item under Reports
```

**Structure Decision**: Backend uses the established single-project FastAPI layout (`app/routers`, `app/services`, `app/schemas`, `app/exceptions`, `app/core`) with a new `app/services/ai/` subpackage that mirrors the existing `app/services/reports/` package structure (submodule per capability + `common` helpers). Frontend uses the established `types → api → hooks → pages/components` layering. Legacy root-level route registration in `app/main.py` is **not** extended to the AI router (new endpoints get the `/api/v1` prefix only — the legacy duplicates are deprecated).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. No justification required. (The `app/services/ai/` subpackage mirrors the existing `app/services/reports/` precedent — this is not new complexity.)
