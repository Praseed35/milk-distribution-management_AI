# Module Map (As of August 4, 2026 — verified against source)

## Tested Modules ✅ (with test coverage)

```
Authentication ✅
    ↓
Users ✅
    ↓
Routes ✅
    ↓
Customers ✅
    ↓
Milk Types ✅
    ↓
Employees ✅ (linked to User + Route)
    ↓
Subscriptions ✅ (links Customer → MilkType, shift quantities)
    ↓
Delivery Exceptions ✅ (modifies Subscription for date ranges)
    ↓
Token Identities ✅ (links Customer → MilkType → Token Number)
    ↓
Token Book Issues ✅ (issues books to TokenIdentity, sheet tracking)
    ↓
Token Book Payments ✅ (records payments for book issues)
    ↓
Daily Delivery Management ✅ (Sprint 3: sessions, deliveries, tokens)
    ↓
Reconciliation ✅ (Sprint 5: loaded vs token vs cash vs returned)
    ↓
Payment Management ✅ (Sprint 6: bills, payments, outstanding)
    ↓
Reports & Analytics ✅ (Sprint 7: 6 report types, CSV, cache, RBAC)
```

## Implemented ✅ (Sprint 8 AI BI, specs/010)

```
AI Business Intelligence ✅ (Sprint 8, specs/010 — backend + frontend + E2E T035 + quickstart T036)
    app/services/ai/:
        forecast.py → GET /ai/forecast   (weekday-seasonal moving average, OWNER/ADMIN)
        anomaly.py  → GET /ai/anomalies  (deterministic z-score checks, OWNER/ADMIN)
        churn.py    → GET /ai/churn-risk (score 0-100, LOW/MEDIUM/HIGH, OWNER/ADMIN)
        insights.py → GET /ai/insights   (LLM narrative + stats; stats_only fallback, OWNER only)
        chat.py     → POST /ai/chat      (Q&A over business data; per-user rate limit, OWNER only)
        client.py   → LLM client (AI_LLM_DISABLED-aware; default mock provider)
        llm_payload.py → prompt/context builders for insights + chat
        cache.py    → 300s per-user TTL cache on AI GETs (?refresh=true bypasses)
    frontend/src:
        api/ai.ts + hooks/useAI.ts + types/ai.ts → components/ai/* (5) → pages/reports/AIInsightsPage.tsx (/reports/ai, OWNER/ADMIN)
    tests/test_ai.py → 87 tests (forecast, anomalies, churn, insights, chat + RBAC + degradation + edge cases)
```

## Not Started ❌

> **Correction (Aug 4, 2026)**: Token Register and Warning Log were previously listed as "Code Complete but UNTESTED ⚠️". Verified against source — **no service or router exists** for either (only the `token_sheet_warnings` TABLE is created/populated during delivery registration). They are NOT implemented.

```
Token Register ❌ (sheet-level ledger, Sprint 4 remaining — not started)
    ↓
Warning Log ❌ (alert dashboard, Sprint 4 remaining — table exists, no API/UI)
    ↓
AI route optimization suggestions ❌ (deferred — not in specs/010 scope)
    ↓
Frontend Phase 8 ❌ (Polish & Testing — Phases 1-7 + AI Insights complete ✅)
```

## Frontend Reports API Module (Phase 7 ✅ IMPLEMENTED)

```
Frontend reports module (specs/009, commit 4489d6a)
    frontend/src/api/reports.ts — consumes all 6 backend /reports/* endpoints:
        getDashboard                 → GET /reports/dashboard
        getRouteDelivery             → GET /reports/route-delivery
        getRevenue                   → GET /reports/revenue
        getConsumption(customerId)   → GET /reports/customer/{customerId}/consumption
        getTokenUtilization          → GET /reports/token-utilization
        getCollectionEfficiency      → GET /reports/collection-efficiency
        downloadReportCsv(path, params, filename) → ?format=csv blob + anchor download
    consumers: hooks/useReports.ts (TanStack Query, refresh in query keys) → pages/reports/*
```

## Dependency Graph (Actual)

```
Sprint 1 (Master Data) ✅ TESTED
  └─→ Sprint 2 (Subscriptions + Exceptions) ✅ TESTED
       └─→ Sprint 3 (Daily Delivery) ✅ TESTED
            ├─→ Sprint 4 remaining (Token Register, Warning) ❌
            └─→ Sprint 5 (Reconciliation) ✅ TESTED
                 └─→ Sprint 6 (Payment Management) ✅ TESTED
                      └─→ Sprint 7 (Reports) ✅ TESTED
                           └─→ Sprint 8 (AI BI) ✅ TESTED (specs/010, 87 tests; E2E T035 + quickstart T036 done)

Sprint 4 Core (Token Book) ✅ TESTED (independent)

Sprint 9 (Frontend Phases 1–2) ✅ COMMITTED (d14589b4)
Sprint 10 (Frontend Phases 3–4) ✅ COMMITTED (f536667f)
Phase 5 (Delivery Management) ✅ IMPLEMENTED (specs/007 all tasks [X])
Phase 6 (Payment Management) ✅ IMPLEMENTED (specs/008 all tasks [X])
Phase 7 (Reports Pages) ✅ IMPLEMENTED (specs/009 all tasks [X], commit 4489d6a)
  └─ Phase 8 (Polish & Testing) ❌ PENDING
Sprint 11 (Testing & Deployment) - needs everything
```

## Database Table Relationships (Complete)

```
users ──────────────────────────────────────────┐
  │                                              │
  ├──< Employee (user_id)                       │
  ├──< TokenBookPayment (collected_by)          │
  ├──< DeliverySession (reopened_by)            │
  ├──< DailyDelivery (added_by, last_edited_by) │
  └──< SessionEdit (edited_by)                  │
                                                 │
Route ───────────────────────────────────────────┤
  │                                              │
  ├──< Customer (route_id) ──< Subscription     │
  │     │                    └──> MilkType       │
  │     ├──< TokenIdentity ──> MilkType          │
  │     ├──< TokenBookIssue ──> MilkType         │
  │     ├──< DailyDelivery ──> MilkType          │
  │     └──< TokenBookIssue (customer_id)        │
  │                                              │
  ├──< Employee (route_id)                      │
  ├──< DeliverySession (route_id)               │
  │     │                                       │
  │     ├──< DailyDelivery (session_id)          │
  │     │     ├──< TokenSheetWarning (delivery) │
  │     │     └──< SessionEdit (delivery_id)    │
  │     └──< SessionEdit (session_id)           │
  │                                              │
  └──< DeliverySession (delivery_partner_id)    │
                                                 │
TokenIdentity ───< TokenBookIssue ───< TokenBookPayment
                    │        └──< DailyDelivery
                    │        └──< TokenSheetWarning
```
