---

description: "Task list for React Frontend feature implementation"
---

# Tasks: React Frontend for Milk Distribution ERP

**Input**: Design documents from `specs/004-react-frontend/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/README.md, quickstart.md

**Tests**: No test tasks included — frontend testing deferred to Phase 8 per spec.

**Organization**: Tasks grouped by the 8 implementation phases from the spec. Within each phase, groups of related user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `app/main.py`, `app/core/config.py`
- **Frontend**: `frontend/src/` (all frontend code under this directory)
- TypeScript files use `.ts` or `.tsx` extension

---

## ✅ Phase 1: Setup — Backend Prep + Frontend Scaffold + Auth

**Purpose**: Backend CORS/prefix/health, frontend project init, auth flow, and app layout.

**No story labels** — these are setup/foundational tasks.

- **All 39 Phase 1 tasks complete. Build passes cleanly.**

### Backend Changes

- [x] T001 Add `CORSMiddleware` to `app/main.py` allowing `http://localhost:5173` with credentials, all methods/headers
- [x] T002 [P] Create umbrella `api_v1 = APIRouter(prefix="/api/v1")` in `app/main.py`, include all sub-routers under it
- [x] T003 [P] Add `GET /api/v1/health` endpoint in `app/main.py` returning status, version, timestamp
- [x] T004 Move existing root-level `app.include_router(...)` calls to use `api_v1.include_router(...)` pattern in `app/main.py`
- [x] T005 Add deprecation comment on legacy root-level route registration in `app/main.py`

### Frontend Scaffold

- [x] T006 Create `frontend/` directory with `npm create vite@latest frontend -- --template react-ts`
- [x] T007 Install dependencies: `react-router-dom`, `axios`, `@tanstack/react-query`, `@tanstack/react-query-devtools`, `react-hot-toast`, `@sentry/react`, `tailwindcss`, `@tailwindcss/vite`
- [x] T008 Configure Vite proxy in `frontend/vite.config.ts` — proxy `/api` to `http://localhost:8000`, port 5173
- [x] T009 [P] Configure Tailwind CSS v4 with `@tailwindcss/vite` plugin in `frontend/vite.config.ts` and `@import "tailwindcss"` in `frontend/src/index.css`
- [x] T010 [P] Create folder structure under `frontend/src/`: `api/`, `components/ui/`, `components/layout/`, `components/guards/`, `hooks/`, `pages/`, `providers/`, `types/`, `config/`, `lib/`
- [x] T011 Create `frontend/src/lib/constants.ts` with status enum mappings and color configurations per spec UI section
- [x] T012 Create `frontend/src/lib/utils.ts` with helper functions (`cn()` classname merger, `formatDate()`, `formatCurrency()`)

### Auth Foundation

- [x] T013 Create `frontend/src/types/auth.ts` with `LoginRequest`, `LoginResponse`, `User`, `UserRole`, `ChangePasswordRequest` interfaces
- [x] T014 Create `frontend/src/types/common.ts` with `ApiResponse`, `PaginatedResponse`, `ApiError`, `DateRangeParams` interfaces
- [x] T015 Create Axios instance in `frontend/src/api/client.ts` with baseURL `/api/v1`, timeout 30s, and request/response interceptors for JWT auth + 401 handling
- [x] T016 Create `frontend/src/api/auth.ts` with `login()`, `getMe()`, `changePassword()` API functions
- [x] T017 Create `AuthProvider` in `frontend/src/providers/AuthProvider.tsx` with context for user, token, login, logout, isAuthenticated; restore token from localStorage on mount
- [x] T018 Create `QueryProvider` in `frontend/src/providers/QueryProvider.tsx` wrapping TanStack Query with devtools
- [x] T019 Initialize Sentry in `frontend/src/main.tsx` with `@sentry/react` for error monitoring
- [x] T020 Create `frontend/src/pages/LoginPage.tsx` with username + password form, POST to `/api/v1/auth/login`, store token, redirect to dashboard
- [x] T021 Create `frontend/src/pages/ChangePasswordPage.tsx` with current/new/confirm password form

### Layout & Routing

