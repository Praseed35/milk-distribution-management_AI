# BUSINESS_RULES.md - Business Domain Rules

> All verified business rules enforced in the codebase.

---

## 1. Milk Distribution Business Model

A milk distribution business delivers milk to customers on fixed routes. Customers subscribe to milk types (e.g., "Full Cream Milk 1000ml") and specify daily quantities for morning and evening shifts. Delivery partners carry physical "token books" - prepaid booklets that customers exchange for milk.

### Key Concepts

- **Route**: A geographical delivery zone grouping customers
- **Customer**: A household receiving milk deliveries, assigned to one route
- **Milk Type**: A product with name and volume (e.g., "Toned Milk 500ml")
- **Subscription**: A customer's recurring order linking to a milk type with shift quantities
- **Delivery Exception**: A temporary pause (vacation, holiday) affecting a subscription
- **Token Identity**: A unique token number assigned to a customer for a specific milk type
- **Token Book**: A physical book of sheets issued to a customer, tracked by issue number
- **Token Book Payment**: Payment record for a token book (can be prepaid, partial, or postpaid)

---

## 2. Customer Management Rules

1. **Auto-generated codes**: Customer codes are `C{NNNNN}` (e.g., C00001), auto-incremented from the highest existing ID
2. **Unique phone**: primary_phone must be unique across all customers
3. **Phone validation**: primary_phone and alternate_phone must be 10 characters exactly
4. **Different phones**: primary_phone and alternate_phone cannot be the same
5. **Route required**: Every customer must be assigned to a valid, active route
6. **Soft delete**: Customers are never physically deleted, only deactivated (is_active=False)

---

## 3. Route Management Rules

1. **Unique code**: route_code must be unique
2. **Unique name**: route_name must be unique
3. **Active check**: Cannot assign inactive route to customer or employee
4. **Soft delete**: Routes are deactivated, not deleted

---

## 4. Milk Type Rules

1. **Unique name**: milk_name must be unique
2. **Positive volume**: volume_ml must be > 0
3. **Soft delete**: Milk types are deactivated, not deleted

---

## 5. Employee Management Rules

1. **Auto-generated codes**: Employee codes are `E{NNNNN}`
2. **Unique phone**: Phone must be unique
3. **Optional user link**: Employee can optionally have a linked User account
4. **All-or-nothing credentials**: If providing username during creation, must also provide password and confirm_password (and vice versa)
5. **OWNER-only creation**: Only OWNER role can create employees or update credentials
6. **Route validation**: If route_id provided, route must exist and be active
7. **Username uniqueness**: If creating a linked user, username must not already exist

---

## 6. Subscription Rules

1. **Unique active subscription**: Only one active subscription per customer + milk_type combination
2. **Quantity validation**: At least one of morning_quantity or evening_quantity must be > 0
3. **Active customer required**: Cannot create subscription for inactive customer
4. **Active milk type required**: Cannot create subscription with inactive milk type
5. **Status default**: New subscriptions default to status="ACTIVE"
6. **Deactivation**: DELETE sets is_active=False AND status="INACTIVE"
7. **Update validation**: After update, quantities cannot both be 0

---

## 7. Delivery Exception Rules

1. **Active subscription required**: Cannot create exception for inactive subscription
2. **Date validation**: end_date must be >= start_date
3. **No overlaps**: Cannot create overlapping exceptions for the same subscription
4. **Single-day exception**: If end_date is null, it's a single-day exception (start_date == end_date for overlap check)
5. **Overlap detection logic**: Two date ranges overlap if: `start_A <= end_B AND end_A >= start_B`
6. **Shift scoping (since migration a1b2c3d4e5f6)**: `shift` is optional (MORNING/EVENING). When set, the exception applies only to that shift; when null, it applies to the whole day. Overlap rules: same-shift exceptions cannot overlap; a whole-day exception cannot overlap another whole-day exception or any shift exception on the same dates; exceptions on different shifts can coexist on the same dates.
7. **Checklist effect**: Session checklist generation excludes customers with an ACTIVE exception where `start_date ≤ session.delivery_date ≤ COALESCE(end_date, session.delivery_date)` and `shift IS NULL OR shift = session.shift`
8. **Status**: Defaults to "ACTIVE", cancellation sets status="CANCELLED"
9. **Exception types**: VACATION, NO_MILK, HOLIDAY (defined in constants but stored as string)

