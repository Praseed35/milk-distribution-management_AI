# Data Model: Reports and Analytics Module

**Date**: 2026-07-30 | **Phase**: Phase 1 (Design & Contracts)

**Note**: No new database tables. All data is computed from existing tables via SQL aggregation queries. This document defines the virtual data model (report response structures).

---

## 1. Route Delivery Report

### Source Tables
- `delivery_sessions` — session metadata (route_id, delivery_date, shift, status, total_milk_loaded)
- `daily_deliveries` — per-customer delivery data (delivered_quantity, delivery_status, milk_type_id)
- `customers` — customer info (name, code)
- `delivery_exceptions` — to exclude excepted customers from expected totals

### Query Logic
1. Find all sessions matching route_id (or all routes if null) within date range
2. For each session, sum loaded quantity from `delivery_sessions.total_milk_loaded`
3. For each session, aggregate `daily_deliveries` by status:
   - DELIVERED, CASH_SALE → delivered quantity
   - NOT_DELIVERED, CANCELLED → counted but excluded from delivered total
4. Cash sales are `daily_deliveries` where `delivery_status == 'CASH_SALE'`
5. Returned milk is the difference between loaded and delivered
6. Shortage/surplus = loaded - (delivered + cash_sales + returned)

### Response Structure

```python
class RouteDeliveryItem(BaseModel):
    route_id: int
    route_name: str
    route_code: str
    session_count: int
    delivery_count: int
    total_loaded_quantity: float           # sum of total_milk_loaded across sessions
    total_delivered_quantity: float        # sum of delivered quantities (DELIVERED + CASH_SALE)
    total_cash_collected: float            # sum of cash_sale delivery amounts
    total_token_registered: float          # sum of DELIVERED status quantities
    total_returned_quantity: float         # loaded - delivered - cash_sales
    shortage_surplus: float                # loaded - (delivered + returned + cash_sales)
    is_balanced: bool                      # |shortage_surplus| < 0.01

class RouteDeliveryReport(BaseModel):
    route_id: int | None                   # None = all routes
    date_from: date
    date_to: date
    shift: str | None                      # MORNING, EVENING, or None for both
    items: list[RouteDeliveryItem]         # one per route (or grouped by day/week)
    summary: RouteDeliveryItem             # totals across all items
```

---

## 2. Revenue Report

### Source Tables
- `customer_payments` — payments with amount, payment_date, payment_mode, payment_type
- `customer_bills` — bills with total_amount
- `token_book_payments` — token book payments with amount, payment_date, payment_mode

### Query Logic
1. Union of `customer_payments` (type=BILL_PAYMENT) and `token_book_payments` (type=PREPAID/POSTPAID)
2. Filter by date range on payment_date
3. Group by source (token_book_payments vs customer_payments), milk_type, route, payment_mode
4. For milk_type grouping: join through subscriptions/token_identities/customer relationships

### Response Structure

```python
class RevenueBreakdown(BaseModel):
    source: str                            # "token_book_payments" or "customer_bill_payments"
    payment_mode: str | None               # CASH, UPI, CARD, etc.
    route_name: str | None
    milk_type_name: str | None
    amount: float
    percentage: float                      # contribution to total (0-100)

class RevenueReport(BaseModel):
    date_from: date
    date_to: date
    total_revenue: float
    token_book_revenue: float
    customer_bill_revenue: float
    by_source: list[RevenueBreakdown]
    by_payment_mode: list[RevenueBreakdown]
    by_route: list[RevenueBreakdown]
    by_milk_type: list[RevenueBreakdown]
```

---

## 3. Collection Efficiency Report

### Source Tables
- `customer_bills` — total_amount, bill_period_start, bill_period_end, due_date, status
- `customer_payments` — amount, payment_date, linked to bills via reference
- `customers` — customer info, route_id

### Query Logic
1. For each customer (filtered by route if specified):
   - Sum `customer_bills.total_amount` for bills in date range
   - Sum `customer_payments.amount` for payments in date range (where payment_type != 'ADVANCE')
   - Balance = billed - paid
   - Collection % = (paid / billed) * 100 (if billed > 0)
2. Aging: based on bill due_dates relative to report date

### Response Structure

```python
class CustomerCollectionItem(BaseModel):
    customer_id: int
    customer_code: str
    customer_name: str
    route_name: str
    total_billed: float
    total_paid: float
    balance: float
    collection_percentage: float
    last_bill_date: date | None
    last_payment_date: date | None
    aging_current: float                   # 0-30 days
    aging_31_60: float                     # 31-60 days
    aging_61_90: float                     # 61-90 days
    aging_90_plus: float                   # 90+ days

class CollectionEfficiencyReport(BaseModel):
    date_from: date
    date_to: date
    route_id: int | None
    total_billed: float
    total_paid: float
    total_balance: float
    overall_collection_percentage: float
    items: list[CustomerCollectionItem]
```

---

## 4. Customer Consumption Report

### Source Tables
- `daily_deliveries` — delivered_quantity, delivery_status, milk_type_id, session_id
- `delivery_sessions` — delivery_date, shift
- `milk_types` — milk_name, volume_ml
- `subscriptions` — morning_quantity, evening_quantity

### Query Logic
1. Join `daily_deliveries` → `delivery_sessions` to get delivery_date
2. Filter by customer_id and date range
3. Group by date (or week/month based on group_by param)
4. For each group, sum delivered_quantity per milk_type
5. Trend: compare last 7 days avg vs preceding 21 days avg (requires 14+ days data)

