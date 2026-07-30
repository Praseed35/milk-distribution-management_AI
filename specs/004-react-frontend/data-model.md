# Data Model: React Frontend TypeScript Types

> TypeScript interfaces mirroring backend Pydantic v2 response/request schemas. Organized per module in `frontend/src/types/`.

## Common Types (`common.ts`)

```typescript
// Generic API response envelopes used by backend
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

export interface PaginatedResponse<T> {
  data?: T[];          // Reports, generic list endpoints
  sessions?: T[];      // Delivery sessions list
  deliveries?: T[];    // Deliveries within a session
  total: number;
  page?: number;
  page_size?: number;
  generated_at?: string; // Reports
}

export interface ApiError {
  detail: string;
  errors?: Record<string, string[]>; // Field-level validation errors
}

export interface DateRangeParams {
  from_date?: string;   // YYYY-MM-DD
  to_date?: string;     // YYYY-MM-DD
  preset?: "today" | "yesterday" | "this_week" | "last_week" | 
           "this_month" | "last_month" | "this_year";
}
```

## Auth (`auth.ts`)

```typescript
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string; // "bearer"
}

export interface User {
  id: number;
  username: string;
  role: UserRole;
}

export type UserRole = "OWNER" | "ADMIN" | "CHECKER" | "DELIVERY_PARTNER" | "EMPLOYEE";

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}
```

## Route (`route.ts`)

```typescript
export interface RouteCreate {
  route_code: string;      // e.g. "R001"
  route_name: string;      // e.g. "Downtown Route"
  description?: string;
}

export interface RouteUpdate {
  route_name?: string;
  description?: string;
}

export interface RouteResponse {
  id: number;
  route_code: string;
  route_name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Customer (`customer.ts`)

```typescript
export interface CustomerCreate {
  customer_code: string;
  customer_name: string;
  primary_phone: string;   // Exactly 10 digits
  alternate_phone?: string;
  address?: string;
  route_id: number;
  remarks?: string;
}

export interface CustomerUpdate {
  customer_name?: string;
  primary_phone?: string;
  alternate_phone?: string;
  address?: string;
  route_id?: number;
  remarks?: string;
}

