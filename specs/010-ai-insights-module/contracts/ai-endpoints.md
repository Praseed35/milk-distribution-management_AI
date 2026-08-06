# API Contracts: AI Insights

**Date**: 2026-08-05 | **Phase**: Phase 1 (Design & Contracts)

**Base URL**: All endpoints are prefixed with `/api/v1/ai` and require authentication via `Authorization: Bearer <token>`.

**Content Types**: JSON only (`Accept: application/json`). No CSV export for AI endpoints.

**Error Responses**:

- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient role permissions
- `422 Unprocessable Entity`: Invalid parameter values (e.g., `horizon_days` out of range)
- `429 Too Many Requests`: Chat rate limit exceeded
- `503 Service Unavailable`: LLM service unavailable/disabled for `/ai/chat`

---

## Endpoint: Demand Forecast

```
GET /api/v1/ai/forecast
```

**Roles**: OWNER, ADMIN

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_id` | int | null (all routes) | Filter by route |
| `milk_type_id` | int | null (all types) | Filter by milk type |
| `horizon_days` | int | 7 | 1–30 |
| `refresh` | bool | false | Bypass 300s cache |

**Response (200)**:
```json
{
  "route_id": 1,
  "milk_type_id": null,
  "horizon_days": 7,
  "date_from": "2026-08-06",
  "date_to": "2026-08-12",
  "method": "weekday_seasonal_moving_average",
  "is_sufficient_history": true,
  "message": null,
  "total_expected": 64.5,
  "low_range": 58.1,
  "high_range": 70.9,
  "items": [
    {"date": "2026-08-06", "predicted_quantity": 9.2, "low": 8.3, "high": 10.1, "actual_quantity": null, "is_sufficient_history": true}
  ]
}
```

**Insufficient history**: `is_sufficient_history=false`, `message` = "Insufficient history for a full forecast (need at least 14 days); showing available historical average.", `total_expected`/`items` still populated from the average or empty when no data.

---

## Endpoint: Anomaly Alerts

```
GET /api/v1/ai/anomalies
```

**Roles**: OWNER, ADMIN

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_id` | int | null | Filter by route |
| `days_back` | int | 7 | Look-back window (1–30) |
| `refresh` | bool | false | Bypass 300s cache |

**Response (200)**:
```json
{
  "generated_at": "2026-08-05T10:00:00",
  "count": 2,
  "items": [
    {
      "type": "RECONCILIATION_SHORTAGE",
      "severity": "HIGH",
      "title": "Reconciliation shortage on Downtown Route session",
      "description": "Loaded 10.00L but only 8.00L accounted for.",
      "entity_type": "session",
      "entity_id": 42,
      "entity_name": "Downtown Route / 2026-08-05 / MORNING",
      "metric": "loaded_vs_accounted",
      "expected": 10.0,
      "actual": 8.0,
      "deviation": -2.0,
      "occurred_on": "2026-08-05",
      "suggested_action": "Review token sheets and cash sale entries; reopen the session if needed."
    }
  ]
}
```

---

## Endpoint: Churn Risk

```
GET /api/v1/ai/churn-risk
```

**Roles**: OWNER, ADMIN

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_id` | int | null | Filter by route |
| `limit` | int | 20 | Max customers returned (1–100) |
| `refresh` | bool | false | Bypass 300s cache |

**Response (200)**:
```json
{
  "generated_at": "2026-08-05T10:00:00",
  "count": 1,
  "items": [
    {
      "customer_id": 7,
      "customer_code": "C00007",
      "customer_name": "Ravi Kumar",
      "route_name": "Downtown Route",
      "risk_score": 78,
      "risk_level": "HIGH",
      "factors": [
        {"factor": "declining_consumption", "weight": 30, "contribution": 26},
        {"factor": "missed_deliveries", "weight": 20, "contribution": 15}
      ],
      "suggested_action": "Call the customer to understand the drop and offer a revised plan."
    }
  ]
}
```

---

## Endpoint: AI Business Insights (Narrative)

```
GET /api/v1/ai/insights
```

**Roles**: OWNER only

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset` | string | this_month | today, yesterday, this_week, last_week, this_month, last_month, this_year |
| `from_date` | date | null | Custom start (overrides preset) |
| `to_date` | date | null | Custom end |
| `refresh` | bool | false | Bypass 300s cache AND regenerate narrative |

**Response (200)** — LLM available:
```json
{
  "generated_at": "2026-08-05T10:00:00",
  "stats_only": false,
  "data_range": {"from": "2026-08-01", "to": "2026-08-05"},
  "narrative": "This month the business delivered 885L of milk...",
  "operational": {"total_sessions": 3, "total_milk_delivered": 885.0},
  "forecast": { },
  "anomalies": {"count": 1, "items": []},
  "churn_risk": {"count": 0, "items": []}
}
```

**Response (200)** — LLM unavailable/disabled (`stats_only=true`, `narrative=null`):
```json
{
  "generated_at": "2026-08-05T10:00:00",
  "stats_only": true,
  "data_range": {"from": "2026-08-01", "to": "2026-08-05"},
  "narrative": null,
  "operational": { },
  "forecast": { },
  "anomalies": {"count": 0, "items": []},
  "churn_risk": {"count": 0, "items": []}
}
```

---

## Endpoint: Conversational Q&A

```
POST /api/v1/ai/chat
```

**Roles**: OWNER only

**Request Body**:
```json
{
  "message": "Which route collected the most cash this month?",
  "history": [
    {"role": "user", "content": "How is revenue trending?"},
    {"role": "assistant", "content": "Revenue is up 8% this month compared to last."}
  ]
}
```

**Request Validation**: `message` non-empty, ≤ 2000 chars; `history` ≤ 8 turns.

**Response (200)**:
```json
{
  "reply": "Downtown Route collected ₹12,400 this month (Aug 1–5, 2026), the most of any route.",
  "data_range": {"from": "2026-08-01", "to": "2026-08-05"},
  "sources": ["revenue_by_route", "route_delivery"],
  "stats_only": false
}
```

**Errors**:

- `429 Too Many Requests`: `{"detail": "Too many requests. Please wait a minute and try again."}` (default 20/min per user)
- `503 Service Unavailable`: `{"detail": "AI service is currently unavailable. Please try again later."}` (LLM down or `AI_LLM_DISABLED=1`)

---

## LLM Payload PII Rules (applies to all endpoints that call the LLM)

The server-side payload builder (`app/services/ai/llm_payload.py`) MUST:

1. Send only aggregated structures (totals, top-N route/customer names, counts, anomaly items, risk items).
2. Strip `customers.primary_phone`, `customers.alternate_phone`, `customers.address` before serialization.
3. Prefix the user prompt with the exact data range so the LLM always states its coverage.
4. Instruct the model to answer "I cannot answer that from the available data" when the question is out of scope.

## Cache Behavior

- `forecast`, `anomalies`, `churn-risk`: cached 300s via `report_cache`, keyed by user + filters; `?refresh=true` bypasses. `REPORT_CACHE_DISABLED=1` disables (already handled by `CACHE_ENABLED`).
- `insights`: cached 300s; `?refresh=true` recomputes both statistics and narrative.
- `chat`: never cached; per-user sliding-window rate limit applies.
