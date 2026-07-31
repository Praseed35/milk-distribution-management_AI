# Quickstart: Subscription & Exceptions Validation Guide

> Runnable validation scenarios proving the feature works end-to-end. Contract and field details in [`contracts/README.md`](./contracts/README.md) and [`data-model.md`](./data-model.md).

## Prerequisites

- Backend running at `http://localhost:8000` (all endpoints under `/api/v1`)
- Database seeded with test data (`python scripts/seed.py`)
- Frontend from the parent feature running: `cd frontend && npm install && npm run dev` (http://localhost:5173)

## Build Verification (before manual testing)

```bash
cd frontend
npm run build          # must pass with no TypeScript errors
npm run dev            # dev server on :5173
```

## Validation Scenarios

### V1: Subscriptions — list and filter

1. Log in as `owner` / `owner123`
2. Navigate to **Operations → Subscriptions** (`/subscriptions`)
3. **Expected**: Table renders with columns Customer Code, Customer Name, Route, Milk Type (name + volume), Morning Qty, Evening Qty, Status, Actions. Loading skeleton shows briefly, then data.
4. Select a customer in the customer filter
5. **Expected**: Only that customer's subscriptions remain (client filters or `/subscriptions/customer/{id}`).

### V2: Subscriptions — create / edit / deactivate

1. On the Subscriptions page click **Create Subscription**
2. Fill: Customer (dropdown of active customers), Milk Type (dropdown), Morning Qty `2`, Evening Qty `1`
3. Submit
4. **Expected**: Success toast "Subscription created"; new row appears with ACTIVE badge. Request body must NOT contain `start_date`/`end_date` (check Network tab).
5. Edit the new subscription → change Morning Qty to `3` → submit
6. **Expected**: Success toast; row quantity updates to 3.
7. Enter a negative quantity → submit
8. **Expected**: Inline validation error "must be zero or greater"; no request sent.
9. Delete (deactivate) the subscription → confirm dialog → confirm
10. **Expected**: Row shows INACTIVE badge (soft delete; still listed).

### V3: Exceptions — list and create

1. Navigate to **Operations → Exceptions** (`/delivery-exceptions`)
2. **Expected**: Table renders with Customer, Route, Type, Shift, Start, End, Status, Actions.
3. Click **Create Exception**
4. Fill: Subscription (dropdown showing customer + milk info), Type `VACATION`, Shift `Morning` (or leave Whole Day), Start Date today, End Date today + 2, Reason optional
5. Submit
6. **Expected**: Success toast "Exception created"; new row appears with ACTIVE badge and the chosen shift (or "Whole Day").
7. Create a second exception for the **same subscription** with an **overlapping** date range and the **same shift**
8. **Expected**: Error toast about overlap; no row created.
9. Create a second exception for the same date range but the **other shift**
10. **Expected**: Created successfully — different shifts coexist on the same subscription/date.
11. Set Start Date after End Date → submit
12. **Expected**: Inline validation error; no request sent.
13. Edit an exception (change end date or shift) → submit → row updates.
14. Delete an exception → confirm → INACTIVE badge (soft delete).

### V4: CHECKER read-only (RBAC)

1. Log out, log in as a CHECKER user
2. Navigate to Subscriptions and Exceptions
3. **Expected**: Lists render normally, but **no** Create/Edit/Delete buttons or links are visible anywhere on either page.
4. Manually navigate to `/subscriptions/new` and `/delivery-exceptions/new`
5. **Expected**: 403 "Forbidden" page renders; the form never mounts.

### V5: Empty and error states

1. With no subscriptions/exceptions matching a filter, clear the filter
2. **Expected**: Empty state "No records found" (with Create button for OWNER/ADMIN).
3. Stop the backend, then reload a list page
4. **Expected**: Error toast after retries; page shows an error/empty state rather than crashing.

## Acceptance Trace

| Parent spec item | Scenario |
|---|---|
| US-020 subscription lifecycle | V1, V2 |
| US-021 exception lifecycle | V3 |
| US-022 CHECKER read-only | V4 |
| FR-012/013 validation | V2 step 7-8, V3 step 9-10 |
| FR-014 overlap rejection | V3 step 7-8 |
| SC-003 load < 1s | V1 step 3 (visual check) |
