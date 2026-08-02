# Data Model: Reports Pages (Phase 7)

> Frontend data contracts for `types/reports.ts`. These interfaces mirror the backend
> response schemas in `app/schemas/reports.py` exactly. All fields are optional-agnostic —
> the backend always returns them unless noted.

## Report Envelope (list-style reports)

```ts
interface ReportEnvelope<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  generated_at: string; // ISO datetime
}
```

Returned by `/reports/route-delivery`, `/reports/token-utilization`, `/reports/collection-efficiency`.
Summary/overall figures are NOT in the envelope — compute them client-side from `data`.

## Operational Dashboard

```ts
interface OperationalDashboard {
  report_date: string;                       // ISO date (today)
  total_sessions: number;
  total_milk_loaded: number;
  total_milk_delivered: number;
  total_cash_collected: number;
  deliveries_by_status: Record<
    "DELIVERED" | "PENDING_TOKEN" | "CASH_SALE" | "NOT_DELIVERED" | "CANCELLED",
    number
  >;
  pending_token_count: number;
  unclosed_sessions: number;
  unbalanced_sessions: number;
  completed_not_closed: number;
}
```

## Route Delivery Report

```ts
interface RouteDeliveryItem {
  route_id: number;
  route_name: string;
  route_code: string;
  session_count: number;
  delivery_count: number;
  total_loaded_quantity: number;
  total_delivered_quantity: number;
  total_cash_collected: number;
  total_token_registered: number;
  total_returned_quantity: number;
  shortage_surplus: number;
  is_balanced: boolean;
}
```

`/reports/route-delivery` returns `ReportEnvelope<RouteDeliveryItem>`. The summary row is computed
client-side by summing numeric columns across `data`.

## Revenue Report

```ts
interface RevenueBreakdown {
  source: string;           // "TOKEN_BOOK" | "CUSTOMER_BILL" (as returned by backend)
  payment_mode: string | null;
  route_name: string | null;
  milk_type_name: string | null;
  amount: number;
  percentage: number;
}

interface RevenueReport {
  date_from: string;        // ISO date
  date_to: string;          // ISO date
  total_revenue: number;
  token_book_revenue: number;
  customer_bill_revenue: number;
  by_source: RevenueBreakdown[];
  by_payment_mode: RevenueBreakdown[];
  by_route: RevenueBreakdown[];
  by_milk_type: RevenueBreakdown[];
}
```

Returned directly (no envelope) by `/reports/revenue`.

## Customer Consumption Report

```ts
interface ConsumptionDay {
  date: string;             // ISO date
  total_quantity: number;
  by_milk_type: Record<string, number>[]; // [{ milk_type_name, quantity }]
}

interface ConsumptionTrend {
  period: string;                       // e.g. "30d"
  recent_7day_avg: number | null;
  preceding_21day_avg: number | null;
  change_percentage: number | null;
}

interface CustomerConsumptionReport {
  customer_id: number;
  customer_name: string;
  date_from: string;
  date_to: string;
  group_by: string;         // "day"
  total_consumption: number;
  average_daily: number;
  days_with_data: number;
  trend: ConsumptionTrend;
  items: ConsumptionDay[];
}
```

Returned directly (no envelope) by `/reports/customer/{id}/consumption`.

## Token Utilization Report

```ts
interface TokenUtilizationItem {
  customer_id: number;
  customer_name: string;
  route_name: string;
  token_number: number;
  milk_type_name: string;
  total_books_issued: number;
  active_books: number;
  completed_books: number;
  total_sheets_used: number;
  total_sheets_remaining: number;
  utilization_percentage: number;   // 0-100
  books_below_20_percent: number;
}
```

`/reports/token-utilization` returns `ReportEnvelope<TokenUtilizationItem>`. Overall utilization is
computed client-side: `used / (used + remaining) × 100`.

## Collection Efficiency Report

```ts
interface CustomerCollectionItem {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  collection_percentage: number;    // 0-100
  last_bill_date: string | null;    // ISO date
  last_payment_date: string | null; // ISO date
  aging_current: number;
  aging_31_60: number;
  aging_61_90: number;
  aging_90_plus: number;
}
```

`/reports/collection-efficiency` returns `ReportEnvelope<CustomerCollectionItem>`. The overall
collection percentage is computed client-side: `total_paid / total_billed × 100`. Aging invariant:
`aging_current + aging_31_60 + aging_61_90 + aging_90_plus === balance`.

## Query params (shared)

```ts
interface ReportDateParams {
  preset?: "today" | "yesterday" | "this_week" | "last_week" | "this_month" | "last_month" | "this_year";
  from_date?: string;   // ISO date
  to_date?: string;     // ISO date
  refresh?: boolean;    // bypass backend cache
}
```

Route-specific params: `route_id` (route-delivery, token-utilization, collection-efficiency),
`shift` (route-delivery), `milk_type_id` + `payment_mode` (revenue), `customer_id` (token-utilization),
`low_threshold` (token-utilization, default 20), `min_outstanding` (collection-efficiency).