- [x] T022 Create `frontend/src/components/guards/ProtectedRoute.tsx` — checks isAuthenticated, redirects to `/login` with return URL saved to sessionStorage
- [x] T023 Create `frontend/src/components/guards/RoleGuard.tsx` — checks user role against allowed roles, shows 403 page if unauthorized
- [x] T024 Create `frontend/src/components/layout/Sidebar.tsx` — collapsible sidebar with role-filtered navigation links using a permissions config
- [x] T025 Create `frontend/src/components/layout/Header.tsx` — top bar with page title, user info, logout button
- [x] T026 Create `frontend/src/components/layout/AppLayout.tsx` — sidebar + header + main content area wrapper
- [x] T027 Create `frontend/src/config/permissions.ts` — role-permission mapping for all modules and routes
- [x] T028 Create `frontend/src/pages/NotFoundPage.tsx` — 404 page
- [x] T029 Create `frontend/src/pages/ForbiddenPage.tsx` — 403 page
- [x] T030 Wire up `App.tsx` with React Router, AuthProvider, QueryProvider, routes for login, dashboard, change-password, and all protected route groups

### UI Primitive Components

- [x] T031 [P] Create `frontend/src/components/ui/Button.tsx` with variants (primary, secondary, danger, ghost), sizes, loading spinner state
- [x] T032 [P] Create `frontend/src/components/ui/Input.tsx` with label, error message display, required indicator
- [x] T033 [P] Create `frontend/src/components/ui/Select.tsx` with options, placeholder, error display
- [x] T034 [P] Create `frontend/src/components/ui/Badge.tsx` with status-to-color mapping for delivery/session/payment statuses
- [x] T035 [P] Create `frontend/src/components/ui/DataTable.tsx` with sorting, pagination, loading skeleton, empty state, error state
- [x] T036 [P] Create `frontend/src/components/ui/ConfirmDialog.tsx` for destructive action confirmations
- [x] T037 [P] Create `frontend/src/components/ui/PageHeader.tsx` with title, description, and action buttons slot
- [x] T038 [P] Create `frontend/src/components/ui/LoadingSpinner.tsx` for async operations
- [x] T039 [P] Create `frontend/src/components/ui/EmptyState.tsx` with message, icon, and optional CTA button

**Checkpoint**: Backend accessible at `/api/v1/health`, frontend runs at `:5173`, login flow works end-to-end, sidebar navigation renders for each role.

---

## ✅ Phase 2: Master Data Pages (US-010, US-011, US-012, US-013, US-014)

**Purpose**: List/create/edit/delete pages for routes, customers, milk types, employees, and users.

- **All 30 Phase 2 tasks complete. Build passes cleanly.**

### Routes (US-010)

- [x] T040 Create `frontend/src/types/route.ts` with `RouteCreate`, `RouteUpdate`, `RouteResponse` interfaces
- [x] T041 Create `frontend/src/api/routes.ts` with CRUD API functions
- [x] T042 Create `frontend/src/hooks/useRoutes.ts` with TanStack Query hooks (`useRoutes`, `useRoute`, `useCreateRoute`, `useUpdateRoute`, `useDeleteRoute`)
- [x] T043 Create `frontend/src/pages/routes/RouteListPage.tsx` with DataTable, search, create button
- [x] T044 Create `frontend/src/pages/routes/RouteFormPage.tsx` with create/edit form, validation, server error handling
- [x] T045 Register `/routes`, `/routes/new`, `/routes/:id/edit` in App.tsx with ProtectedRoute + RoleGuard

### Customers (US-011)

- [x] T046 Create `frontend/src/types/customer.ts` with `CustomerCreate`, `CustomerUpdate`, `CustomerResponse` interfaces
- [x] T047 Create `frontend/src/api/customers.ts` with CRUD API functions
- [x] T048 Create `frontend/src/hooks/useCustomers.ts` with TanStack Query hooks
- [x] T049 Create `frontend/src/pages/customers/CustomerListPage.tsx` with DataTable, route filter, search
- [x] T050 Create `frontend/src/pages/customers/CustomerFormPage.tsx` with route dropdown (from useRoutes), phone validation
- [x] T051 Create `frontend/src/pages/customers/CustomerDetailPage.tsx` with subscriptions, payments, consumption tabs
- [x] T052 Register `/customers`, `/customers/new`, `/customers/:id`, `/customers/:id/edit` in App.tsx