---

## 8. Token Identity Rules

1. **Composite uniqueness**: (customer_id, milk_type_id, token_number) must be unique
2. **Active customer required**: Customer must exist and be active
3. **Active milk type required**: MilkType must exist and be active
4. **Token number**: Positive integer
5. **Update restriction**: Only token_number can be updated (customer and milk_type are immutable)

---

## 9. Token Book Issue Rules

1. **One active book per identity**: Cannot issue a new book if one is already ACTIVE for the same token_identity_id
2. **Unique issue_number**: Issue number must be unique per token identity
3. **Default status**: New issues start with status="WAITING"
4. **Status lifecycle**: WAITING -> ACTIVE -> COMPLETED
5. **current_sheet**: Starts at 0, incremented as sheets are used

---

## 10. Token Book Payment Rules

1. **Amount validation**: amount_paid cannot exceed book_price
2. **Auto-calculation**: balance_amount = book_price - amount_paid
3. **Auto status determination**:
   - balance_amount <= 0 -> "PAID"
   - amount_paid > 0 AND balance_amount > 0 -> "PARTIAL"
   - amount_paid == 0 -> "PENDING"
4. **Payment modes**: PREPAID or POSTPAID
5. **Recalculation on update**: When payment is updated, balance and status are always recalculated

---

## 11. Authentication Rules

1. **JWT expiry**: Tokens expire after 30 minutes
2. **Algorithm**: HS256
3. **Token payload**: {sub: username, role: role, exp: datetime}
4. **Password hashing**: bcrypt via passlib
5. **Password validation**: Minimum 6 characters for change-password
6. **Change password**: Must provide current password, new password must differ from current, confirm must match

---

## 12. Authorization Rules

1. **Role hierarchy**: OWNER > CHECKER > DELIVERY_PARTNER > EMPLOYEE
2. **Enforcement**: Only employee CRUD (create, credentials) and owner-dashboard check roles
3. **Default**: Most endpoints have no role restriction
4. **Access denied**: Returns HTTP 403 with "Access denied" message

---

## 13. Delivery Session Rules

1. **Unique session**: Only one session per (route_id, delivery_date, shift) combination
2. **Session state machine**:
   - PLANNED -> STARTED (via dispatch/start)
   - STARTED -> COMPLETED (manual completion)
   - COMPLETED -> CLOSED (via close, requires balanced reconciliation)
   - CLOSED -> COMPLETED (via reopen, owner only)
3. **Dispatch can only be recorded once** per session
4. **Optimistic locking**: Session and delivery records have a `version` column incremented on each write; concurrent edits raise `ConcurrentEditError`
5. **Reopen tracking**: Sessions track `reopened_by`, `reopened_at`, and `reopen_count`
6. **All edits are audited**: Every status change creates a `SessionEdit` record with old/new JSONB snapshots

## 14. Delivery Registration Rules

1. **Delivery statuses**: DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED
2. **Delivery sources**: PLANNED (from subscription) or UNPLANNED (walk-in/phone order)
3. **Unplanned deliveries** require a reason and can be registered as TOKEN_SHEET, CASH, or PENDING
4. **Token registration** sets delivery_status to DELIVERED and delivered_quantity to planned_quantity
5. **Token sheet validation** rules:
   - Must have an active token book for the customer + milk_type
   - Sheet number must be within book range (1 to total_sheets)
   - Sheet must not already be used (checked against daily_deliveries with DELIVERED status)
   - Non-sequential sheets (skipping ahead) generate NON_SEQUENTIAL_SHEET warning
   - Out-of-order sheets (using old sheet) generate SHEET_OUT_OF_ORDER warning
   - Old books with remaining sheets generate NEW_BOOK_BEFORE_OLD_FINISHED warning
   - Warnings require acknowledgment before proceeding

## 15. Reconciliation Rules

1. **Formula**: `difference = loaded_milk - (token_registered + cash_sales + returned_milk)`
2. **Balanced check**: `|difference| < 0.01` (tolerance for floating point)
3. **Cannot close** an unbalanced session (raises `SessionNotBalancedError`)
4. **Cannot close** an already closed session (raises `SessionAlreadyClosedError`)
5. **Cash sales** can be added/removed during reconciliation; stored as DailyDelivery with CASH_SALE status
6. **Reconciliation validation** checks for pending tokens and mismatches before allowing close

