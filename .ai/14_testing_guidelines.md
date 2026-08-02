# Testing Guidelines

## Purpose

This document defines the testing standards for the Milk Distribution Management System.

Testing ensures that business workflows, APIs, authentication, and database operations behave correctly and continue working as the project evolves.

Every new feature should include appropriate tests.

---

# Testing Philosophy

The goal of testing is to verify business behavior rather than implementation details.

Tests should be

- Reliable
- Repeatable
- Independent
- Easy to understand
- Fast

A passing test should provide confidence that the business requirement is satisfied.

---

# Testing Pyramid

The project follows the testing pyramid.

```
            Integration Tests
                   ▲
              API Tests
                   ▲
             Service Tests
                   ▲
             Unit Tests
```

Business logic should primarily be tested at the Service Layer.

---

# Project Test Structure

```
tests/

├── unit/
│
├── services/
│
├── api/
│
├── integration/
│
├── fixtures/
│
└── conftest.py
```

Every business module should have corresponding tests.

---

# What to Test

Every new feature should verify

- Happy path
- Validation failures
- Business rule violations
- Permission checks
- Database persistence
- Error responses

---

# Router Testing

Routers should verify

- Status codes
- Response schema
- Authentication
- Authorization
- Request validation

Routers should NOT test business logic.

Business logic belongs in service tests.

---

# Service Testing

Every service should verify

- Business validation
- Database changes
- Transactions
- Exception handling
- Business workflows

Examples

Customer creation

Token book issuance

Cash sale recording

Payment recording

Route reconciliation

---

# Database Testing

Verify

- Records are created
- Records are updated
- Relationships are maintained
- Foreign keys work
- Constraints are enforced
- Rollbacks work correctly

---

# Authentication Testing

Verify

- Login success
- Login failure
- Invalid password
- Invalid JWT
- Expired JWT
- Refresh token
- Protected endpoints
- Role permissions

---

# Customer Module Tests

Example scenarios

✔ Create customer

✔ Update customer

✔ Disable customer

✔ Duplicate customer

✔ Invalid route

✔ Customer not found

---

# Route Module Tests

Verify

- Route creation

- Route update

- Customer assignment

- Inactive routes

- Route deletion policy

---

# Token Book Tests

Verify

- Book creation

- Exactly 30 sheets generated

- Duplicate token number rejected

- Token usage

- Token reuse prevented

- Lost book workflow

---

# Delivery Tests

Verify

- Delivery creation

- Invalid customer

- Invalid route

- Completed delivery cannot change

- Multiple deliveries

- Delivery history

---

# Cash Sale Tests

Verify

- Cash sale creation

- Invalid quantity

- Invalid amount

- Daily totals

- Reconciliation impact

---

# Payment Tests

Verify

- Full payment

- Partial payment

- Advance payment

- Outstanding balance update

- Payment history

---

# Reconciliation Tests

Verify

Loaded Milk

=

Delivered Milk

+

Cash Sales

+

Returned Milk

Test

Balanced route

Unbalanced route

Duplicate reconciliation

Route closing

---

# API Testing

Verify

- Correct status code

- Response model

- Validation errors

- Authentication

- Authorization

- Pagination

- Filtering

- Searching

- Sorting

---

# Exception Testing

Every custom exception should be tested.

Example

```
CustomerNotFound

↓

404
```

```
TokenAlreadyUsed

↓

409
```

```
RouteInactive

↓

400
```

---

# Transaction Testing

Verify rollback.

Example

Issue Token Book

↓

Create Book

↓

Create Sheets

↓

Failure

↓

Rollback

↓

No partial data

---

# Test Data

Use isolated test data.

Avoid depending on production-like data.

Each test should prepare only the data it requires.

---

# Fixtures

Use fixtures for reusable setup.

Examples

- Test database session
- Test user
- Owner account
- Checker account
- Delivery partner
- Customer
- Route
- Token book

Fixtures should remain independent.

---

# Mocking

Mock only external dependencies.

Examples

- SMS service
- Email service
- WhatsApp notifications
- Payment gateway

Do not mock the database when testing business workflows.

---

# Coverage Goals

Recommended minimum coverage

Overall

80%

Critical modules

90%+

Critical modules include

- Authentication
- Token books
- Deliveries
- Reconciliation
- Payments

Coverage is a guide, not the primary objective.

Business correctness is more important than a percentage.

---

# Regression Testing

Whenever a bug is fixed

1. Add a failing test.
2. Fix the bug.
3. Ensure the new test passes.
4. Ensure existing tests continue to pass.

Every bug fix should increase test coverage.

---

# Performance Testing

Large datasets should verify

- Customer listing
- Route reports
- Daily reports
- Reconciliation
- Search
- Pagination

Avoid N+1 query problems.

---

# AI Checklist

Before writing tests

✔ Identify the business workflow

✔ Test success scenarios

✔ Test failure scenarios

✔ Test permissions

✔ Test database persistence

✔ Test exceptions

✔ Test rollback behavior

Never

- Test implementation details instead of behavior.
- Depend on another test's data.
- Skip business rule validation.
- Ignore authentication and authorization.
- Leave critical workflows without automated tests.

---

# Golden Rule

Tests should verify that the ERP behaves correctly from a business perspective.

