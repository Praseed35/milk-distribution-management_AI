# Research: AI Insights Module

**Date**: 2026-08-05 | **Phase**: Phase 0 (Outline & Research)

This document resolves every design decision for the AI Insights module. Each entry records the decision, the rationale, and the alternatives considered. All decisions were verified against the existing codebase (FastAPI 0.138 / SQLAlchemy 2.0 / Pydantic 2.13 / PostgreSQL / React 19 + Vite, 379 pytest + 45 Playwright tests).

---

## R1. LLM Provider and Client Library

**Decision**: Use the NVIDIA NIM hosted inference endpoint (`https://integrate.api.nvidia.com/v1`, OpenAI-compatible `POST /v1/chat/completions`, `Authorization: Bearer nvapi-...`) through a thin **`httpx`**-based client. **No new Python dependency.**

**Rationale**:
- `httpx` 0.28.1 is already pinned in `requirements.txt`; the call is a single JSON POST.
- The endpoint's request/response schema is a standard Chat Completions payload (`messages`, `model`, `temperature`, `max_tokens`) — trivially representable with a small wrapper and easy to monkeypatch in tests.
- The `.env` already contains `NVIDIA_API_KEY` (currently unused), so the provider fits the project with zero configuration work for the owner.
- The constitution requires explicit approval before adding libraries; avoiding a dependency is the most compliant choice.

**Alternatives considered**:
- `openai` Python SDK — cleaner streaming API, but adds a dependency for one POST.
- `langchain` / `llama-index` — heavyweight orchestration frameworks, unjustified for a single endpoint.
- Self-hosted NIM container — same OpenAI-compatible surface, requires GPU infrastructure; documented as a future swap via `base_url` env var.

**Details**: client module wraps `httpx.post` with `timeout=30`, maps HTTP errors to `AIUnavailableError`; `model` configurable via env (default `meta/llama-3.3-70b-instruct`), `temperature=0.2`, `max_tokens` configurable (default 700 for chat). Streaming (`stream=True` + SSE) is deferred to a follow-up; v1 uses non-streaming responses.

---

## R2. LLM Model Choice

**Decision**: `meta/llama-3.3-70b-instruct`, configurable via `NVIDIA_MODEL` env var.

**Rationale**:
- Confirmed available in the NVIDIA NIM hosted catalog with strong instruction-following and summarization quality.
- Small data payloads (aggregate report summaries) fit comfortably within its context window.
- Configurable default means the owner can switch models (e.g., a Nemotron model) without code changes.

**Alternatives considered**: `nvidia/llama-3.1-nemotron-70b-instruct` (fine too, kept as a documented alternative), `nvidia/llama-3.1-nemotron-super-49b-v1` (higher quality, higher cost/latency).

---

## R3. Configuration and Environment Loading

**Decision**: Extend `app/core/config.py` with `load_dotenv()` and AI settings: `NVIDIA_BASE_URL`, `NVIDIA_API_KEY`, `NVIDIA_MODEL`, `AI_ENABLED`, `AI_CHAT_MAX_TOKENS`, `AI_CHAT_MAX_REQUESTS_PER_MINUTE`.

