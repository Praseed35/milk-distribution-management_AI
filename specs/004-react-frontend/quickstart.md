# Quickstart: React Frontend Validation Guide

> Runnable validation scenarios to prove the frontend works end-to-end.

## Prerequisites

- Backend running at `http://localhost:8000`
- Database seeded with test data (`python scripts/seed.py`)
- Node.js 18+ installed

## Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at `http://localhost:5173`. Vite proxy forwards `/api/*` → `http://localhost:8000`.

---

## Validation Scenarios

### V1: Backend Health Check (before frontend)

```bash
# CORS check
curl -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:8000/api/v1/health

# Expected: 200 with Access-Control-Allow-Origin header

# Health endpoint
curl http://localhost:8000/api/v1/health

# Expected: {"status": "ok", "version": "1.0.0", "timestamp": "..."}
```

### V2: Login Flow (end-to-end)

1. Navigate to `http://localhost:5173`
2. You should be redirected to `/login`
3. Enter credentials: `owner` / `owner123`
4. Click Login
5. **Expected**: Redirected to dashboard, JWT stored in localStorage (`auth_token`), sidebar shows all navigation links

### V3: Role-Based Routing

1. Log out
2. Log in as `delivery1` / `delivery123` (DELIVERY_PARTNER)
3. **Expected**: Sidebar shows limited links (Dashboard, Session Checklist)
4. Navigate to `/routes` manually
5. **Expected**: Redirected to dashboard or shown 403 page

### V4a: Master Data CRUD (Routes) ✅ Working

1. Log in as owner
2. Navigate to Routes page
3. **Expected**: Table showing R001-R005
4. Click "Create Route"
5. Fill form: `R006`, `New Test Route`
6. Submit
7. **Expected**: Route appears in table, toast shows success
8. Click edit on R006, change name, submit
9. **Expected**: Name updated in table
10. Delete R006
11. **Expected**: Confirm dialog appears, after confirm route disappears (soft delete)

### V4b: Master Data CRUD (Customers) ✅ Working

1. Navigate to Customers page
2. **Expected**: Table showing C00001-C00015
3. Create/Edit/Detail links all functional

### V4c: Master Data CRUD (Milk Types) ✅ Working

1. Navigate to Milk Types page
2. **Expected**: Table showing 7 milk types
3. Create/Edit with volume and price validation

### V4d: Master Data CRUD (Employees) ✅ Working

1. Navigate to Employees page
2. **Expected**: Table showing E00001-E00005
3. Credentials management page accessible

### V4e: Master Data CRUD (Users) ✅ Working

1. Navigate to Users page
2. **Expected**: Table showing system users
3. Create new user with role/password

### V4f: Subscriptions (Phase 3)

1. Log in as owner
2. Navigate to Subscriptions page (`/subscriptions`)
3. **Expected**: Table showing existing subscriptions with customer name/code, route, milk type (name + volume), morning/evening qty, status badge
4. Click "Create Subscription"
5. Fill form: select customer, select milk type, morning qty 2, evening qty 1
6. Submit
7. **Expected**: New subscription appears in list (status ACTIVE), toast "Subscription created"
8. Edit the subscription, change morning quantity, submit
9. **Expected**: Quantity updates in list
10. Delete the subscription
11. **Expected**: Confirm dialog, then row shows Inactive (or disappears — soft delete)
12. **API note**: `POST /subscriptions` body must NOT include `start_date`/`end_date` — server assigns them. Sending them yields 422.

### V4g: Delivery Exceptions (Phase 3)

1. Navigate to Exceptions page (`/delivery-exceptions`)
2. **Expected**: Table showing exceptions with customer, route, type, date range, status
3. Click "Create Exception"
4. Fill form: select subscription (customer + milk info shown), type VACATION, start date today, optional end date/reason
5. Submit
6. **Expected**: New exception appears, toast "Exception created"
7. Edit an exception (change end date), submit
8. **Expected**: Date updates
9. Delete an exception
10. **Expected**: Confirm dialog, then soft delete
11. **Edge cases**: Overlapping date range for same subscription → 400 toast "overlaps with an existing exception"; inactive subscription → 400 toast.

### V4h: CHECKER Read-Only (Phase 3)

1. Log out, log in as a CHECKER user
2. Navigate to Subscriptions and Exceptions
3. **Expected**: Lists render, **no** Create/Edit/Delete buttons or links visible
4. Manually navigate to `/subscriptions/new`
5. **Expected**: 403 Forbidden page (RoleGuard)
6. Sidebar Operations group shows Subscriptions/Exceptions for CHECKER

### V5: Delivery Session Workflow (Pending — Phase 5)

### V6: Payment Recording (Pending — Phase 6)

### V7: Report Dashboard (Pending — Phase 7)

### V8: 401 Redirect

1. Open browser DevTools → Application → Local Storage
2. Delete `auth_token`
3. Make any action (navigate or click)
4. **Expected**: Redirected to `/login`, toast "Session expired"

### V9: Error Toast

1. Navigate to Routes
2. Stop the backend server
3. Try to load the page
4. **Expected**: Error toast "Server error. Please try again." after retries exhausted

### V10: Responsive Layout

1. Open on desktop (1920px) → sidebar visible, content fills remaining space
2. Resize to tablet (768px) → sidebar collapses, hamburger icon appears
3. Resize to mobile (375px) → tables horizontally scrollable, forms stack vertically
