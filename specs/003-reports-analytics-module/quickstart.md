# Quickstart: Reports and Analytics Module

**Date**: 2026-07-30 | **Phase**: Phase 1 (Design & Contracts)

This guide provides runnable validation scenarios to verify the feature works end-to-end. Use this after implementation to confirm correctness.

**Prerequisites**:
- Database seeded with sample data (`python scripts/seed.py`)
- Server running (`uvicorn app.main:app`)

**Test files**: `tests/test_reports.py`

---

## Validation Scenario 1: Route Delivery Report

### Setup
```python
# Seed data: Create 1 route, 3 customers with subscriptions
# Create 1 delivery session for today, record 3 deliveries (2 DELIVERED, 1 CASH_SALE)
# Session loaded = 6L, delivered = 4L, cash = 2L
```

### Test
```
GET /reports/route-delivery?preset=today&route_id=1
```

### Expected Outcome
```json
{
  "data": [{
    "route_id": 1,
    "route_name": "Route A",
    "session_count": 1,
    "delivery_count": 3,
    "total_loaded_quantity": 6.0,
    "total_delivered_quantity": 6.0,
    "total_cash_collected": 2.0,
    "shortage_surplus": 0.0,
    "is_balanced": true
  }],
  "total": 1,
  "page": 1
}
```

### Verification
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/reports/route-delivery?preset=today&route_id=1" | python -m json.tool
```

---

## Validation Scenario 2: Revenue Report

### Setup
```python
# Seed: Create 2 token book payments (3000 + 2000 = 5000 INR)
# Seed: Create 2 customer bill payments (1500 + 1500 = 3000 INR)
# Total revenue should be 8000 INR
```

### Test
```
GET /reports/revenue?preset=this_month
```

### Expected Outcome
- `total_revenue` = 8000.0
- `token_book_revenue` = 5000.0
- `customer_bill_revenue` = 3000.0
- `by_source` has 2 entries with correct percentages (62.5% and 37.5%)

### Verification
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/reports/revenue?preset=this_month" | python -m json.tool
```

### Role Restriction Test
```bash
# Should return 403 for non-OWNER roles
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8000/reports/revenue?preset=this_month" | grep -q "403"
```

---

## Validation Scenario 3: Collection Efficiency

### Setup
```python
# Seed: Create a bill for Customer A: 1000 INR
# Seed: Record payment of 600 INR for Customer A
# Expected: 60% collection, 400 INR outstanding
```

### Test
```
GET /reports/collection-efficiency?customer_id=1
```

### Expected Outcome
```json
{
  "data": [{
    "customer_id": 1,
    "customer_name": "Customer A",
    "total_billed": 1000.0,
    "total_paid": 600.0,
    "balance": 400.0,
    "collection_percentage": 60.0
  }],
  "overall_collection_percentage": 60.0
}
```

---

## Validation Scenario 4: Customer Consumption

### Setup
```python
# Seed: Customer A with subscription for 2L/day
# Record 30 days of deliveries at 2L/day = 60L total
```

### Test
```
GET /reports/customer/1/consumption?group_by=day
```

### Expected Outcome
- `total_consumption` = 60.0
- `average_daily` = 2.0
- `days_with_data` = 30
- `items` has 30 entries with 2.0 each

---

## Validation Scenario 5: Token Book Utilization

### Setup
```python
# Seed: Customer A with token identity, token book issue (30 sheets, 20 used)
# Expected: 20 used, 10 remaining, 66.67% utilization
```

### Test
```
GET /reports/token-utilization
```

### Expected Outcome
```json
{
  "data": [{
    "customer_name": "Customer A",
    "total_sheets_used": 20,
    "total_sheets_remaining": 10,
    "utilization_percentage": 66.67
  }]
}
```

---

## Validation Scenario 6: Operational Dashboard

### Setup
```python
# Seed: 3 sessions today (2 closed, 1 STARTED with balanced reconciliation)
# Seed: 1 session from yesterday (CLOSED)
# Seed: 20 deliveries (15 DELIVERED, 3 CASH_SALE, 2 PENDING_TOKEN)
```

### Test
```
GET /reports/dashboard
```

### Expected Outcome
```json
{
  "total_sessions": 3,
  "total_milk_loaded": 30.0,
  "total_milk_delivered": 28.0,
  "total_cash_collected": 5.0,
  "deliveries_by_status": {
    "DELIVERED": 15,
    "PENDING_TOKEN": 2,
    "CASH_SALE": 3,
    "NOT_DELIVERED": 0,
    "CANCELLED": 0
  },
  "unclosed_sessions": 1,
  "unbalanced_sessions": 0,
  "completed_not_closed": 0
}
```

---

## Validation Scenario 7: CSV Export

### Test
```
GET /reports/route-delivery?preset=today&format=csv
```

### Expected Outcome
```csv
route_id,route_name,route_code,session_count,delivery_count,total_loaded_quantity,total_delivered_quantity,total_cash_collected,shortage_surplus,is_balanced
1,Route A,R001,1,3,6.0,6.0,2.0,0.0,true
```

### Verification
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/reports/route-delivery?preset=today&format=csv" | head -2
```

---

## Running All Tests

```bash
# Run the full report test suite
pytest tests/test_reports.py -v --tb=short

# Run with coverage (if configured)
pytest tests/test_reports.py --cov=app.services.reports --cov=app.routers.reports --cov=app.schemas.reports
```

---

## Expected Test Count

| Test Area | Expected Tests |
|-----------|---------------|
| Route Delivery Report | 8-10 (success, filter variants, auth, edge cases) |
| Revenue Report | 6-8 (success, role restriction, empty data) |
| Collection Efficiency | 6-8 (success, aging, filters, empty) |
| Customer Consumption | 6-8 (success, trend, customer not found) |
| Token Utilization | 6-8 (success, empty, low threshold filter) |
| Operational Dashboard | 6-8 (success, mixed session states) |
| CSV Export | 4-6 (per report type, content-type header) |
| Authentication/RBAC | 6-8 (401, 403 per role) |
| **Total** | **~48-64 tests** |
