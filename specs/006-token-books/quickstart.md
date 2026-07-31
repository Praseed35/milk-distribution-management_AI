# Quickstart: Token Book Pages Validation Guide

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

### V1: Token Identities — list and filter

1. Log in as `owner` / `owner123`
2. Navigate to **Operations → Token Identities** (`/token-identities`)
3. **Expected**: Table renders with columns Customer Code, Customer Name, Milk Type (name + volume), Token Number, Actions. Loading skeleton shows briefly, then data.
4. Select a customer in the customer filter (and/or a milk type filter)
5. **Expected**: Only matching identities remain (client-side filter over the list).

### V2: Token Identities — create / edit / deactivate

1. On the Token Identities page click **Create Identity**
2. Fill: Customer (dropdown of active customers), Milk Type (dropdown), Token Number `100`
3. Submit
4. **Expected**: Success toast "Token identity created"; new row appears with Token Number 100.
5. Create a second identity with the **same** customer + milk type + token number
6. **Expected**: Error toast (duplicate); no row created; form stays open.
7. Edit the first identity → change Token Number to `101` → submit
8. **Expected**: Success toast; row updates to 101.
9. Enter a token number of `0` or negative → submit
10. **Expected**: Inline validation error; no request sent.
11. Delete (deactivate) the identity → confirm dialog → confirm
12. **Expected**: Row disappears (backend returns active rows only).

### V3: Token Book Issues — list and create

1. Navigate to **Operations → Token Book Issues** (`/token-book-issues`)
2. **Expected**: Table renders with Customer, Milk Type, Token Number, Issue Number, Issue Date, Current Sheet, Status, Actions.
3. Click **Create Issue**
4. Fill: Token Identity (dropdown — customers without an active book offered), Issue Number `5`, Remarks optional
5. Submit
6. **Expected**: Success toast "Token book issue created"; row appears with status WAITING and Current Sheet 0.
7. Try to create a **second** issue for the same identity
8. **Expected**: Error toast (active book exists) — or the identity is not offered in the dropdown once an ACTIVE book exists; no row created.
9. Edit the issue → set Status to `ACTIVE`, Current Sheet `10` → submit
10. **Expected**: Row updates to ACTIVE / sheet 10.
11. Edit again → set Status to `COMPLETED` → submit
12. **Expected**: Status badge shows Completed.
13. Delete an issue → confirm → row disappears (soft delete).

### V4: Token Book Payments — list and create

1. Navigate to **Operations → Token Payments** (`/token-book-payments`)
2. **Expected**: Table renders with Customer, Payment Mode, Book Price, Amount Paid, Balance, Status, Date, Actions.
3. Click **Create Payment**
4. Fill: Book Issue (dropdown), Payment Mode `PREPAID`, Book Price `100`, Amount Paid `100`
5. Submit
6. **Expected**: Success toast "Token book payment created"; row shows Balance 0 and status PAID.
7. Create another payment with Book Price `100`, Amount Paid `40`
8. **Expected**: Balance 60, status PARTIAL.
9. Create a payment with Book Price `100`, Amount Paid `150`
10. **Expected**: Inline validation error (amount cannot exceed book price); no request sent.
11. Edit the partial payment → Amount Paid `100` → submit
12. **Expected**: Balance recomputed to 0, status PAID.
13. Delete a payment → confirm → row disappears (soft delete).

### V5: CHECKER operations (RBAC)

1. Log out, log in as a CHECKER user
2. Navigate to Token Identities and Token Book Issues
3. **Expected**: Both lists render normally (nav shows all three) with full **Create/Edit/Delete** actions visible and working (create an identity, edit an issue, etc.)
4. Navigate to Token Payments
5. **Expected**: The payments list renders read-only — no Create/Edit/Delete buttons or links are visible.
6. Manually navigate to `/token-book-payments/new` and `/token-book-payments/:id/edit`
7. **Expected**: 403 "Forbidden" page renders; the payment form never mounts. `/token-identities/new`, `/token-book-issues/new` and their edit routes render normally.

### V6: Empty and error states

1. With no rows matching a filter, clear the filter
2. **Expected**: Full list renders again; empty list shows "No records found" (with Create button for OWNER/ADMIN).
3. Stop the backend, then reload a list page
4. **Expected**: Error toast after retries; page shows an error/empty state rather than crashing.

## Acceptance Trace

| Parent spec item | Scenario |
|---|---|
| US-030 token identity lifecycle | V1, V2 |
| US-031 book issuance | V3 |
| US-032 book payments | V4 |
| US-033 CHECKER read-only | V5 |
| FR-006 duplicate identity | V2 step 5-6 |
| FR-012 active book exists | V3 step 7-8 |
| FR-013 duplicate issue number | V3 (server 400 path) |
| FR-019 amount exceeds book price | V4 step 9-10 |
| FR-020 balance computation | V4 step 7-8, 11-12 |
| SC-001/002/003 create under 2 min | V2/V3/V4 (timed) |
