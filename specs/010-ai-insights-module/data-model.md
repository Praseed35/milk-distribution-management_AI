# Data Model: AI Insights Module

**Date**: 2026-08-05 | **Phase**: Phase 1 (Design & Contracts)

## Design Principle

The AI module is **read-only** — it introduces **no new database tables** and **no Alembic migration**. All AI outputs are **derived entities** computed on request from the existing 17-table schema. Source queries MUST filter `is_active == True` on every soft-deletable table (constitution Principle IV).

## Source Tables Consumed

| Source table | Columns used | Used by |
|---|---|---|
| `delivery_sessions` | `id`, `route_id`, `delivery_date`, `shift`, `status`, `total_milk_loaded`, `total_token_registered`, `total_cash_sales`, `total_returned_milk`, `reconciliation_status`, `is_active` | forecast, anomaly, insights |
| `daily_deliveries` | `id`, `session_id`, `customer_id`, `milk_type_id`, `planned_quantity`, `delivered_quantity`, `delivery_status`, `delivery_date`, `is_active` | forecast, anomaly, churn, insights |
| `subscriptions` | `id`, `customer_id`, `milk_type_id`, `morning_quantity`, `evening_quantity`, `status`, `is_active` | anomaly (expected volume) |
| `delivery_exceptions` | `id`, `subscription_id`, `exception_type`, `start_date`, `end_date`, `status`, `is_active` | anomaly (expected-volume exclusion), churn |
| `customers` | `id`, `customer_code`, `customer_name`, `route_id`, `is_active` | churn, insights (names only — contact fields excluded from LLM payload) |
| `routes` | `id`, `route_code`, `route_name`, `is_active` | forecast, anomaly, insights |
| `milk_types` | `id`, `milk_name`, `is_active` | forecast (milk-type filter) |
| `customer_payments` | `id`, `customer_id`, `amount`, `payment_mode`, `payment_date`, `is_active` | anomaly (payment spike), churn |
| `token_book_payments` | `id`, `amount_paid`, `payment_date`, `is_active` | anomaly (payment spike) |
| `customer_bills` | `id`, `customer_id`, `balance_amount`, `due_date`, `is_active` | churn (aging) |

## Derived Entities (response models, no persistence)

### DemandForecast

| Field | Type | Notes |
|---|---|---|
| `route_id` | int \| null | null = whole business |
| `milk_type_id` | int \| null | optional filter |
| `horizon_days` | int | default 7, 1–30 |
| `date_from` | date | today + 1 |
| `date_to` | date | today + horizon_days |
| `method` | string | "weekday_seasonal_moving_average" |
| `is_sufficient_history` | bool | false when < 14 historical days |
| `message` | string \| null | "insufficient history" notice per FR-003 |
| `total_expected` | float \| null | sum of day predictions (null if insufficient) |
| `low_range` | float \| null | 80% interval lower bound (sum) |
| `high_range` | float \| null | 80% interval upper bound (sum) |
| `items` | list[ForecastDay] | one per forecast day |

**ForecastDay**: `date`, `predicted_quantity`, `low`, `high`, `actual_quantity` (null), `is_sufficient_history`.

### AnomalyReport

| Field | Type | Notes |
|---|---|---|
| `generated_at` | datetime | — |
| `count` | int | len(items) |
| `items` | list[AnomalyItem] | sorted HIGH → LOW, then by date desc |

**AnomalyItem**: `type` (enum: `RECONCILIATION_SHORTAGE`, `UNCLOSED_SESSION`, `DELIVERY_SHORTFALL`, `CONSUMPTION_DROP`, `PAYMENT_SPIKE`, `UNPLANNED_OVERAGE`), `severity` (`HIGH`/`MEDIUM`/`LOW`), `title`, `description`, `entity_type` (`session`/`route`/`customer`/`payment`), `entity_id`, `entity_name`, `metric`, `expected` (float), `actual` (float), `deviation` (float), `occurred_on` (date), `suggested_action` (string).

### ChurnRiskReport

| Field | Type | Notes |
|---|---|---|
| `generated_at` | datetime | — |
| `count` | int | — |
| `items` | list[ChurnRiskItem] | sorted by score desc |

**ChurnRiskItem**: `customer_id`, `customer_code`, `customer_name`, `route_name`, `risk_score` (0–100), `risk_level` (`LOW`/`MEDIUM`/`HIGH`), `factors` (list of {`factor`, `weight`, `contribution`}), `suggested_action` (string).

**Scoring**: declining consumption trend 30% · exception frequency 20% · NOT_DELIVERED/CANCELLED rate 20% · payment recency 15% · outstanding aging 15%. LOW < 40, MEDIUM 40–69, HIGH ≥ 70.

### AIInsightsResponse

| Field | Type | Notes |
|---|---|---|
| `generated_at` | datetime | — |
| `stats_only` | bool | true when LLM unavailable (FR-007) |
| `data_range` | {`from`, `to`} | range the narrative covers |
| `narrative` | string \| null | plain-language LLM summary (null when stats_only) |
| `operational` | dict | today's dashboard numbers (reuses dashboard service) |
| `forecast` | DemandForecast | next-7-day summary |
| `anomalies` | AnomalyReport | top items |
| `churn_risk` | ChurnRiskReport | top items |

### ChatExchange (request/response)

| Field | Type | Notes |
|---|---|---|
| request `message` | string | non-empty, ≤ 2000 chars |
| request `history` | list[{role, content}] | ≤ 8 prior turns |
| response `reply` | string | LLM answer |
| response `data_range` | {`from`, `to`} | range used for the answer |
| response `sources` | list[string] | which reports/sections informed the answer |
| response `stats_only` | bool | false for chat success |

## State Transitions

None. All AI entities are stateless, read-only views recomputed per request. The only stateful element is the in-memory per-user chat rate-limiter (sliding window), which lives in `app/services/ai/chat.py` and is never persisted.
