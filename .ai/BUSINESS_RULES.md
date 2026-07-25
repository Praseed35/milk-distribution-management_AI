# Business Rules: Milk Management AI

## Domain Overview

This system manages a **milk distribution business** operating on a subscription model. Customers subscribe to milk types, receive deliveries on scheduled routes during morning/evening shifts, and are billed based on delivered quantities.

---

## Master Data Rules

### Routes
1. Each route has a **unique code** and **unique name** (e.g., "Downtown", "RT001")
2. Routes can be soft-deleted (deactivated) but not hard-deleted
3. Customers must belong to an **active route**
4. An inactive route cannot have new customers or subscriptions created against it

### Milk Types
1. Each milk type has a **unique name** (e.g., "Full Cream 1000ml")
2. Volume must be positive (in milliliters)
3. Milk types can be soft-deleted (deactivated)
4. An inactive milk type cannot be used in new subscriptions

### Customers
1. Each customer gets an **auto-generated code**: `C00001`, `C00002`, etc. (sequential, zero-padded to 5 digits)
2. `primary_phone` must be **exactly 10 digits** and globally unique
3. `alternate_phone` (if provided) must be **exactly 10 digits** and **different from primary_phone**
4. Each customer belongs to exactly one active route
5. Customer codes are sequential across the entire system (not per-route)
6. Soft-deleting a customer does not cascade-deactivate subscriptions

### Users
1. Username must be unique
2. Passwords are bcrypt-hashed before storage
3. Roles: `OWNER`, `CHECKER`, `DELIVERY_PARTNER` (enum defined but only string-validated in model)
4. No timestamps tracked on user records

---

## Subscription Rules

1. A subscription links a **customer** to a **milk type** with morning and evening quantities
2. A customer can only have **one active subscription per milk type** (no duplicates)
3. At least one of `morning_quantity` or `evening_quantity` must be > 0
4. Both quantities must be >= 0 (no negative values)
5. Deactivation sets `is_active=False` and `status="INACTIVE"` (soft-delete)
6. After deactivation, the customer can re-subscribe to the same milk type
7. Subscriptions can be updated (partial update — only non-null fields changed)
8. Both customer and milk type must be **active** to create a subscription

---

## Authentication & Authorization Rules

1. Authentication is JWT-based (HS256, 30-minute expiry)
2. JWT payload contains `sub` (username) and `role`
3. `get_current_user` dependency decodes JWT and fetches user from DB
4. `require_role(["ROLE"])` factory creates role-checking dependencies
5. Only `/auth/me` and `/auth/owner-dashboard` are auth-protected currently
6. **All other endpoints are unprotected** (no auth dependency applied)

---

## Token Accounting Rules (Planned)

1. Tokens represent milk delivery entitlements per customer per shift
2. A token can be: COLLECTED, PENDING, or CARRY_FORWARD
3. Daily token settlement tracks what was delivered vs. what was owed
4. Pending tokens carry forward to the next day
5. Cash sales are separate from token-based deliveries

---

## Delivery Workflow Rules (Planned)

1. Morning and evening shifts are independent
2. Each shift has its own milk allocation per route
3. Delivery partners record deliveries per customer per shift
4. Checker verifies delivered quantities against subscriptions
5. Discrepancies trigger reconciliation workflow

---

## Payment & Reconciliation Rules (Planned)

1. Payment statuses: PAID, PENDING, PARTIAL
2. Reconciliation matches subscriptions against actual deliveries
3. Customer pays based on delivered quantities (not subscribed quantities)
4. Advance credits can be applied to future deliveries

---

## Session/Route Status Workflow (Planned)

```
PLANNED → STARTED → COMPLETED → CLOSED
```

1. A delivery session starts as PLANNED
2. When route delivery begins, status moves to STARTED
3. After all deliveries on route are completed → COMPLETED
4. After financial reconciliation → CLOSED

---

## Data Integrity Rules

1. All entities use **soft-delete** (`is_active` flag) — no hard deletes
2. Foreign keys are validated at the service layer (not DB-level cascades)
3. Duplicate detection is done by querying before insert/update
4. `customer_code` generation queries the last record — potential race condition under concurrent creates
5. Timestamps are server-generated (`server_default=func.now()`)
