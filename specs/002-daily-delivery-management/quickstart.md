# Quickstart Guide: Daily Delivery Management

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Overview

This guide provides validation scenarios to verify the daily delivery management feature works correctly.

---

## Prerequisites

1. PostgreSQL database running
2. FastAPI server started
3. Test data seeded (routes, customers, employees, token books)
4. Authentication configured (OWNER and CHECKER roles)

---

## Validation Scenarios

### Scenario 1: Normal Morning Delivery

**Goal**: Complete delivery lifecycle for a normal morning shift

**Steps**:
1. **Create Session**
   ```
   POST /api/v1/deliveries/sessions
   Body: { "route_id": 1, "delivery_date": "2026-01-27", "shift": "MORNING", "delivery_partner_id": 5 }
   Expected: 201 Created
   ```

2. **Record Dispatch**
   ```
   POST /api/v1/deliveries/sessions/1/dispatch
   Body: { "total_milk_loaded": 5.0 }
   Expected: 200 OK, status: "STARTED"
   ```

3. **Record Deliveries**
   ```
   POST /api/v1/deliveries
   Body: { "session_id": 1, "customer_id": 10, "milk_type_id": 1, "delivered_quantity": 1, "delivery_status": "DELIVERED", "token_sheet_number": 3 }
   Expected: 201 Created
   ```

4. **Record Cash Sale**
   ```
   POST /api/v1/deliveries
   Body: { "session_id": 1, "customer_id": 12, "milk_type_id": 1, "delivered_quantity": 1, "delivery_status": "CASH_SALE", "cash_amount": 25.00 }
   Expected: 201 Created
   ```

5. **Submit Reconciliation**
   ```
   POST /api/v1/deliveries/sessions/1/reconciliation/submit
   Body: { "total_cash_collected": 25.00, "cash_sales": [...], "returned_milk": 0.5 }
   Expected: 200 OK, is_balanced: true
   ```

6. **Close Session**
   ```
   POST /api/v1/deliveries/sessions/1/close
   Expected: 200 OK, status: "CLOSED"
   ```

**Expected Result**: Session closed with balanced reconciliation

---

### Scenario 2: Token Sheet Return

**Goal**: Return a token sheet for undelivered milk

**Steps**:
1. **Edit Previous Session**
   ```
   POST /api/v1/deliveries/sessions/2/reopen
   Body: { "reason": "Customer complaint" }
   Expected: 200 OK, status: "COMPLETED"
   ```

2. **Edit Delivery**
   ```
   PUT /api/v1/deliveries/10/edit
   Body: { "delivery_status": "NOT_DELIVERED", "return_token_sheet": true, "reason": "Customer said no milk" }
   Expected: 200 OK
   ```

**Expected Result**: Token sheet returned, customer's current_sheet decremented

---

### Scenario 3: Unplanned Customer with Token

**Goal**: Add unplanned customer and register token

**Steps**:
1. **Add Unplanned Delivery**
   ```
   POST /api/v1/deliveries/unplanned
   Body: { "session_id": 1, "customer_id": 15, "milk_type_id": 1, "delivered_quantity": 1, "delivery_status": "DELIVERED", "registration_method": "TOKEN_SHEET", "token_sheet_number": 5, "reason": "Customer changed mind" }
   Expected: 201 Created, delivery_source: "UNPLANNED"
   ```

2. **Validate Token**
   ```
   POST /api/v1/deliveries/validate-token
   Body: { "customer_id": 15, "milk_type_id": 1, "sheet_number": 5 }
   Expected: 200 OK, is_valid: true
   ```

**Expected Result**: Unplanned delivery recorded with token registered

---

### Scenario 4: Non-Sequential Token Sheet

**Goal**: Handle non-sequential token sheet with warning

**Steps**:
1. **Register Token**
   ```
   POST /api/v1/deliveries/10/register-token
   Body: { "token_sheet_number": 5, "acknowledged_warnings": ["NON_SEQUENTIAL_SHEET"], "acknowledgment_reason": "Customer confirmed #4 is lost" }
   Expected: 200 OK, warnings_logged: 1
   ```

**Expected Result**: Token registered with warning logged

---

### Scenario 5: New Book Usage Warning

**Goal**: Warn when new book is used before old book is finished