### Milk Types (US-012)

- [x] T053 Create `frontend/src/types/milk-type.ts` with `MilkTypeCreate`, `MilkTypeUpdate`, `MilkTypeResponse` interfaces
- [x] T054 Create `frontend/src/api/milk-types.ts` with CRUD API functions
- [x] T055 Create `frontend/src/hooks/useMilkTypes.ts` with TanStack Query hooks
- [x] T056 Create `frontend/src/pages/milk-types/MilkTypeListPage.tsx` with DataTable
- [x] T057 Create `frontend/src/pages/milk-types/MilkTypeFormPage.tsx` with volume_ml validation
- [x] T058 Register `/milk-types`, `/milk-types/new`, `/milk-types/:id/edit` in App.tsx

### Employees (US-013)

- [x] T059 Create `frontend/src/types/employee.ts` with `EmployeeCreate`, `EmployeeUpdate`, `EmployeeResponse`, `EmployeeCredentials` interfaces
- [x] T060 Create `frontend/src/api/employees.ts` with CRUD + credentials API functions
- [x] T061 Create `frontend/src/hooks/useEmployees.ts` with TanStack Query hooks
- [x] T062 Create `frontend/src/pages/employees/EmployeeListPage.tsx` with role filter
- [x] T063 Create `frontend/src/pages/employees/EmployeeFormPage.tsx` with role/route dropdowns, optional user creation fields
- [x] T064 Create `frontend/src/pages/employees/EmployeeCredentialsPage.tsx` to manage username/password
- [x] T065 Register `/employees`, `/employees/new`, `/employees/:id/edit`, `/employees/:id/credentials` in App.tsx

### Users (US-014)

- [x] T066 Create `frontend/src/api/users.ts` with list + create API functions
- [x] T067 Create `frontend/src/pages/users/UserListPage.tsx` with read-only table
- [x] T068 Create `frontend/src/pages/users/UserCreatePage.tsx` with username/role/password form
- [x] T069 Register `/users`, `/users/new` in App.tsx

**Checkpoint**: All master data CRUD works end-to-end. Routes, customers, milk types, employees, and users can be managed from the UI.

---

## Phase 3: Subscription & Exception Pages (US-020, US-021, US-022)

**Purpose**: Customer subscription management, delivery exceptions, read-only view for Checker.

### Subscriptions (US-020)

- [ ] T070 Create `frontend/src/types/subscription.ts` with `SubscriptionCreate`, `SubscriptionUpdate`, `SubscriptionResponse` interfaces
- [ ] T071 Create `frontend/src/api/subscriptions.ts` with CRUD + customer filter API functions
- [ ] T072 Create `frontend/src/hooks/useSubscriptions.ts` with TanStack Query hooks
- [ ] T073 Create `frontend/src/pages/subscriptions/SubscriptionListPage.tsx` with customer/route filter
- [ ] T074 Create `frontend/src/pages/subscriptions/SubscriptionFormPage.tsx` with customer dropdown, milk type dropdown, morning/evening fields
- [ ] T075 Register `/subscriptions`, `/subscriptions/new`, `/subscriptions/:id/edit` in App.tsx with OWNER/ADMIN guard

### Delivery Exceptions (US-021)

- [ ] T076 Create `frontend/src/types/delivery-exception.ts` with `DeliveryExceptionCreate`, `DeliveryExceptionUpdate`, `DeliveryExceptionResponse` interfaces
- [ ] T077 Create `frontend/src/api/delivery-exceptions.ts` with CRUD + subscription filter API functions
- [ ] T078 Create `frontend/src/hooks/useDeliveryExceptions.ts` with TanStack Query hooks
- [ ] T079 Create `frontend/src/pages/delivery-exceptions/ExceptionListPage.tsx` with subscription/customer filter
- [ ] T080 Create `frontend/src/pages/delivery-exceptions/ExceptionFormPage.tsx` with subscription selector, exception type dropdown, date range picker
- [ ] T081 Register `/delivery-exceptions`, `/delivery-exceptions/new` in App.tsx with OWNER/ADMIN guard