export interface CustomerResponse {
  id: number;
  customer_code: string;
  customer_name: string;
  primary_phone: string;
  alternate_phone: string | null;
  address: string | null;
  route_id: number;
  route_name?: string;     // Joined from route
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Milk Type (`milk-type.ts`)

```typescript
export interface MilkTypeCreate {
  milk_name: string;
  volume_ml: number;
  description?: string;
}

export interface MilkTypeUpdate {
  milk_name?: string;
  volume_ml?: number;
  description?: string;
}

export interface MilkTypeResponse {
  id: number;
  milk_name: string;
  volume_ml: number;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Employee (`employee.ts`)

```typescript
export interface EmployeeCreate {
  employee_code: string;
  name: string;
  phone: string;
  address?: string;
  role: "CHECKER" | "DELIVERY_PARTNER";
  route_id?: number | null;
  username?: string;      // Created with User account
  password?: string;      // For user account creation
}

export interface EmployeeUpdate {
  name?: string;
  phone?: string;
  address?: string;
  role?: "CHECKER" | "DELIVERY_PARTNER";
  route_id?: number | null;
}

export interface EmployeeCredentials {
  username: string;
  password: string;
}

export interface EmployeeResponse {
  id: number;
  employee_code: string;
  name: string;
  phone: string;
  address: string | null;
  role: string;
  route_id: number | null;
  route_name?: string;
  user_id: number | null;
  username?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Subscription (`subscription.ts`)

```typescript
export interface SubscriptionCreate {
  customer_id: number;
  milk_type_id: number;
  morning_quantity: number;
  evening_quantity: number;
  start_date: string;
  end_date?: string;
  remarks?: string;
}

export interface SubscriptionUpdate {
  morning_quantity?: number;
  evening_quantity?: number;
  end_date?: string;
  status?: string;
  remarks?: string;
}

export interface SubscriptionResponse {
  id: number;
  customer_id: number;
  customer_name?: string;
  customer_code?: string;
  route_name?: string;
  milk_type_id: number;
  milk_name?: string;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  start_date: string;
  end_date: string | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Delivery Exception (`delivery-exception.ts`)

```typescript
export interface DeliveryExceptionCreate {
  subscription_id: number;
  exception_type: "VACATION" | "NO_MILK" | "HOLIDAY";
  start_date: string;
  end_date: string;
  reason: string;
}

export interface DeliveryExceptionUpdate {
  exception_type?: string;
  end_date?: string;
  reason?: string;
  status?: string;
}

export interface DeliveryExceptionResponse {
  id: number;
  subscription_id: number;
  customer_name?: string;
  milk_name?: string;
  exception_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Token Identity (`token-identity.ts`)

```typescript
export interface TokenIdentityCreate {
  customer_id: number;
  milk_type_id: number;
  token_number: number;
}

export interface TokenIdentityUpdate {
  token_number?: number;
}

export interface TokenIdentityResponse {
  id: number;
  customer_id: number;
  customer_name?: string;
  milk_type_id: number;
  milk_name?: string;
  token_number: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Token Book (`token-book.ts`)

```typescript
export interface TokenBookIssueCreate {
  token_identity_id: number;
  customer_id: number;
  milk_type_id: number;
  issue_number: string;
  book_number: string;
  total_sheets: number;
  issue_date: string;
}

export interface TokenBookIssueResponse {
  id: number;
  token_identity_id: number;
  customer_id: number;
  customer_name?: string;
  milk_type_id: number;
  milk_name?: string;
  issue_number: string;
  book_number: string;
  total_sheets: number;
  current_sheet: number;
  status: "WAITING" | "ACTIVE" | "COMPLETED";
  issue_date: string;
  completion_date: string | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenBookPaymentCreate {
  token_book_issue_id: number;
  payment_mode: "PREPAID" | "POSTPAID";
  book_price: number;
  amount_paid: number;
  payment_date: string;
  collected_by?: number;
  remarks?: string;
}

export interface TokenBookPaymentResponse {
  id: number;
  token_book_issue_id: number;
  issue_number?: string;
  payment_mode: string;
  payment_status: "PAID" | "PARTIAL" | "PENDING";
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  collected_by: number | null;
  collector_name?: string;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Delivery Session (`delivery-session.ts`)

```typescript
export interface DeliverySessionCreate {
  route_id: number;
  delivery_date: string;     // YYYY-MM-DD
  shift: "MORNING" | "EVENING";
  delivery_partner_id: number;
}

export interface DeliverySessionResponse {
  id: number;
  route_id: number;
  route_name?: string;
  route_code?: string;
  delivery_date: string;
  shift: string;
  delivery_partner_id: number;
  delivery_partner_name?: string;
  status: "PLANNED" | "STARTED" | "COMPLETED" | "CLOSED";
  total_milk_loaded: number | null;
  total_token_registered: number | null;
  total_cash_sales: number | null;
  total_returned_milk: number | null;
  reconciliation_status: "BALANCED" | "UNBALANCED" | "PENDING" | null;
  reopened_by: number | null;
  reopened_at: string | null;
  reopen_count: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface SessionListResponse {
  sessions: DeliverySessionResponse[];
  total: number;
}
```

## Daily Delivery (`daily-delivery.ts`)

```typescript
export type DeliveryStatus = "DELIVERED" | "PENDING_TOKEN" | "CASH_SALE" | "NOT_DELIVERED" | "CANCELLED";

export interface DailyDeliveryResponse {
  id: number;
  session_id: number;
  customer_id: number;
  customer_name?: string;
  customer_code?: string;
  milk_type_id: number;
  milk_name?: string;
  planned_quantity: number;
  delivered_quantity: number | null;
  delivery_status: DeliveryStatus;
  delivery_source: "PLANNED" | "UNPLANNED";
  token_sheet_number: number | null;
  token_book_issue_id: number | null;
  cash_amount: number | null;
  added_reason: string | null;
  shift: string;
  delivery_date: string;
  remarks: string | null;
  version: number;
}

export interface DeliveryChecklistResponse {
  session: DeliverySessionResponse;
  deliveries: DailyDeliveryResponse[];
}

export interface TokenRegistrationRequest {
  delivery_id: number;
  token_sheet_number: number;
}

export interface UnplannedDeliveryRequest {
  session_id: number;
  customer_id: number;
  milk_type_id: number;
  quantity: number;
  delivery_status: DeliveryStatus;
  reason: string;
  token_sheet_number?: number;
  cash_amount?: number;
}

export interface TokenValidationRequest {
  customer_id: number;
  milk_type_id: number;
  sheet_number: number;
}

export interface TokenValidationResponse {
  valid: boolean;
  warning?: {
    code: string;
    message: string;
  };
}
```

## Payment (`payment.ts`)

```typescript
export interface CustomerPaymentCreate {
  customer_id: number;
  payment_mode: "CASH" | "UPI" | "CARD" | "CHEQUE" | "BANK_TRANSFER";
  amount: number;
  payment_date: string;
  remarks?: string;
}

export interface CustomerPaymentResponse {
  id: number;
  customer_id: number;
  customer_name?: string;
  payment_mode: string;
  amount: number;
  payment_date: string;
  remarks: string | null;
  created_at: string;
}

export interface BillGenerateRequest {
  customer_ids: number[];
  bill_period_start: string;
  bill_period_end: string;
}

export interface BillResponse {
  id: number;
  customer_id: number;
  customer_name?: string;
  bill_period_start: string;
  bill_period_end: string;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  bill_status: string;
  items: BillItemResponse[];
  created_at: string;
}

export interface BillItemResponse {
  milk_type_id: number;
  milk_name?: string;
  quantity: number;
  rate_per_unit: number;
  amount: number;
}

export interface OutstandingBalance {
  customer_id: number;
  customer_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  aging_days: number;
}
```

## Reports (`reports.ts`)

```typescript
export interface OperationalDashboard {
  report_date: string;
  total_sessions: number;
  total_milk_loaded: number;
  total_milk_delivered: number;
  total_cash_collected: number;
  deliveries_by_status: Record<string, number>;
  pending_token_count: number;
  unclosed_sessions: number;
  unbalanced_sessions: number;
  completed_not_closed: number;
}

export interface RouteDeliveryReport {
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

export interface RevenueReport {
  date_from: string;
  date_to: string;
  total_revenue: number;
  token_book_revenue: number;
  customer_bill_revenue: number;
  by_source: { source: string; amount: number; percentage: number }[];
  by_payment_mode?: { mode: string; amount: number; percentage: number }[];
  by_route?: { route_name: string; amount: number; percentage: number }[];
  by_milk_type?: { milk_name: string; amount: number; percentage: number }[];
}

export interface CustomerConsumptionReport {
  customer_id: number;
  customer_name: string;
  date_from: string;
  date_to: string;
  total_consumption: number;
  average_daily: number;
  days_with_data: number;
  trend: {
    period: "increasing" | "declining" | "stable";
    recent_7day_avg: number;
    preceding_21day_avg: number;
    change_percentage: number;
  };
  items: {
    date: string;
    total_quantity: number;
    by_milk_type: { milk_type: string; quantity: number }[];
  }[];
}

export interface TokenUtilizationReport {
  token_book_issue_id: number;
  customer_name: string;
  milk_name: string;
  issue_number: string;
  total_sheets: number;
  sheets_used: number;
  sheets_remaining: number;
  utilization_percentage: number;
}

export interface CollectionEfficiencyReport {
  customer_id: number;
  customer_name: string;
  total_billed: number;
  total_paid: number;
  balance: number;
  collection_percentage: number;
  aging_0_30: number;
  aging_31_60: number;
  aging_61_90: number;
  aging_90_plus: number;
}
```