**Steps**:
1. **Validate Token**
   ```
   POST /api/v1/deliveries/validate-token
   Body: { "customer_id": 10, "milk_type_id": 1, "sheet_number": 1, "token_book_issue_id": 457 }
   Expected: 200 OK, warnings: ["NEW_BOOK_BEFORE_OLD_FINISHED"]
   ```

**Expected Result**: Warning shown, can proceed with acknowledgment

---

### Scenario 6: Concurrent Edit Detection

**Goal**: Handle optimistic locking conflict

**Steps**:
1. **User A Edits**
   ```
   PUT /api/v1/deliveries/10
   Body: { "delivery_status": "NOT_DELIVERED" }
   Expected: 200 OK, version: 2
   ```

2. **User B Edits (with old version)**
   ```
   PUT /api/v1/deliveries/10
   Body: { "delivery_status": "CASH_SALE" }
   Expected: 409 Conflict
   ```

**Expected Result**: Concurrent edit rejected with version conflict

---

### Scenario 7: Reconciliation Shortage

**Goal**: Handle milk shortage during reconciliation

**Steps**:
1. **Submit Reconciliation**
   ```
   POST /api/v1/deliveries/sessions/1/reconciliation/submit
   Body: { "total_cash_collected": 25.00, "returned_milk": 0.5 }
   Expected: 200 OK, is_balanced: false, difference: 0.2
   ```

2. **Attempt Close**
   ```
   POST /api/v1/deliveries/sessions/1/close
   Expected: 400 Bad Request, "Reconciliation not balanced"
   ```

**Expected Result**: Session cannot be closed until shortage resolved

---

### Scenario 8: Reopen History Tracking

**Goal**: Track multiple reopens of same session

**Steps**:
1. **First Reopen**
   ```
   POST /api/v1/deliveries/sessions/1/reopen
   Body: { "reason": "Customer complaint" }
   Expected: 200 OK, reopen_count: 1
   ```

2. **Close Again**
   ```
   POST /api/v1/deliveries/sessions/1/close
   Expected: 200 OK, status: "CLOSED"
   ```

3. **Second Reopen**
   ```
   POST /api/v1/deliveries/sessions/1/reopen
   Body: { "reason": "Another complaint" }
   Expected: 200 OK, reopen_count: 2
   ```

**Expected Result**: reopen_count incremented correctly

---

### Scenario 9: Customer History with Edits

**Goal**: View complete customer history including edits

**Steps**:
1. **Get Customer History**
   ```
   GET /api/v1/customers/10/delivery-history?include_reopened=true
   Expected: 200 OK with delivery records and edit history
   ```

**Expected Result**: All deliveries shown with edit details

---

### Scenario 10: Edit History for Audit

**Goal**: View complete edit history for a session

**Steps**:
1. **Get Edit History**
   ```
   GET /api/v1/deliveries/sessions/1/edit-history
   Expected: 200 OK with all edits
   ```

**Expected Result**: All edits shown with user, time, and reason

---

## Verification Checklist

### Data Integrity
- [ ] Token sheet numbers unique per book
- [ ] current_sheet incremented correctly
- [ ] No duplicate registrations for same book/sheet
- [ ] Reconciliation formula: loaded = token + cash + returned

### State Management
- [ ] Session status transitions valid
- [ ] Delivery status transitions valid
- [ ] Cannot close unbalanced session
- [ ] Reopen increments count correctly

### Audit Trail
- [ ] All edits logged with user/time/reason
- [ ] Token sheet warnings logged
- [ ] Session reopen history tracked

### Edge Cases
- [ ] Unplanned customer with token works
- [ ] Non-sequential sheet shows warning
- [ ] New book warning before old finished
- [ ] Concurrent edit conflict detected

---

## Test Commands

### Run Unit Tests
```bash
python -m pytest tests/unit/daily_delivery -v
```

### Run Integration Tests
```bash
python -m pytest tests/integration/daily_delivery -v
```

### Run All Tests
```bash
python -m pytest tests/ -v --tb=short
```

---

## Success Criteria

1. All validation scenarios pass
2. Unit test coverage > 80%
3. Integration tests pass
4. No critical bugs
5. Documentation complete

---

## Next Steps

After completing validation:
1. Run `/speckit.implement` to generate task breakdown
2. Review generated tasks
3. Start implementation