### Read-Only Checker View (US-022)

- [ ] T082 Add CHECKER role to route guards for subscription/exception list pages (read-only, no create/edit buttons)
- [ ] T083 Conditionally hide create/edit buttons and form access based on user role in subscription/exception list pages

**Checkpoint**: Subscriptions and exceptions fully manageable. Checker can view but not edit.

---

## Phase 4: Token Book Pages (US-030, US-031, US-032, US-033)

**Purpose**: Token identity, book issue, and payment management.

### Token Identities (US-030)

- [ ] T084 Create `frontend/src/types/token-identity.ts` with `TokenIdentityCreate`, `TokenIdentityUpdate`, `TokenIdentityResponse` interfaces
- [ ] T085 Create `frontend/src/api/token-books.ts` with identity CRUD API functions
- [ ] T086 Create `frontend/src/pages/token-books/TokenIdentityListPage.tsx` with customer/milk-type filter
- [ ] T087 Create `frontend/src/pages/token-books/TokenIdentityFormPage.tsx` with customer/milk-type dropdowns
- [ ] T088 Register `/token-identities`, `/token-identities/new` in App.tsx

### Token Book Issues (US-031)

- [ ] T089 Create `frontend/src/types/token-book.ts` with `TokenBookIssueCreate`, `TokenBookIssueResponse` interfaces
- [ ] T090 Add issue CRUD API functions to `frontend/src/api/token-books.ts`
- [ ] T091 Create `frontend/src/pages/token-books/TokenBookIssueListPage.tsx` with identity/customer filter
- [ ] T092 Create `frontend/src/pages/token-books/TokenBookIssueFormPage.tsx` with identity selector, sheet count, issue date
- [ ] T093 Register `/token-book-issues`, `/token-book-issues/new` in App.tsx

### Token Book Payments (US-032)

- [ ] T094 Add `TokenBookPaymentCreate`, `TokenBookPaymentResponse` types to `frontend/src/types/token-book.ts`
- [ ] T095 Add payment CRUD API functions to `frontend/src/api/token-books.ts`
- [ ] T096 Create `frontend/src/pages/token-books/TokenBookPaymentListPage.tsx` with issue filter
- [ ] T097 Create `frontend/src/pages/token-books/TokenBookPaymentFormPage.tsx` with book price, amount paid, payment mode dropdown
- [ ] T098 Register `/token-book-payments`, `/token-book-payments/new` in App.tsx

### Checker View (US-033)

- [ ] T099 Add CHECKER read-only access to token book list pages (view only, no create/edit)

**Checkpoint**: Token identities, issues, and payments fully manageable.

---

## Phase 5: Delivery Management Pages (US-040 through US-048)

**Purpose**: Delivery session lifecycle, registration, reconciliation, and close. All-in-one scrollable session detail page.

### Types and API Client

- [ ] T100 Create `frontend/src/types/delivery-session.ts` with `DeliverySessionCreate`, `DeliverySessionResponse`, `SessionListResponse` interfaces
- [ ] T101 Create `frontend/src/types/daily-delivery.ts` with `DailyDeliveryResponse`, `DeliveryChecklistResponse`, `TokenRegistrationRequest`, `UnplannedDeliveryRequest`, `TokenValidationRequest`, `TokenValidationResponse`, `DeliveryStatus` interfaces
- [ ] T102 Create `frontend/src/api/delivery-sessions.ts` with all session lifecycle API functions (create, start, dispatch, close, checklist, reconciliation, report)
- [ ] T103 Create `frontend/src/api/deliveries.ts` with delivery edit API functions (register token, validate token, unplanned, edit, reopen, warnings, edit-history, token-status)

### Hooks

- [ ] T104 Create `frontend/src/hooks/useDeliverySessions.ts` with TanStack Query hooks for session CRUD, dispatch, close, checklist, reconciliation
- [ ] T105 Create `frontend/src/hooks/useDeliveries.ts` with TanStack Query hooks for token registration, validation, unplanned, edit, reopen

### Session List & Create

