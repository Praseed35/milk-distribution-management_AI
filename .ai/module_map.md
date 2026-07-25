# Module Map (As of July 26, 2026)

## Implemented Modules ✅

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
```

## Planned Modules ❌ (Dependency Order)

```
Daily Delivery Management ❌ (Sprint 3)
    ↓
Token Register ❌ (Sprint 4 remaining, needs Daily Delivery)
    ↓
Token Ledger ❌ (Sprint 4 remaining, needs Sprint 3 + 5)
    ↓
Warning Log ❌ (Sprint 4 remaining, needs Sprint 3 + 5)
    ↓
Reconciliation ❌ (Sprint 5, needs Daily Delivery)
    ↓
Payment Management ❌ (Sprint 6, needs Reconciliation)
    ↓
Reports & Analytics ❌ (Sprint 7, needs all above)
    ↓
AI Business Intelligence ❌ (Sprint 8)
    ↓
React Frontend ❌ (Sprint 9)
```

## Dependency Graph

```
Sprint 1 (Master Data)
  └─→ Sprint 2 (Subscriptions + Exceptions)
       └─→ Sprint 3 (Daily Delivery)
            ├─→ Sprint 4 remaining (Token Register, Ledger, Warning)
            └─→ Sprint 5 (Reconciliation)
                 └─→ Sprint 6 (Payment Management)
                      └─→ Sprint 7 (Reports)
                           └─→ Sprint 8 (AI BI)

Sprint 4 Core (Token Book) ✅ (independent, completed)

Sprint 9 (Frontend) - needs all backend complete
Sprint 10 (Testing & Deployment) - needs everything
```

## Database Table Relationships

```
users ──────────────────────┐
                             │
routes ──────────────┐      │
    │                 │      │
    │            customers   │
    │                 │      ├── employees.user_id
    │            subscriptions│
    │                 │      │
    │            delivery_exceptions
    │
    ├── token_identities ──────────┐
    │                 │             │
    │            token_book_issues  │
    │                 │             │
    │            token_book_payments│
    │                              └── collected_by → users.id
    │
    └── employees.route_id
```