## 16. Delivery Edit Rules

1. **Only Owner** can reopen closed sessions (`OwnerRequiredError`)
2. **Only Owner** can edit deliveries within a reopened session
3. **Reopening** changes session status from CLOSED to COMPLETED
4. **Token sheet return**: When undoing a delivery, the token sheet is returned to the customer (book.current_sheet decremented)
5. **Edit history** is available via `GET /deliveries/session/{session_id}/edit-history`
6. **Authentication**: `edit_delivery` and `reopen_session` require an authenticated user (`get_current_user`); the user id is recorded in the `session_edits` audit trail. (Previously hardcoded `user_id=1` — **FIXED July 29, 2026**)

## 17. Soft Delete Pattern

All entities use soft delete:
1. Every table has `is_active = Boolean, default=True`
2. DELETE endpoints set `is_active = False`
3. All read queries filter `is_active == True`
4. Some entities also set a status field on deactivation:
   - Subscription -> "INACTIVE"
   - DeliveryException -> "CANCELLED"
5. Records are never physically deleted from the database
6. **Exception**: `session_edits` table has NO is_active — it's an immutable audit trail

## 18. Customer Payment Rules (Sprint 6)

1. **Valid payment modes**: CASH, UPI, CARD, CHEQUE, BANK_TRANSFER
2. **Valid payment types**: ADVANCE or BILL_PAYMENT
3. **Active customer required**: Cannot create a payment for an inactive/missing customer
4. **BILL_PAYMENT requires a bill**: `bill_id` is mandatory; the bill must exist, be active, not CANCELLED (`BillAlreadyCancelledError`), and not PAID (`BillAlreadyPaidError`)
5. **ADVANCE payments** are never linked to a bill (`bill_id` forced to None)
6. **Auto recalculation**: Creating/updating/deactivating a BILL_PAYMENT recalculates its bill:
   - `paid_amount` = sum of active payments on the bill
   - `balance_amount` = `total_amount - paid_amount`
   - status auto-set: PAID if balance <= 0, PARTIAL if paid > 0, else PENDING
7. **Deactivation**: DELETE soft-deletes the payment (`is_active=False`) and recalculates the linked bill
8. **Filtering**: List endpoint supports filters by customer_id, payment_mode, payment_type, from_date, to_date

## 19. Customer Bill Rules (Sprint 6)

1. **Bill generation** aggregates daily deliveries for a customer where `delivery_status` in (DELIVERED, CASH_SALE) and the session's `delivery_date` is within `bill_period_start`..`bill_period_end`
2. **Line items**: Grouped by milk_type_id; each `CustomerBillItem` has quantity, unit_price (from the milk type's current `unit_price`), and amount
3. **Total**: `total_amount` = sum of all line-item amounts
4. **No deliveries in period**: Raises `NoDeliveriesForBillError` — a bill cannot be generated for an empty period
5. **Initial state**: `status="PENDING"`, `paid_amount=0`, `balance_amount=total_amount`
6. **Valid bill statuses**: PENDING, PARTIAL, PAID, OVERDUE, CANCELLED (status can be set explicitly via update endpoint; PAID/PARTIAL/PENDING are also auto-derived from payments)
7. **Outstanding balance**: `balance = sum(billed for PENDING/PARTIAL/OVERDUE bills) - sum(all active payments)`; response also includes last bill date and last payment date

## 20. Report & Analytics Rules (Sprint 7)

1. **Report types**: route-wise (daily/weekly/monthly), customer consumption, revenue, collection efficiency, token book utilization, operational dashboard
2. **Response envelope**: `{data, total, page, page_size, generated_at}`; `?format=csv` returns CSV instead of JSON
3. **Caching**: In-memory cache keyed by report parameters; cache-busting via `?refresh=true`
4. **RBAC**: Report endpoints use `require_role` per endpoint — e.g., route-delivery requires OWNER; collection-efficiency and token-utilization allow OWNER/ADMIN; customer-consumption allows OWNER/ADMIN/CHECKER; the operational dashboard is the most permissive (includes DELIVERY_PARTNER)