- [ ] T106 Create `frontend/src/pages/delivery/SessionListPage.tsx` — filterable by date, route, status with DataTable
- [ ] T107 Create `frontend/src/pages/delivery/SessionCreatePage.tsx` — route dropdown, date picker, shift selector, delivery partner dropdown
- [ ] T108 Create `frontend/src/pages/delivery/SessionDetailPage.tsx` — all-in-one scrollable page with sections: Dispatch, Checklist/Register, Reconciliation, Close, Summary

### Dispatch Section

- [ ] T109 Create dispatch form within `SessionDetailPage.tsx` — input for total milk loaded, POST to dispatch endpoint, show only when status=PLANNED

### Checklist/Register Section

- [ ] T110 Create checklist table within `SessionDetailPage.tsx` — displays expected customers with planned quantities
- [ ] T111 Add delivery status dropdown per row (DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED)
- [ ] T112 Add token sheet input for DELIVERED status rows with client-side call to validate-token endpoint
- [ ] T113 Add token warning acknowledgment modal — shows warning message, requires acknowledgment to proceed
- [ ] T114 Add "Add Unplanned Delivery" button with inline form for ad-hoc deliveries

### Reconciliation Section

- [ ] T115 Create reconciliation summary display — loaded vs token vs cash vs returned with balance status
- [ ] T116 Add cash sales input — add/remove cash sale amounts
- [ ] T117 Add returned milk input
- [ ] T118 Add validate and submit reconciliation buttons
- [ ] T119 Add close session button (shown only when balanced)

### Summary Section

- [ ] T120 Create session summary display — read-only report after session is closed

### Edit & Reopen (US-048)

- [ ] T121 Create `frontend/src/pages/delivery/DeliveryEditPage.tsx` for Owner to edit previous deliveries, reopen closed sessions
- [ ] T122 Register all delivery routes (`/delivery/sessions`, `/delivery/sessions/new`, `/delivery/sessions/:id`, `/delivery/edit/:deliveryId`) in App.tsx with appropriate role guards

**Checkpoint**: Full delivery workflow works end-to-end — create → dispatch → register → reconcile → close. Owner can edit/reopen.

---

## Phase 6: Payment Pages (US-050, US-051, US-052, US-053)

**Purpose**: Customer payment recording, bill generation, outstanding balance tracking.

### Types

- [ ] T123 Create `frontend/src/types/payment.ts` with `CustomerPaymentCreate`, `CustomerPaymentResponse`, `BillGenerateRequest`, `BillResponse`, `BillItemResponse`, `OutstandingBalance` interfaces

### API & Hooks

- [ ] T124 Create `frontend/src/api/payments.ts` with payment CRUD, bill generate, bill list, outstanding API functions
- [ ] T125 Create `frontend/src/hooks/usePayments.ts` with TanStack Query hooks

### Payment Pages

- [ ] T126 Create `frontend/src/pages/payments/PaymentListPage.tsx` — filterable by customer, payment mode, date range
- [ ] T127 Create `frontend/src/pages/payments/PaymentFormPage.tsx` — customer dropdown, amount, payment mode dropdown (CASH/UPI/CARD/CHEQUE/BANK_TRANSFER), date, remarks
- [ ] T128 Create `frontend/src/pages/payments/BillListPage.tsx` — list of generated bills with customer filter
- [ ] T129 Create `frontend/src/pages/payments/BillGeneratePage.tsx` — multi-select customers, date range, generate button, display generated bills
- [ ] T130 Create `frontend/src/pages/payments/OutstandingPage.tsx` — table of customers with outstanding balances
- [ ] T131 Register `/payments`, `/payments/new`, `/payments/bills`, `/payments/bills/generate`, `/payments/outstanding` in App.tsx with OWNER/ADMIN guard

**Checkpoint**: Payments recordable, bills generatable, outstanding balances viewable.

---

## Phase 7: Report Pages (US-060 through US-065)

**Purpose**: Operational dashboard, route delivery report, revenue report, consumption report, token utilization, collection efficiency.

### Types

- [ ] T132 Create `frontend/src/types/reports.ts` with `OperationalDashboard`, `RouteDeliveryReport`, `RevenueReport`, `CustomerConsumptionReport`, `TokenUtilizationReport`, `CollectionEfficiencyReport` interfaces

