# Research: Token Book Pages

> Phase 0 output for `specs/006-token-books`. Consolidates decisions on the unknowns and technology choices for this feature. Derived from verification against the backend (`app/routers/token_books.py`, `app/services/token_book_service.py`, `app/schemas/token_identity.py`, `app/schemas/token_book.py`) and the parent feature `004-react-frontend` plan artifacts (2026-07-31).

## Technology Decisions

### Reuse established frontend stack
- **Decision**: No new libraries. Use the existing React 19 / Vite 8 / TypeScript 6 / Tailwind 4 / TanStack Query v5 / axios / react-hot-toast stack already installed in `frontend/package.json`.
- **Rationale**: Phases 1–3 of the parent feature established working patterns (types → api → hooks → pages) with these libraries. Introducing anything new would violate the constitution's tech-stack gate.
- **Alternatives considered**: A component library (shadcn/Radix) — rejected; parent spec resolved pure Tailwind primitives.

### Response handling — plain array lists
- **Decision**: `GET /token-books/identities/`, `/issues/`, and `/payments/` are typed as direct arrays and rendered in full by the existing DataTable.
- **Rationale**: Verified `response_model=list[...]` on all three list endpoints in `app/routers/token_books.py`. No pagination envelope, so no pagination wiring.
- **Alternatives considered**: Paginated envelope — rejected (fields do not exist); client-side pagination — rejected (expected volume < 2,000).

### List vs Detail DTO split
- **Decision**: Two interface shapes per module. List shape = flat joined fields (`customer_code`, `customer_name`, `milk_type_name`/`milk_type_volume`, `token_number`, `issue_number`, `status`, `current_sheet`, `book_price`, `amount_paid`, `balance_amount`). Detail shape = nested objects (`customer`/`milk_type` for identities; `token_identity` for issues; `token_book_issue` for payments).
- **Rationale**: The backend defines distinct `*ListResponse` and `*DetailResponse` schemas (verified). The table renders the list DTO; the edit form hydrates from the detail endpoint. `MilkTypeSummaryResponse.unit_price` defaults to `0` server-side when omitted, so the nested detail endpoints validate cleanly.
- **Alternatives considered**: One unified interface with all-optional fields — rejected (loses type safety, contradicts Schema-Driven Contracts).

### Token identity create/update field sets
- **Decision**: `TokenIdentityCreate` sends `customer_id`, `milk_type_id`, `token_number`. `TokenIdentityUpdate` sends **only** `token_number` — customer and milk type are immutable after creation.
- **Rationale**: Verified against `app/schemas/token_identity.py`. Update schema has a single field.
- **Alternatives considered**: Sending customer/milk type on update — rejected; would be ignored or 422.

### Token book issue fields
- **Decision**: `TokenBookIssueCreate` sends `token_identity_id`, `issue_number`, `remarks` (optional). `TokenBookIssueUpdate` sends `status`, `current_sheet`, `completion_date`, `remarks` — only the values the user changes.
- **Rationale**: Verified against `app/schemas/token_book.py`. The backend assigns `issue_date` (now), `current_sheet` (0), and `status` ("WAITING") on create; `book_number` and `total_sheets` (30) are backend-internal and never returned in response schemas.
- **Alternatives considered**: Sending `issue_date`/`current_sheet` on create — rejected; would 422 (unknown/ignored fields).

### Book issue status values
- **Decision**: Add a `BOOK_ISSUE_STATUS` constant (`WAITING` | `ACTIVE` | `COMPLETED`) to `frontend/src/lib/constants.ts` and merge it into `STATUS_BADGE_MAP`.
- **Rationale**: The model defaults status to `WAITING`; `create_book_issue` enforces one active book per identity by checking `status == "ACTIVE"`; completion is `COMPLETED`. `STATUS_BADGE_MAP` currently lacks `WAITING`/`COMPLETED` badges.
- **Alternatives considered**: Reusing only the existing `ACTIVE` badge — rejected; would render unknown-status rows without a badge.

### Token book payment fields
- **Decision**: `TokenBookPaymentCreate` sends `token_book_issue_id`, `payment_mode` (PREPAID | POSTPAID), `book_price` (> 0), `amount_paid` (>= 0, default 0), `remarks` (optional). `TokenBookPaymentUpdate` sends `payment_mode`, `payment_status`, `book_price`, `amount_paid`, `remarks`.
- **Rationale**: Verified against `app/schemas/token_book.py`. The backend computes `payment_status` (PAID / PARTIAL / PENDING) and `balance_amount` (book_price − amount_paid) on create and update; `amount_paid` > `book_price` is rejected with 400. `TOKEN_PAYMENT_MODES = ["PREPAID", "POSTPAID"]` already exists in `frontend/src/lib/constants.ts`; `PAYMENT_STATUS` already exists.
- **Alternatives considered**: Computing balance client-side — rejected; the server is authoritative and returns `balance_amount` in every list/detail DTO.

### Filtering strategy
- **Decision**: Customer/milk-type filter on identities, customer/identity filter on issues, and issue filter on payments are all **client-side** over the returned flat arrays.
- **Rationale**: `GET /identities/customer/{id}` and `GET /issues/identity/{id}` exist but return a different, non-flat DTO shape; list endpoints accept no query params. Client-side filtering over the flat list DTOs matches the 005 pattern for cross-field filters.
- **Alternatives considered**: Dedicated filtered endpoints — rejected; response shapes differ from the list DTOs and would require two data sources.

### CHECKER read-only (RBAC)
- **Decision**: List routes registered under ProtectedRoute (OWNER/ADMIN/CHECKER); create/edit routes wrapped in `RoleGuard` with `roles=["OWNER", "ADMIN"]`. Action buttons and edit/delete links conditionally rendered only when `user.role !== "CHECKER"`. Sidebar nav roles updated to grant CHECKER read-only access to Token Identities and Token Book Issues (Token Payments already includes CHECKER).
- **Rationale**: Spec FR-021/FR-022 require CHECKER read-only on all three lists (US-033: verify token sheets during registration). Server enforces authorization regardless; the UI guards are UX. Parent nav scaffolding currently restricts identities/issues to OWNER/ADMIN only.
- **Alternatives considered**: Restricting CHECKER to payments only — rejected; contradicts spec FR-021 and US-033.

## Edge Cases from Spec

| Edge Case | Approach |
|-----------|----------|
| Duplicate token number for same customer + milk type | Backend 400; surface as error toast; form stays open |
| Duplicate issue number for same identity | Backend 400; toast |
| Second active issue on an identity | Backend 400 (`ActiveBookExists`); toast; identity selector only offers identities with no active ACTIVE book |
| Payment amount > book price | Backend 400; toast + inline hint; prevent submission client-side |
| Payment on deactivated issue | Form only offers active issues (filter `is_active` from issue list); backend 404 otherwise |
| Empty lists | Existing `EmptyState` component ("No records found") with Create button when permitted |
| Deactivated records | INACTIVE badge via existing `Badge`/`getStatusColor`; soft-delete only (backend returns only `is_active=true` rows, so deactivated records disappear from the list — no INACTIVE rows expected in practice) |
| CHECKER reaches create/edit URL directly | `RoleGuard` renders `ForbiddenPage` (403) |
| Negative token/issue numbers, zero/negative prices | Inline validation in the forms; backend also enforces (`gt=0` / `ge=0`) |
| Backend unavailable | TanStack Query retries (default 3), then error toast per parent spec NFR-3 |