A feature is considered complete only when its expected business behavior is verified through automated tests.

---

# End-to-End (Playwright) Testing

E2E tests run the real FastAPI backend and the real React frontend together and are used to surface
frontend↔backend contract gaps, auth flows, and role guards that unit/API tests cannot catch.

## How to Run

From `frontend/`:

```
npx playwright test        # headless, single worker
npx playwright test --ui   # interactive UI
npx playwright test e2e/delivery.spec.ts   # single spec
npm run test:e2e           # full suite — 45 tests green (setup-owner + chromium)
```

## Architecture

- **Isolated database** `milk_management_e2e` — never the dev/prod DB `milk_managemen_ai`.
- Two `webServer` entries in `frontend/playwright.config.ts` boot everything per run:
  1. `scripts/e2e_backend.py` — FastAPI on port **8001**; on startup it drops/creates tables and
     seeds from `scripts/seed.py`, so every run starts from a known state. It also sets
     `REPORT_CACHE_DISABLED=1`, which makes `app/services/reports/cache.py` (module-level
     `CACHE_ENABLED` flag) no-op `get()`/`set()` so the in-memory 300s report cache — keyed by
     user with no invalidation on mutation — never serves stale zero-session data during E2E runs.
  2. Vite dev server on port **5174**, proxying `/api` → `http://localhost:8001`.
- `projects`: `setup-owner` (logs in as `owner/owner123` and saves `storageState`), plus `chromium`
  with a dependency on it. `auth.spec.ts` overrides `storageState` to start logged-out.
- Seed identities: `owner` = OWNER (`owner123`), `checker1` = CHECKER (`checker123`),
  `delivery1` = DELIVERY_PARTNER (`delivery123`), `admin` = OWNER (`admin123`),
  `employee1` = EMPLOYEE (`emp123`); route `R001 - Downtown Route`; customers
  `C00001 Rajesh Kumar` / `C00002 Priya Sharma` (C00001 has a VACATION exception
  today→today+2, so no deliveries today; `C00011 Karthik Rao` — "Small Pack Milk"
  2L MORNING/1L EVENING — is used for today's bill/payment tests); milk types
  rendered as `<name> (<volume> ml)`.

## Specs

`frontend/e2e/` (8 spec files, 45 tests): `auth.spec.ts`, `master-data.spec.ts`,
`operations.spec.ts`, `token-books.spec.ts`, `delivery.spec.ts`, `payments.spec.ts`,
`reports.spec.ts` (7 tests: dashboard today-session KPIs, route-delivery aggregation + "Balanced"
badge + totals + CSV download, consumption breakdown at `/reports/consumption/1`, revenue +
collection aging buckets (sum to balance), token utilization threshold flagging, role restrictions
for CHECKER/EMPLOYEE, DELIVERY_PARTNER own-route scope), plus `helpers.ts` (`unique`,
`uniquePhone`, `futureDate`) and `setup/owner.setup.ts`. Login assertions in `owner.setup.ts`,
`auth.spec.ts`, and `payments.spec.ts` now point to `/reports/dashboard` (the new index redirect).

## Pitfalls Learned (hard-won)

- **Trailing-slash redirects + proxy**: FastAPI 307-redirects `/api/v1/routes` → `/api/v1/routes/`.
  With Vite `changeOrigin: true` the browser follows the redirect straight to the backend origin and
  gets CORS-blocked. `frontend/vite.config.ts` must keep `changeOrigin: false`.
- **Native HTML5 validation blocks React errors**: form inputs use `required`/`min`/`minLength`, so
  the browser blocks submit before `validate()` runs. All form pages with custom `validate()` must
  use `<form noValidate>` or React validation messages are unreachable.
- **Required asterisks break `getByLabel`**: labels render `Name*`, so `getByLabel("Name")` substring
  matches `Name*` but `{ exact: true }` times out. Use anchored regexes like `getByLabel(/^Password/)`
  to avoid colliding with `Confirm Password`.
- **`selectOption` labels must be exact strings** — regex labels are not supported.
- **Unordered queries reorder rows after UPDATE**: PostgreSQL returns an updated row at the end of the
  heap when there is no `ORDER BY`. `getSessionDeliveries` had no ordering, so rows jumped around in
  the UI after a status update (fixed with `ORDER BY DailyDelivery.id`).
- **Duplicate-key E2E data**: delivery sessions are unique on `(route_id, delivery_date, shift)`.
  E2E tests that create sessions must use distinct dates.
- **Never run backend pytest against the dev DB**: `tests/conftest.py` defaults to
  `USE_ACTUAL_DB=true` and `TEST_DB_URL=...milk_managemen_ai`, and its session fixture runs
  `drop_all`/`create_all`. Running it wipes the dev/prod DB. Always set
  `USE_ACTUAL_DB=false` (SQLite) or point `TEST_DB_URL` at a scratch Postgres database.
- **Report cache can serve stale E2E data**: `app/services/reports/cache.py` caches report
  responses in memory for 300s, keyed by user, with no invalidation on delivery/payment mutation.
  E2E always boots with `REPORT_CACHE_DISABLED=1` (see Architecture above); a fresh E2E run that
  forgets this flag can assert against stale zero-session data.