# Data Model: Subscription & Exceptions TypeScript Types

> TypeScript interfaces mirroring backend Pydantic v2 response/request schemas (`app/schemas/subscription.py`, `app/schemas/delivery_exception.py`). Verified 2026-07-31. Files live in `frontend/src/types/`.

## Shared summaries (referenced from existing type files)

```typescript
// from customer.ts
export interface CustomerSummaryResponse {
  id: number;
  customer_code: string;
  customer_name: string;
  primary_phone: string;
}

// from milk-type.ts
export interface MilkTypeSummaryResponse {
  id: number;
  milk_name: string;
  volume_ml: number;
  unit_price: number;
}
```

## Subscription (`subscription.ts`)

> `start_date`/`end_date` are **response-only** — never sent in create/update. List and Detail responses have different shapes; use both.

```typescript
export interface SubscriptionCreate {
  customer_id: number;          // gt=0
  milk_type_id: number;         // gt=0
  morning_quantity: number;     // default 0, ge=0
  evening_quantity: number;     // default 0, ge=0
  status?: string;              // default "ACTIVE", max 20
  remarks?: string | null;      // max 255
}

export interface SubscriptionUpdate {
  morning_quantity?: number;    // ge=0
  evening_quantity?: number;    // ge=0
  status?: string;              // max 20
  remarks?: string | null;      // max 255
}

// GET /subscriptions/ and GET /subscriptions/customer/{id}
export interface SubscriptionListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  milk_type_name: string;
  milk_type_volume: number;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  is_active: boolean;
}

// GET /subscriptions/{id} — edit form hydration
export interface SubscriptionDetailResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
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

// POST /subscriptions/, PUT /subscriptions/{id}, DELETE /subscriptions/{id}
export interface SubscriptionResponse {
  id: number;
  customer_id: number;
  milk_type_id: number;
  morning_quantity: number;
  evening_quantity: number;
  status: string;
  remarks: string | null;
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## Delivery Exception (`delivery-exception.ts`)

> `end_date`/`reason` optional on create; `status` updatable. `shift` (MORNING | EVENING | null) scopes the exception to a delivery shift — null means whole day and conflicts with every shift; a shift-specific exception only conflicts with the same shift or whole-day ones. List, single-resource, and detail responses have different shapes.

```typescript
export type ExceptionType = "VACATION" | "NO_MILK" | "HOLIDAY";
export type ExceptionShift = "MORNING" | "EVENING";

export interface DeliveryExceptionCreate {
  subscription_id: number;      // gt=0
  exception_type: ExceptionType; // max 20
  shift?: ExceptionShift | null; // null = whole day (validated against Shift enum server-side)
  start_date: string;           // required ISO datetime
  end_date?: string | null;
  reason?: string | null;       // max 255
}

export interface DeliveryExceptionUpdate {
  exception_type?: ExceptionType;
  shift?: ExceptionShift | null; // null clears back to whole day (via model_fields_set)
  start_date?: string;
  end_date?: string | null;
  reason?: string | null;
  status?: string;              // max 20
}

// GET /delivery-exceptions/ — flat list DTO
export interface DeliveryExceptionListResponse {
  id: number;
  subscription_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  route_name: string;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  status: string;
  is_active: boolean;
}

// POST /delivery-exceptions/, PUT/DELETE /delivery-exceptions/{id},
// GET /delivery-exceptions/subscription/{id}
export interface DeliveryExceptionResponse {
  id: number;
  subscription_id: number;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  reason: string | null;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// GET /delivery-exceptions/{id} — nested detail DTO
export interface DeliveryExceptionDetailResponse {
  id: number;
  subscription: SubscriptionSummaryResponse;
  exception_type: string;
  shift: string | null;
  start_date: string;
  end_date: string | null;
  reason: string | null;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionSummaryResponse {
  id: number;
  customer: CustomerSummaryResponse;
  morning_quantity: number;
  evening_quantity: number;
}
```

## State Transitions

| Entity | Source State | Trigger | Target State |
|---|---|---|---|
| Subscription | ACTIVE | deactivate (soft delete) | INACTIVE (`is_active=false`) |
| Subscription | INACTIVE | — | (no reactivation in this phase) |
| Exception | ACTIVE | deactivate (soft delete) | INACTIVE (`is_active=false`) |

## Validation Rules (client mirrors)

| Field | Rule | Enforced |
|---|---|---|
| `morning_quantity` / `evening_quantity` | >= 0 | client + server |
| `exception_type` | one of VACATION, NO_MILK, HOLIDAY | client (select) + server |
| `shift` | null (whole day), MORNING, or EVENING | client (select) + server (Shift enum) |
| `start_date` | required | client + server |
| `start_date` vs `end_date` | end not before start | client + server |
| exception overlap (same subscription) | none — whole-day conflicts with all shifts; shift-specific conflicts only with same shift or whole-day | server (client surfaces toast) |
| inactive subscription | cannot add exception | server (client surfaces toast) |
