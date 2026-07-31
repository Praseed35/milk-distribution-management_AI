# Data Model: Token Book TypeScript Types

> TypeScript interfaces mirroring backend Pydantic v2 response/request schemas (`app/schemas/token_identity.py`, `app/schemas/token_book.py`). Verified 2026-07-31. Files live in `frontend/src/types/`.

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
  unit_price: number; // backend defaults to 0 when omitted
}
```

## Token Identity (`token-identity.ts`)

> `customer_id` and `milk_type_id` are immutable after creation — `TokenIdentityUpdate` carries only `token_number`. List, single-resource, and detail responses have different shapes; use all three.

```typescript
export interface TokenIdentityCreate {
  customer_id: number;   // gt=0
  milk_type_id: number;  // gt=0
  token_number: number;  // gt=0
}

export interface TokenIdentityUpdate {
  token_number?: number; // gt=0 (only updatable field)
}

// GET /token-books/identities/ — flat list DTO
export interface TokenIdentityListResponse {
  id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  milk_type_id: number;
  milk_type_name: string;
  milk_type_volume: number;
  token_number: number;
  is_active: boolean;
}

// GET /token-books/identities/{id} — nested detail DTO (edit form hydration)
export interface TokenIdentityDetailResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
  token_number: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// POST /token-books/identities/, PUT/DELETE /token-books/identities/{id},
// GET /token-books/identities/customer/{id}
export interface TokenIdentityResponse {
  id: number;
  customer_id: number;
  milk_type_id: number;
  token_number: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Nested summary used by issue/payment detail DTOs
export interface TokenIdentitySummaryResponse {
  id: number;
  customer: CustomerSummaryResponse;
  milk_type: MilkTypeSummaryResponse;
  token_number: number;
}
```

## Token Book Issue (`token-book.ts`)

> `issue_date`, `current_sheet` (0), and `status` ("WAITING") are backend-assigned on create — never sent. `book_number`/`total_sheets` are backend-internal and never returned. Status values: `WAITING` | `ACTIVE` | `COMPLETED`.

```typescript
export type BookIssueStatus = "WAITING" | "ACTIVE" | "COMPLETED";
export type BookPaymentStatus = "PAID" | "PARTIAL" | "PENDING";
export type TokenPaymentMode = "PREPAID" | "POSTPAID";

export interface TokenBookIssueCreate {
  token_identity_id: number; // gt=0
  issue_number: number;      // gt=0
  remarks?: string | null;   // max 255
}

export interface TokenBookIssueUpdate {
  status?: BookIssueStatus;      // max 20
  current_sheet?: number;        // ge=0
  completion_date?: string | null;
  remarks?: string | null;       // max 255
}

// GET /token-books/issues/ — flat list DTO
export interface TokenBookIssueListResponse {
  id: number;
  token_identity_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  milk_type_name: string;
  token_number: number;
  issue_number: number;
  issue_date: string;
  status: string;
  current_sheet: number;
  is_active: boolean;
}

// GET /token-books/issues/{id} — nested detail DTO (edit form hydration)
export interface TokenBookIssueDetailResponse {
  id: number;
  token_identity: TokenIdentitySummaryResponse;
  issue_number: number;
  issue_date: string;
  completion_date: string | null;
  current_sheet: number;
  status: string;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// POST /token-books/issues/, PUT/DELETE /token-books/issues/{id},
// GET /token-books/issues/identity/{id}
export interface TokenBookIssueResponse {
  id: number;
  token_identity_id: number;
  issue_number: number;
  issue_date: string;
  completion_date: string | null;
  current_sheet: number;
  status: string;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Nested summary used by payment detail DTO
export interface TokenBookIssueSummaryResponse {
  id: number;
  token_identity: TokenIdentitySummaryResponse;
  issue_number: number;
  status: string;
}
```

## Token Book Payment (`token-book.ts`)

> `payment_status` (PAID | PARTIAL | PENDING) and `balance_amount` (book_price − amount_paid) are **computed server-side** on create and update — the client only sends the raw inputs. `amount_paid` > `book_price` is rejected (400).

```typescript
export interface TokenBookPaymentCreate {
  token_book_issue_id: number;  // gt=0
  payment_mode: TokenPaymentMode; // max 20
  book_price: number;           // gt=0
  amount_paid: number;          // default 0, ge=0
  remarks?: string | null;      // max 255
}

export interface TokenBookPaymentUpdate {
  payment_mode?: TokenPaymentMode;   // max 20
  payment_status?: BookPaymentStatus; // max 20
  book_price?: number;               // gt=0
  amount_paid?: number;              // ge=0
  remarks?: string | null;           // max 255
}

// GET /token-books/payments/ — flat list DTO
export interface TokenBookPaymentListResponse {
  id: number;
  token_book_issue_id: number;
  customer_id: number;
  customer_code: string;
  customer_name: string;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  is_active: boolean;
}

// GET /token-books/payments/{id} — nested detail DTO (edit form hydration)
export interface TokenBookPaymentDetailResponse {
  id: number;
  token_book_issue: TokenBookIssueSummaryResponse;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  collected_by: number | null;
  remarks: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// POST /token-books/payments/, PUT/DELETE /token-books/payments/{id},
// GET /token-books/payments/issue/{id}
export interface TokenBookPaymentResponse {
  id: number;
  token_book_issue_id: number;
  payment_mode: string;
  payment_status: string;
  book_price: number;
  amount_paid: number;
  balance_amount: number;
  payment_date: string;
  collected_by: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

## State Transitions

| Entity | Source State | Trigger | Target State |
|---|---|---|---|
| Token Identity | active | deactivate (soft delete) | `is_active=false` (no reactivation this phase) |
| Token Book Issue | WAITING | set to ACTIVE (form) | ACTIVE |
| Token Book Issue | ACTIVE | set to COMPLETED (form) | COMPLETED |
| Token Book Issue | any | deactivate (soft delete) | `is_active=false` (removed from list — backend filters `is_active=true`) |
| Token Book Payment | any | deactivate (soft delete) | `is_active=false` (removed from list) |

## Validation Rules (client mirrors)

| Field | Rule | Enforced |
|---|---|---|
| `token_number` | > 0, unique per customer (reusable across a customer's milk types; must not be used by another active customer) | client + server |
| `issue_number` | > 0, unique per identity | client + server |
| one active book per identity | cannot create issue with `status="ACTIVE"` already present | server (client offers only identities without an active book) |
| `book_price` | > 0 | client + server |
| `amount_paid` | >= 0 and <= `book_price` | client + server |
| `payment_mode` | one of PREPAID, POSTPAID | client (select) + server (string length) |
| `status` (issue) | one of WAITING, ACTIVE, COMPLETED | client (select) + server (string length) |