### API & Hooks

- [ ] T133 Create `frontend/src/api/reports.ts` with all 6 report API functions (with preset/date-range params, CSV format support)
- [ ] T134 Create `frontend/src/hooks/useReports.ts` with TanStack Query hooks for each report type

### Dashboard (US-060)

- [ ] T135 Create `frontend/src/pages/reports/DashboardPage.tsx` — KPI cards grid: sessions count, milk loaded/delivered, deliveries by status, pending tokens, unclosed sessions
- [ ] T136 Register `/reports/dashboard` in App.tsx as the root `/` redirect target

### Route Delivery Report (US-061)

- [ ] T137 Create `frontend/src/pages/reports/RouteDeliveryReportPage.tsx` — date range + route selector + DataTable with performance metrics
- [ ] T138 Register `/reports/route-delivery` in App.tsx

### Revenue Report (US-062)

- [ ] T139 Create `frontend/src/pages/reports/RevenueReportPage.tsx` — date range picker, optional route/milk-type filters, revenue breakdown table
- [ ] T140 Register `/reports/revenue` in App.tsx with OWNER-only RoleGuard

### Customer Consumption (US-063)

- [ ] T141 Create `frontend/src/pages/reports/ConsumptionReportPage.tsx` — customer selector, date range, consumption trend display with trend badge
- [ ] T142 Register `/reports/consumption/:customerId` in App.tsx

### Token Utilization (US-064)

- [ ] T143 Create `frontend/src/pages/reports/TokenUtilizationPage.tsx` — table with utilization percentage bars, low threshold filter
- [ ] T144 Register `/reports/token-utilization` in App.tsx

### Collection Efficiency (US-065)

- [ ] T145 Create `frontend/src/pages/reports/CollectionEfficiencyPage.tsx` — aging analysis table with color-coded buckets
- [ ] T146 Register `/reports/collection-efficiency` in App.tsx

**Checkpoint**: All 6 report pages render with data from backend. Dashboard shows today's KPIs.

---

## Phase 8: Polish & Cross-Cutting Concerns (US-071, US-072, US-073)

**Purpose**: Loading states, form validation, confirm dialogs, error boundary, responsive layout, 404 page.

- [ ] T147 Add global `ErrorBoundary` component in `frontend/src/components/ErrorBoundary.tsx` wrapping the app, reporting to Sentry
- [ ] T148 Add loading skeleton components for DataTable rows, card placeholders on dashboard
- [ ] T149 Add React.memo on DataTable rows for performance
- [ ] T150 Lazy-load page components with `React.lazy()` + `Suspense` in App.tsx
- [ ] T151 Add form validation: required fields, phone (10 digits), min/max lengths, email format where applicable
- [ ] T152 Add confirm dialogs on all delete/close/reopen/cancel actions
- [ ] T153 Add responsive sidebar — collapsible on < 768px with hamburger icon
- [ ] T154 Add responsive tables — horizontal scroll on mobile
- [ ] T155 Add `react-hot-toast` error/success/info toast providers in App.tsx
- [ ] T156 Add client-side route transitions with loading indicators
- [ ] T157 Run `quickstart.md` validation scenarios V1 through V10 end-to-end
- [ ] T158 Update `.gitignore` in frontend/ to exclude node_modules, dist, .env

**Checkpoint**: Production-ready polish — loading states, validation, confirmations, responsive design, error tracking.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies — can start immediately
- **Phase 2**: Depends on Phase 1 completion (auth + layout + UI components)
- **Phase 3**: Depends on Phase 1 + Phase 2 (needs customer data from Phase 2)
- **Phase 4**: Depends on Phase 1 + Phase 2 (needs customer + milk type data)
- **Phase 5**: Depends on Phase 1 + Phase 2 + Phase 3 (needs routes, customers, subscriptions)
- **Phase 6**: Depends on Phase 1 + Phase 2 (needs customers)
- **Phase 7**: Depends on Phase 1 (needs auth + layout)
- **Phase 8**: Depends on Phase 1 through Phase 7 (polish applies to all pages)

