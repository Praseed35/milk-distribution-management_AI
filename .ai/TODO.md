# TODO: Milk Management AI

## Immediate (Required for MVP)

### Security
- [ ] Move hardcoded secrets to environment variables (DB URL, JWT secret)
- [ ] Add `Depends(get_current_user)` to all non-login endpoints
- [ ] Remove `test_kimi.py` or move API key to `.env`
- [ ] Add CORS middleware configuration

### Auth Hardening
- [ ] Enforce role-based access on all endpoints (not just `/auth/owner-dashboard`)
- [ ] Add refresh token mechanism

### Schema Fixes
- [ ] Make `CustomerUpdate` fields optional (currently requires all fields)
- [ ] Add `UserResponse` Pydantic schema
- [ ] Add `EmployeeResponse` Pydantic schema

### Code Cleanup
- [ ] Remove duplicate root `main.py`
- [ ] Remove `app/temp.py`
- [ ] Remove dead code in subscription service (redundant `is_active` checks)

---

## Short-Term (Core Features)

### Employee Module
- [ ] Implement employee CRUD service
- [ ] Implement employee router with all endpoints
- [ ] Add employee tests
- [ ] Link employee to user properly (user_id FK)

### Token Book Module
- [ ] Design TokenBook model (customer, shift, date, quantity, status)
- [ ] Implement token service (issue, collect, carry-forward)
- [ ] Implement token book router
- [ ] Add token book schemas and exceptions
- [ ] Add token book tests

### Milk Allocation Module
- [ ] Design MilkAllocation model (route, milk_type, shift, date, quantity)
- [ ] Implement allocation service
- [ ] Implement allocation router
- [ ] Add tests

### Delivery Module
- [ ] Design Delivery model (subscription, shift, date, quantity_delivered, status)
- [ ] Implement delivery service
- [ ] Implement delivery router
- [ ] Add tests

---

## Medium-Term (Business Logic)

### Cash Sales Module
- [ ] Design CashSale model (milk_type, quantity, amount, date, route)
- [ ] Implement cash sale service and router
- [ ] Add tests

### Reconciliation Module
- [ ] Design Reconciliation model (date, route, subscription, delivered, billed, difference)
- [ ] Implement reconciliation service (compare allocations vs deliveries)
- [ ] Implement reconciliation router
- [ ] Add tests

### Reports Module
- [ ] Implement daily delivery report endpoint
- [ ] Implement customer-wise billing report
- [ ] Implement route-wise summary report
- [ ] Implement milk-type-wise sales report

### Dashboard Module
- [ ] Owner dashboard (total customers, active subscriptions, daily revenue)
- [ ] Checker dashboard (pending verifications, route status)
- [ ] Delivery partner dashboard (today's deliveries, pending stops)

---

## Long-Term (Quality & Scale)

### Database Improvements
- [ ] Add timestamps to `users` and `employees` tables
- [ ] Add indexes on frequently queried columns (route_id, status, customer_code)
- [ ] Add DB-level cascade rules on foreign keys
- [ ] Add NOT NULL constraints where missing

### Code Quality
- [ ] Standardize exception hierarchy (all inherit from `BusinessException`)
- [ ] Standardize service return types (all return ORM models or all return response schemas)
- [ ] Use Pydantic enums in models (replace raw strings for role, status)
- [ ] Add structured logging throughout
- [ ] Add API rate limiting
- [ ] Fix customer code race condition (use DB sequence)

### Testing
- [ ] Add subscription CRUD tests
- [ ] Add employee CRUD tests
- [ ] Add integration tests for auth flow
- [ ] Add test coverage reporting

### Documentation
- [ ] Write README.md with setup, usage, and development instructions
- [ ] Add OpenAPI descriptions to all endpoints
- [ ] Add inline docstrings to all service methods

### DevOps
- [ ] Add Docker Compose for PostgreSQL + app
- [ ] Add CI/CD pipeline
- [ ] Add environment-based configuration (dev/staging/prod)
- [ ] Add health check endpoint

---

## Backlog (Future V2)

- [ ] Mobile app for delivery partners
- [ ] Online payment integration
- [ ] QR code token system
- [ ] Multi-branch support
- [ ] Inventory management
- [ ] Vehicle/fleet management
- [ ] AI-powered demand forecasting
- [ ] Customer notification system (SMS/WhatsApp)
