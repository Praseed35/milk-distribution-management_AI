# TODO.md - Development Roadmap

> Sprint-based development plan with dependencies and status.

---

## Current State

**Completed**: Sprints 1, 2, and 4 (Core Token Book Management)
**Test Count**: 218 tests passing
**Total Tables**: 10
**Total API Endpoints**: ~40

---

## Sprint Plan

### Sprint 1: Master Data (COMPLETED)
- [x] User management (basic create)
- [x] JWT Authentication (login, me, change-password)
- [x] Route CRUD
- [x] Customer CRUD with auto-generated codes
- [x] Milk Type CRUD
- [x] Employee CRUD with optional user linking
- [x] Role-based access control
- [x] Seed data script

### Sprint 2: Subscriptions + Delivery Exceptions (COMPLETED)
- [x] Subscription CRUD with joined queries
- [x] Subscription deactivation
- [x] Delivery Exception CRUD
- [x] Date overlap detection
- [x] Active subscription/milk type validation
- [x] Subscription by customer endpoint

### Sprint 3: Daily Delivery Management (PLANNED)
**Depends on**: Sprint 1, 2
**Key Features**:
- [ ] Daily delivery session (morning/evening shift)
- [ ] Route-day assignment
- [ ] Delivery checklist generation from active subscriptions
- [ ] Skip/deliver marking per subscription
- [ ] Delivery partner assignment per route per shift
- [ ] Delivery status tracking (DELIVERED, SKIPPED, CANCELLED)
- [ ] Integration with delivery exceptions (auto-skip)

**New Tables Needed**:
- `delivery_sessions` - Daily session per route per shift
- `delivery_items` - Per-subscription delivery record in a session

### Sprint 4 (Remaining): Token Register, Ledger, Warning Log
**Depends on**: Sprint 3, 5
**Key Features**:
- [ ] Token Register - Sheet-by-sheet tracking within a book
- [ ] Token Ledger - Complete token transaction history
- [ ] Warning Log - Alerts for expiring books, unpaid balances

**New Tables Needed**:
- `token_register` - Sheet-level tracking
- `token_ledger` - Transaction log
- `warning_logs` - Warning/alert records

### Sprint 5: Reconciliation (PLANNED)
**Depends on**: Sprint 3
**Key Features**:
- [ ] Daily reconciliation per route/shift
- [ ] Expected vs delivered comparison
- [ ] Cash collection tracking
- [ ] Shortage/surplus detection
- [ ] Reconciliation approval workflow

**New Tables Needed**:
- `reconciliation_sessions` - Daily reconciliation record
- `reconciliation_items` - Per-subscription reconciliation

### Sprint 6: Payment Management (PLANNED)
**Depends on**: Sprint 5
**Key Features**:
- [ ] Customer payment ledger
- [ ] Advance payment tracking
- [ ] Monthly bill generation
- [ ] Payment collection by delivery partner
- [ ] Outstanding balance tracking

### Sprint 7: Reports and Analytics (PLANNED)
**Depends on**: All above sprints
**Key Features**:
- [ ] Route-wise daily/weekly/monthly reports
- [ ] Customer-wise consumption reports
- [ ] Revenue reports
- [ ] Collection efficiency reports
- [ ] Token book utilization reports

### Sprint 8: AI Business Intelligence (PLANNED)
**Depends on**: Sprint 7
**Key Features**:
- [ ] Demand forecasting
- [ ] Customer churn prediction
- [ ] Route optimization suggestions
- [ ] Anomaly detection (unusual orders, payments)

### Sprint 9: Frontend - React (PLANNED)
**Depends on**: All backend
**Key Features**:
- [ ] Owner dashboard
- [ ] Customer management UI
- [ ] Delivery partner mobile app
- [ ] Subscription management
- [ ] Token book tracking
- [ ] Reports dashboard

### Sprint 10: Testing and Deployment (PLANNED)
**Key Features**:
- [ ] Comprehensive test coverage (target: 95%+)
- [ ] API documentation finalization
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment
- [ ] Performance testing
- [ ] Security audit

---

## Immediate Next Steps

1. **Start Sprint 3**: Design daily delivery management tables and APIs
2. **Address tech debt**: Move SECRET_KEY to env, fix exception hierarchy
3. **Add API versioning**: Prefix all routes with `/api/v1`
4. **Add CORS middleware**: Required before frontend work
5. **Add pagination**: For all list endpoints