### Response Structure

```python
class ConsumptionDay(BaseModel):
    date: date
    total_quantity: float
    by_milk_type: list[dict]              # [{"milk_type": "Full Cream", "quantity": 2.0}, ...]

class ConsumptionTrend(BaseModel):
    period: str                            # "increasing", "declining", "stable", "insufficient_data"
    recent_7day_avg: float | None
    preceding_21day_avg: float | None
    change_percentage: float | None

class CustomerConsumptionReport(BaseModel):
    customer_id: int
    customer_name: str
    date_from: date
    date_to: date
    group_by: str                          # "day", "week", "month"
    total_consumption: float
    average_daily: float
    days_with_data: int
    trend: ConsumptionTrend
    items: list[ConsumptionDay]
```

---

## 5. Token Book Utilization Report

### Source Tables
- `token_identities` — token_number, customer_id, milk_type_id
- `token_book_issues` — issue_number, total_sheets, current_sheet, status
- `token_book_payments` — amount, status, book_price
- `customers` — customer info
- `daily_deliveries` — to count used sheets (via token registration)

### Query Logic
1. For each token identity, find the active (or all) book issues
2. Used sheets = `current_sheet` (tracks last used sheet number)
3. Remaining = `total_sheets - current_sheet`
4. Utilization % = (current_sheet / total_sheets) * 100
5. Group by customer, route

### Response Structure

```python
class TokenUtilizationItem(BaseModel):
    customer_id: int
    customer_name: str
    route_name: str
    token_number: int
    milk_type_name: str
    total_books_issued: int
    active_books: int
    completed_books: int
    total_sheets_used: int
    total_sheets_remaining: int
    utilization_percentage: float
    books_below_20_percent: int            # books needing replacement soon

class TokenUtilizationReport(BaseModel):
    route_id: int | None
    total_customers_with_tokens: int
    total_books_issued: int
    total_sheets_used: int
    total_sheets_remaining: int
    overall_utilization_percentage: float
    items: list[TokenUtilizationItem]
```

---

## 6. Operational Dashboard

### Source Tables
- `delivery_sessions` — today's sessions grouped by route
- `daily_deliveries` — today's delivery status counts
- `subscriptions`, `delivery_exceptions` — expected quantities

### Query Logic
1. Count sessions for today's date across all routes
2. For each session, aggregate delivery statuses
3. Sum loaded milk across all sessions
4. Sum delivered milk across all deliveries with DELIVERED or CASH_SALE status
5. Count unclosed sessions from previous days (status != CLOSED and delivery_date < today)
6. Count unbalanced sessions (sessions with status=STARTED/COMPLETED that have reconciliation diff)
7. Count sessions left in COMPLETED status (dispatch done but not closed)

### Response Structure

```python
class OperationalDashboard(BaseModel):
    report_date: date
    total_sessions: int
    total_milk_loaded: float
    total_milk_delivered: float
    total_cash_collected: float
    deliveries_by_status: dict             # {"DELIVERED": N, "PENDING_TOKEN": N, "CASH_SALE": N, "NOT_DELIVERED": N, "CANCELLED": N}
    pending_token_count: int
    unclosed_sessions: int                 # previous days, not closed
    unbalanced_sessions: int               # sessions with reconciliation issues
    completed_not_closed: int              # dispatch done, awaiting close
```

---

## 7. Shared Types

### Report Envelope (all list endpoints)

```python
class ReportEnvelope(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    generated_at: datetime
```

### Report Request Filters

```python
class DateRangeFilter(BaseModel):
    preset: str | None = None              # "today", "yesterday", "this_week", "last_week", "this_month", "last_month", "this_year"
    from_date: date | None = None
    to_date: date | None = None
    shift: str | None = None               # "MORNING", "EVENING"
    group_by: str | None = None            # "day", "week", "month"

class ReportPagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
```

---

## 8. Existing Tables Referenced

| Table | Key Columns Used | Report Usage |
|-------|-----------------|-------------|
| `delivery_sessions` | id, route_id, delivery_date, shift, status, total_milk_loaded, delivery_partner_id | Route, Dashboard |
| `daily_deliveries` | id, session_id, customer_id, milk_type_id, delivered_quantity, delivery_status, planned_quantity | Route, Consumption, Dashboard |
| `customers` | id, customer_code, customer_name, route_id, is_active | All reports |
| `routes` | id, route_name, route_code, is_active | Route, Revenue |
| `milk_types` | id, milk_name, volume_ml, is_active | Revenue, Consumption |
| `subscriptions` | id, customer_id, milk_type_id, morning_quantity, evening_quantity, is_active | Route (expected qty) |
| `customer_payments` | id, customer_id, amount, payment_date, payment_mode, payment_type | Revenue, Collection |
| `customer_bills` | id, customer_id, total_amount, paid_amount, bill_period_start, bill_period_end, due_date, status | Collection |
| `customer_bill_items` | id, bill_id, milk_type_id, quantity, unit_price, total_price | Collection |
| `token_book_issues` | id, token_identity_id, issue_number, total_sheets, current_sheet, status | Token Utilization |
| `token_book_payments` | id, token_book_issue_id, amount, payment_date, payment_mode | Revenue |
| `token_identities` | id, customer_id, milk_type_id, token_number | Token Utilization |
| `delivery_exceptions` | id, subscription_id, start_date, end_date, status | Route (exclude expected) |