**Rationale**:
- The constitution requires secrets/config via environment variables or `app/core/config.py`; currently `config.py` holds only `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and no `load_dotenv()` exists anywhere in the app (the `.env` file is not currently auto-loaded by the backend).
- `python-dotenv` 1.2.2 is already pinned in `requirements.txt`.
- Existing env-driven settings use `os.getenv(...)` (e.g., `app/database.py`, `app/services/reports/cache.py` `REPORT_CACHE_DISABLED`); AI settings follow the same pattern with `load_dotenv()` at import time in `config.py`.

**Alternatives considered**: a separate `app/core/settings.py` with `pydantic-settings` (pydantic-settings is already pinned, but the project's existing convention is plain `os.getenv`); a dedicated `.env.ai` file (unnecessary).

---

## R4. Demand Forecasting Method

**Decision**: Deterministic **day-of-week seasonal average blended with a recent moving average and linear trend**, with a residual-based 80% prediction interval. No ML library.

**Rationale**:
- Daily milk demand has strong weekly seasonality (weekday vs weekend) — a simple moving average ignores this; per-weekday averaging captures it without training.
- Data volume is small (single-business ERP, weeks-to-months of history), so SARIMA/Prophet-style models cannot be fit reliably and would add heavy dependencies (`statsmodels` ~60MB) that the constitution restricts.
- Deterministic math means unit tests can assert exact numbers, matching the project's test-first, exactness culture (reports "accurate to within 0.01 units", SC-006 of spec 003).

**Method (specified for implementation)**:
1. Query `delivery_sessions.delivery_date` + `daily_deliveries.delivered_quantity` (+ `route_id`/`milk_type_id` filters, `is_active=True`, status IN (`DELIVERED`,`CASH_SALE`)), aggregated per date.
2. For each target day `d` (next `horizon` days, default 7): take the average of the same weekday over the last `k=4` occurrences (fall back to fewer if unavailable); blend with the 14-day trailing average (weight 0.3) to damp single-week anomalies.
3. Add a linear trend term computed from the last 14 days (slope × offset), capped so the forecast cannot exceed ±25% of the blended baseline.
4. Prediction interval = blended value ± `1.28 × σ_residuals` where σ is the std-dev of recent daily forecast residuals (80% interval).
5. If fewer than 14 historical days exist: return the available daily average with `is_sufficient_history=false` and the message text, per spec FR-003.

**Alternatives considered**: `statsmodels` SARIMA (insufficient data + dependency), Facebook Prophet (dependency + overkill), pure linear regression trend (ignores weekly seasonality), last-value persistence (too naive).

---

## R5. Anomaly Detection Method

**Decision**: **Rule-based checks first (deterministic, testable) with z-score statistics for volume/payment outliers.** Severity: HIGH / MEDIUM / LOW.

**Rationale**: Rules map 1:1 to business facts already stored in the DB (reconciliation status, session status, subscription expected quantities, consumption trend) and are exactly testable. z-scores catch volume/payment outliers that rules cannot enumerate. Unsupervised models (isolation forest, LOF) need more data and `scikit-learn` — rejected.

**Anomaly types** (each becomes a schema `AnomalyItem`):
1. **RECONCILIATION_SHORTAGE** (HIGH) — session `reconciliation_status == "UNBALANCED"` today; shows `total_milk_loaded` vs sum delivered+returned.
2. **UNCLOSED_SESSION** (MEDIUM) — session `delivery_date < today` with `status != "CLOSED"` and `is_active=True`; suggests closing/investigating.
3. **DELIVERY_SHORTFALL** (MEDIUM) — route daily delivered volume >25% below subscription-expected volume (active subscriptions × morning+evening, exception-excluded, reusing the delivery checklist logic) within the last 7 days.
4. **CONSUMPTION_DROP** (LOW/MEDIUM) — per-customer recent-7-day average < 75% of prior-21-day average (reuses the trend computation pattern in `app/services/reports/consumption.py`).
5. **PAYMENT_SPIKE** (LOW) — a single `customer_payments`/`token_book_payments` amount with z-score > 3 relative to that customer's 90-day history.
6. **UNPLANNED_OVERAGE** (LOW) — route daily volume >25% above expected (potential unplanned cash sales pattern).

**Thresholds** are module-level constants (easy to tune), and each item carries `expected`, `actual`, `deviation`, `suggested_action`.

---

## R6. Churn-Risk Scoring Method

**Decision**: **Deterministic weighted rule score** (0–100) with risk levels LOW (<40) / MEDIUM (40–69) / HIGH (≥70).

**Weights**: consumption trend change 30%, delivery-exception frequency 20%, NOT_DELIVERED/CANCELLED rate 20%, payment recency 15%, outstanding balance aging 15%.

**Rationale**: Each factor maps to existing tables (`daily_deliveries`, `delivery_exceptions`, `customer_payments`, `customer_bills`), is deterministic, and is independently assertable in tests (spec stories 4.1–4.4). No ML needed — this is a weighted heuristic, transparent and explainable to the owner (factors are surfaced in the response).

**Alternatives considered**: logistic regression on engineered features (needs labeled churn data that does not exist), survival analysis (overkill).

---

## R7. Caching

**Decision**: Reuse the existing `report_cache` singleton (`app/services/reports/cache.py`). TTL: forecast/anomalies/churn = 300s; insights narrative = 300s; chat = never cached. Respect the existing `REPORT_CACHE_DISABLED=1` env (already honored by `CACHE_ENABLED`).

**Rationale**: No new cache layer; consistent with the reports module; `invalidate()` already available for future write-path invalidation. The same caveat as the existing reports cache applies (no automatic invalidation on writes) — acceptable for v1 and consistent with the current reports behavior documented in TECH_DEBT.

---

## R8. Chat Rate Limiting and Guardrails

**Decision**: Per-user **in-memory sliding-window rate limit** (default 20 requests / 60 s → HTTP 429) in the router/service layer; response `max_tokens` capped (default 700); conversation history window limited to the last 8 messages.

**Rationale**: No Redis in the stack; single-process uvicorn makes in-memory limiting sufficient. The constitution does not mandate a specific limiter; TECH_DEBT #14 already flags the absence of rate limiting, and this feature specifically needs protection (external API cost exposure).

**Alternatives considered**: Redis-based limiter (new infra), `slowapi` (new dependency — rejected to stay lean).

---

## R9. Role-Based Access Control

**Decision**:
- `GET /ai/forecast`, `GET /ai/anomalies`, `GET /ai/churn-risk` → `require_role(["OWNER", "ADMIN"])`.
- `GET /ai/insights` and `POST /ai/chat` → `require_role(["OWNER"])` only (insights narrative includes revenue figures; chat can return financial data on request).
- CHECKER and DELIVERY_PARTNER → 403 on all AI endpoints.

**Rationale**: Matches spec FR-008 and mirrors the existing reports RBAC (revenue is OWNER-only at `app/routers/reports.py`). Financial narratives must not leak to CHECKER/PARTNER.

---

## R10. Graceful Degradation / Feature Flag

**Decision**: Add `AI_ENABLED` (default from presence of `NVIDIA_API_KEY`) and `AI_LLM_DISABLED=1` env to force LLM off (mirrors `REPORT_CACHE_DISABLED`). When the LLM is unavailable/disabled/misconfigured:
- `GET /ai/insights` → 200 with `stats_only=true`, `narrative=null`, all statistical sections intact.
- `POST /ai/chat` → 503 with a clear error body.
- Statistical endpoints (forecast/anomalies/churn) → always work, no LLM dependency.

**Rationale**: Spec FR-007 / SC-005. The dashboard must never break because the external service is down.

---

## R11. Security and PII Minimization

**Decision**: The LLM payload builder accepts only **aggregated** data: totals, top-N route/customer names, summary counts, anomaly/risk items without contact fields (address, phones, alternate numbers). A dedicated `build_llm_payload(...)` strips `Customer.primary_phone`, `alternate_phone`, `address` before serialization. Chat context is built from the same aggregated structures. The server never forwards raw query rows.

**Rationale**: Spec FR-009 / Constitution security requirements. Customer contact details are sensitive; the LLM needs no more than names + numbers to answer.

---

## R12. Frontend Approach

**Decision**: No new frontend dependencies. One new page `AIInsightsPage` at `/reports/ai` (OWNER/ADMIN) reusing `KpiCard`, `UtilizationBar`, `PresetFilter` visual language and the existing `types → api → hooks → pages` layering. Narrative rendered as plain paragraphs (no markdown library). Forecast rendered as Tailwind bars/tables (no chart library).

**Rationale**: The frontend deliberately has no chart library; reports pages already render charts as Tailwind-styled bars/tables. Adding `recharts`/`react-markdown` would deviate from the established visual system and add bundles for marginal benefit in v1.

**Alternatives considered**: `recharts` (richer charts, new dependency), `react-markdown` (narratives are plain paragraphs — unnecessary), `@tanstack/react-query` already present for data fetching.

---

## R13. Testing Strategy

**Decision**: Backend unit tests in `tests/test_ai.py` using existing `conftest.py` fixtures; LLM client monkeypatched so **no test ever hits the network**. CI/E2E forces `AI_LLM_DISABLED=1`. Frontend E2E in `frontend/e2e/ai.spec.ts` using the existing Playwright setup (`scripts/e2e_backend.py` on :8001, `milk_management_e2e` DB).

**Rationale**: Spec/Constitution test-first (Principle III). Tests cover: statistical exactness (forecast math, anomaly rule outputs, churn weights), RBAC (401 unauthenticated, 403 CHECKER/PARTNER, 200 OWNER/ADMIN), graceful degradation (LLM disabled → stats-only), payload PII stripping (no phone/address in sent payload), rate limit 429, and frontend rendering + chat error state.

**Alternatives considered**: live LLM integration tests (flaky, costs credits — rejected; a manual smoke command is provided in `quickstart.md` instead).