### User Story Dependency Graph

```
Phase 1 (Setup + Auth + Layout)
  ├──→ Phase 2 (Master Data: Routes, Customers, Milk Types, Employees, Users)
  │     ├──→ Phase 3 (Subscriptions & Exceptions → needs Customer)
  │     ├──→ Phase 4 (Token Books → needs Customer + Milk Type)
  │     ├──→ Phase 5 (Delivery → needs Route + Customer + Subscription)
  │     └──→ Phase 6 (Payments → needs Customer)
  ├──→ Phase 7 (Reports → needs auth only, no master data dependency)
  └──→ Phase 8 (Polish → depends on all phases for full coverage)
```

### Parallel Opportunities

- All tasks marked [P] within a phase can run in parallel
- Within Phase 2, each entity (routes, customers, milk types, employees, users) can be built in parallel
- Within Phase 4, token identity, issue, and payment pages can be built in parallel
- Phase 6 and Phase 7 can proceed simultaneously once Phase 2 is done
- Different form pages within the same phase can be developed in parallel

---

## Parallel Example: Phase 2 Master Data

```bash
# All routes tasks in parallel:
Task: T040 Create types/route.ts
Task: T041 Create api/routes.ts
Task: T042 Create hooks/useRoutes.ts
Task: T043 Create RouteListPage.tsx
Task: T044 Create RouteFormPage.tsx

# All customers tasks in parallel:
Task: T046 Create types/customer.ts
Task: T047 Create api/customers.ts
Task: T048 Create hooks/useCustomers.ts
Task: T049 Create CustomerListPage.tsx
Task: T050 Create CustomerFormPage.tsx

# All milk types tasks in parallel:
Task: T053 Create types/milk-type.ts
Task: T054 Create api/milk-types.ts
Task: T055 Create hooks/useMilkTypes.ts
Task: T056 Create MilkTypeListPage.tsx
Task: T057 Create MilkTypeFormPage.tsx
```

---

## Implementation Strategy

### MVP First (Phase 1 Only)

1. Complete Phase 1: Backend prep + frontend scaffold + auth flow + layout
2. **STOP and VALIDATE**: Login/logout works, sidebar renders, dashboard loads
3. Deploy/demo — basic authentication-ready shell

### Incremental Delivery

1. Complete Phase 1 → Auth & layout ready
2. Add Phase 2 → Master data management ready (MVP+)
3. Add Phase 3 → Subscription management ready
4. Add Phase 4 → Token book management ready
5. Add Phase 5 → Delivery workflow ready (core operational value)
6. Add Phase 6 → Payment management ready
7. Add Phase 7 → Reporting ready
8. Add Phase 8 → Production polish

### Why This Order

Master data (Phase 2) is the foundation for almost everything else. Delivery management (Phase 5) is the highest operational value but depends on routes, customers, and subscriptions. Reports (Phase 7) provides the most visible business value but is independent of most data — can be delivered early alongside Phase 2 if desired.

---

## Summary

| Phase | User Stories | Tasks | Independent Test |
|-------|-------------|-------|------------------|
| 1 — Setup + Auth + Layout | US-001, US-002, US-003, US-004, US-070 | T001-T039 | Login at :5173, sidebar navigation for each role |
| 2 — Master Data | US-010, US-011, US-012, US-013, US-014 | T040-T069 | CRUD routes, customers, milk types, employees |
| 3 — Subscriptions & Exceptions | US-020, US-021, US-022 | T070-T083 | Create subscription linked to customer, add exception |
| 4 — Token Books | US-030, US-031, US-032, US-033 | T084-T099 | Create identity, issue book, record payment |
| 5 — Delivery Management | US-040 through US-048 | T100-T122 | Full session lifecycle create→dispatch→register→reconcile→close |
| 6 — Payments | US-050, US-051, US-052, US-053 | T123-T131 | Record payment, generate bill, view outstanding |
| 7 — Reports | US-060 through US-065 | T132-T146 | Dashboard loads, report tables render |
| 8 — Polish | US-071, US-072, US-073 | T147-T158 | Loading states, validation, confirmations, responsive |
| **Total** | **23 user stories** | **158 tasks** | |
