# Module Map (As of July 29, 2026)

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

## Code Complete but UNTESTED ⚠️ (no test coverage)

```
Token Register ⚠️ (sheet-level ledger, Sprint 4 remaining)
    ↓
Warning Log ⚠️ (alert dashboard, Sprint 4 remaining)
```

## Not Started ❌

```
Token Register ❌ (sheet-level ledger, Sprint 4 remaining)
    ↓
Warning Log ❌ (alert dashboard, Sprint 4 remaining)
    ↓
AI Business Intelligence ❌ (Sprint 8)
    ↓
React Frontend ❌ (Sprint 9)
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
                           └─→ Sprint 8 (AI BI) ❌

Sprint 4 Core (Token Book) ✅ TESTED (independent)

Sprint 9 (Frontend) - needs all backend done
Sprint 10 (Testing & Deployment) - needs everything
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
