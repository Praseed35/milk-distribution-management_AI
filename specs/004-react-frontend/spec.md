# Feature Specification: React Frontend for Milk Distribution ERP

---

## Clarifications

### Session 2026-07-31

- Q: Backend response format inconsistency — how should the frontend normalize them? → A: Per-endpoint normalization in each API module file.
- Q: Frontend error monitoring — Sentry or console only? → A: Sentry integration for unhandled errors and API failures.
- Q: Component library — shadcn/ui, pure Tailwind, or Headless UI? → A: Pure Tailwind CSS, all UI primitives built from scratch.
- Q: Delivery registration UX — wizard, tabbed, or all-in-one? → A: All-in-one scrollable page with sections for dispatch, register, reconciliation, close.
- Q: Expected data volume — small, medium, or large? → A: Medium (< 2,000 customers, < 50 routes, < 200 sessions/day). Standard pagination (page_size=50) sufficient; no virtual scrolling needed.

---

## Feature Overview

Add a modern React-based Single Page Application (SPA) frontend to the existing FastAPI backend, providing a complete graphical user interface for all business modules of the Milk Distribution ERP. The frontend will serve administrative users (Owner, Admin, Checker, Delivery Partner) with role-based access, JWT authentication, and a responsive dashboard-driven layout.

---

## Business Problem

The Milk Distribution ERP currently has **no user interface** other than the raw REST API and the auto-generated Swagger docs at `/docs`. Business users cannot interact with the system without writing HTTP requests. This makes the system unusable for daily operations — customer registration, subscription management, delivery reconciliation, token book payments, and reporting cannot be performed by non-technical staff.

---

## Objectives

1. Provide a complete web-based UI covering all 14 backend router modules.
2. Implement JWT-based login with automatic token handling and 401 redirect.
3. Enforce role-based access control at the route and UI component level.
4. Deliver a responsive, mobile-friendly layout suitable for office desktops and tablets.
5. Keep the frontend codebase clean, typed, and maintainable using TypeScript.
6. Use industry-standard libraries (React Router v6, TanStack Query, Axios) for predictable patterns.
7. Phase the implementation so each deployable increment adds business value.

---

## Scope

| In Scope | Out of Scope |
|---|---|
| Backend CORS configuration for dev server | Mobile native apps (Flutter) |
| API prefix migration to `/api/v1` | Customer-facing portal (V2) |
| Root health endpoint | AI/Business Intelligence UI (V2) |
| Complete React + Vite + TypeScript SPA | GPS / map-based route tracking (V2) |
| JWT login, auto-refresh, 401 redirect | QR code / barcode scanning (V2) |
| Role-based routing and component guards | Offline/PWA support |
| 14 module CRUD + workflow pages | Real-time notifications |
| Dashboard with operational KPIs | Dark mode theming |
| TanStack Query data fetching | CSV/PDF export from frontend (backend handles CSV) |
| Vite proxy configuration | |

---

## Stakeholders

| Stakeholder | Interest |
|---|---|
| **Business Owner** | Full access to all modules, reports, and configuration |
| **Admin** | Customer, route, subscription, and employee management |
| **Checker** | Daily delivery registration, token registration, reconciliation, route closing |
| **Delivery Partner** | View assigned route and delivery checklist (read-only) |
| **Developer** | Clean, typed codebase with standard patterns |
| **Future Maintainer** | Predictable project structure, documented API client layer |

---

## User Stories

### Epic: Authentication

| ID | Priority | User Story |
|---|---|---|
| US-001 | P0 | As a user, I want to log in with my username and password, so that I can access the ERP according to my role. |
| US-002 | P0 | As a user, I want my JWT token to be automatically attached to every API request, so that I don't have to manually provide credentials. |
| US-003 | P0 | As a user, I want to be redirected to the login page when my token expires or is invalid, so that I can re-authenticate securely. |
| US-004 | P1 | As a user, I want to change my password after logging in, so that I can maintain account security. |

### Epic: Master Data Management

| ID | Priority | User Story |
|---|---|---|
| US-010 | P0 | As an Owner, I want to list, create, update, and soft-delete routes, so that I can manage delivery areas. |
| US-011 | P0 | As an Owner, I want to list, create, update, and soft-delete customers with route assignment, so that customer records are maintained digitally. |
| US-012 | P0 | As an Owner, I want to list, create, update, and soft-delete milk types, so that the product catalog is maintained. |
| US-013 | P0 | As an Owner, I want to list, create, and update employees with optional user account linking, so that staff records are digitized. |
| US-014 | P1 | As an Owner, I want to list and create system users, so that authentication accounts can be managed. |

### Epic: Subscription & Exceptions

| ID | Priority | User Story |
|---|---|---|
| US-020 | P0 | As an Owner, I want to create and manage customer subscriptions (milk type, morning/evening quantities), so that daily delivery is planned correctly. |
| US-021 | P0 | As an Owner, I want to create delivery exceptions (vacation, no milk, holiday) for subscriptions, so that temporary changes are reflected in deliveries. |
| US-022 | P1 | As a Checker, I want to view subscriptions and exceptions in read-only mode, so that I can reference them during daily operations. |

### Epic: Token Books

| ID | Priority | User Story |
|---|---|---|
| US-030 | P0 | As an Owner, I want to create token identities (assign token numbers to customer+milk-type), so that token books can be issued. |
| US-031 | P0 | As an Owner, I want to issue token books with issue numbers, so that physical books are tracked. |
| US-032 | P1 | As an Owner, I want to record token book payments (prepaid/postpaid), so that book finances are tracked. |
| US-033 | P2 | As a Checker, I want to view token book details, so that I can verify token sheets during registration. |

### Epic: Daily Delivery & Reconciliation

| ID | Priority | User Story |
|---|---|---|
| US-040 | P0 | As a Checker, I want to create a delivery session (route + date + shift + partner), so that daily operations begin. |
| US-041 | P0 | As a Checker, I want to record dispatch (total milk loaded), so that the route starts with known inventory. |
| US-042 | P0 | As a Checker, I want to view the session checklist, so that I know which customers are expected. |
| US-043 | P0 | As a Checker, I want to register delivery status for each customer (delivered/pending/cash/not-delivered), so that the daily record is accurate. |
| US-044 | P0 | As a Checker, I want to register token sheets for delivered items, with warning acknowledgment, so that token accounting is complete. |
| US-045 | P0 | As a Checker, I want to add cash sales and returned milk during reconciliation, so that the route can be balanced. |
| US-046 | P0 | As a Checker, I want to view reconciliation status and close a balanced route, so that the day's work is finalized. |
| US-047 | P1 | As a Checker, I want to add unplanned deliveries, so that ad-hoc requests are captured. |
| US-048 | P1 | As an Owner, I want to reopen closed sessions and edit previous deliveries, so that errors can be corrected. |

### Epic: Payments

| ID | Priority | User Story |
|---|---|---|
| US-050 | P0 | As an Owner, I want to record customer payments (cash/UPI/card/cheque/bank transfer), so that accounts receivable is updated. |
| US-051 | P0 | As an Owner, I want to generate customer bills for a date range, so that periodic billing is automated. |
| US-052 | P1 | As an Owner, I want to view outstanding balances per customer, so that I can follow up on collections. |
| US-053 | P1 | As an Owner, I want to view payment history filtered by date, customer, and mode, so that financial tracking is easy. |

### Epic: Reports

| ID | Priority | User Story |
|---|---|---|
| US-060 | P0 | As an Owner, I want to see an operational dashboard with key KPIs, so that I get a quick daily overview. |
| US-061 | P1 | As an Owner, I want to view route delivery performance reports, so that I can analyze operational efficiency. |
| US-062 | P1 | As an Owner, I want to view revenue reports filtered by date and route, so that financial performance is tracked. |
| US-063 | P1 | As an Owner, I want to view customer consumption trends, so that I can understand buying patterns. |
| US-064 | P1 | As an Owner, I want to view token utilization reports, so that I can manage token book inventory. |
| US-065 | P2 | As an Owner, I want to view collection efficiency with aging analysis, so that I can manage receivables. |

### Epic: UX Foundations

| ID | Priority | User Story |
|---|---|---|
| US-070 | P0 | As a user, I want a sidebar navigation that reflects my role permissions, so that I can access only what I'm allowed to see. |
| US-071 | P0 | As a user, I want loading spinners and error toasts on every async operation, so that I know the system state. |
| US-072 | P1 | As a user, I want consistent form validation with clear error messages, so that I can correct input mistakes. |
| US-073 | P1 | As a user, I want confirm dialogs before destructive actions (delete, close route, cancel), so that I don't accidentally lose data. |

---

## Functional Requirements

### FR-1: Backend Preparation

| ID | Requirement | Details |
|---|---|---|
| FR-1.1 | CORS Middleware | Add `CORSMiddleware` to `app/main.py` allowing origin `http://localhost:5173` (Vite default). Include credentials, all methods, all headers. |
| FR-1.2 | API Prefix Migration | Wrap all routers under an `APIRouter` with prefix `/api/v1` and include that router instead of individual routers. OR add a middleware that strips/mounts prefix. **Recommendation**: use `APIRouter(prefix="/api/v1")` as an umbrella and include sub-routers under it. |
| FR-1.3 | Root Health Endpoint | Add `GET /api/v1/health` returning `{"status": "ok", "version": "1.0.0", "timestamp": "..."}`. No auth required. |
| FR-1.4 | Backward Compatibility | **Assumption**: No backward compatibility maintained. All frontend requests go to `/api/v1/...`. The old root-level routes remain for existing scripts but are deprecated. Mark them with a warning log. |
| FR-1.5 | OpenAPI Prefix | Ensure `/docs` and `/openapi.json` reflect the new `/api/v1` prefix. |

### FR-2: Frontend Scaffolding

| ID | Requirement | Details |
|---|---|---|
| FR-2.1 | Project Init | Create `frontend/` at project root. Use `npm create vite@latest frontend -- --template react-ts`. |
| FR-2.2 | Dependencies | Install: `react-router-dom`, `axios`, `@tanstack/react-query`, `@tanstack/react-query-devtools`, `react-hot-toast`, `@sentry/react`. Dev: `tailwindcss`, `postcss`, `autoprefixer`, `@types/react-router-dom`. |
| FR-2.3 | Vite Proxy | Configure in `vite.config.ts`: proxy `/api` to `http://localhost:8000`. This avoids CORS during development and matches the production setup where a reverse proxy (nginx) will serve both. |

### FR-3: Authentication

| ID | Requirement | Details |
|---|---|---|
| FR-3.1 | Login Page | Route `/login`. Form with username + password fields. POST to `/api/v1/auth/login`. On success, store the JWT access token in `localStorage` under key `auth_token`. |
| FR-3.2 | Auth Context | Create `AuthContext` with: `user` (id, username, role), `token`, `login()`, `logout()`, `isAuthenticated`. On app mount, check localStorage for existing token and validate by calling `GET /api/v1/auth/me`. If invalid/expired, clear token and redirect to `/login`. |
| FR-3.3 | Axios Interceptor | Request interceptor: attach `Authorization: Bearer <token>` header. Response interceptor: on 401, clear token, redirect to `/login`. |
| FR-3.4 | Change Password | Form on profile page. PUT to `/api/v1/auth/change-password`. Validate client-side (new password match, min length). |
| FR-3.5 | Logout | Clear token from localStorage, reset auth context, navigate to `/login`. |

### FR-4: Protected Routing

| ID | Requirement | Details |
|---|---|---|
| FR-4.1 | Auth Guard | `ProtectedRoute` component checks `isAuthenticated`. If not authenticated, redirect to `/login`. |
| FR-4.2 | Role Guard | `RoleGuard({ roles: ["OWNER"] })` component checks user role. If not authorized, show 403 page or redirect to dashboard. |
| FR-4.3 | Sidebar | Dynamic navigation links based on user role. Owner sees all links. Checker sees delivery, token, subscription (read) links. Delivery Partner sees only dashboard and checklist. |

### FR-5: Page Hierarchy & Routing

| Path | Page | Roles | Module |
|---|---|---|---|
| `/login` | LoginPage | Public | Auth |
| `/` | DashboardPage | All | Dashboard |
| `/change-password` | ChangePasswordPage | All | Auth |
| `/users` | UserListPage | OWNER, ADMIN | Users |
| `/users/new` | UserCreatePage | OWNER, ADMIN | Users |
| `/routes` | RouteListPage | OWNER, ADMIN | Routes |
| `/routes/new` | RouteFormPage | OWNER, ADMIN | Routes |
| `/routes/:id/edit` | RouteFormPage | OWNER, ADMIN | Routes |
| `/customers` | CustomerListPage | OWNER, ADMIN, CHECKER | Customers |
| `/customers/new` | CustomerFormPage | OWNER, ADMIN | Customers |
| `/customers/:id/edit` | CustomerFormPage | OWNER, ADMIN | Customers |
| `/customers/:id` | CustomerDetailPage | OWNER, ADMIN, CHECKER | Customers |
| `/milk-types` | MilkTypeListPage | OWNER, ADMIN, CHECKER | Milk Types |
| `/milk-types/new` | MilkTypeFormPage | OWNER, ADMIN | Milk Types |
| `/milk-types/:id/edit` | MilkTypeFormPage | OWNER, ADMIN | Milk Types |
| `/employees` | EmployeeListPage | OWNER, ADMIN | Employees |
| `/employees/new` | EmployeeFormPage | OWNER | Employees |
| `/employees/:id/edit` | EmployeeFormPage | OWNER | Employees |
| `/employees/:id/credentials` | EmployeeCredentialsPage | OWNER | Employees |
| `/subscriptions` | SubscriptionListPage | OWNER, ADMIN, CHECKER | Subscriptions |
| `/subscriptions/new` | SubscriptionFormPage | OWNER, ADMIN | Subscriptions |
| `/subscriptions/:id/edit` | SubscriptionFormPage | OWNER, ADMIN | Subscriptions |
| `/delivery-exceptions` | ExceptionListPage | OWNER, ADMIN, CHECKER | Exceptions |
| `/delivery-exceptions/new` | ExceptionFormPage | OWNER, ADMIN | Exceptions |
| `/token-identities` | TokenIdentityListPage | OWNER, ADMIN | Token Books |
| `/token-identities/new` | TokenIdentityFormPage | OWNER | Token Books |
| `/token-book-issues` | TokenBookIssueListPage | OWNER, ADMIN | Token Books |
| `/token-book-issues/new` | TokenBookIssueFormPage | OWNER | Token Books |
| `/token-book-payments` | TokenBookPaymentListPage | OWNER, ADMIN, CHECKER | Token Books |
| `/token-book-payments/new` | TokenBookPaymentFormPage | OWNER, ADMIN | Token Books |
| `/delivery/sessions` | SessionListPage | OWNER, ADMIN, CHECKER | Deliveries |
| `/delivery/sessions/new` | SessionCreatePage | OWNER, ADMIN, CHECKER | Deliveries |
| `/delivery/sessions/:id` | SessionDetailPage | OWNER, ADMIN, CHECKER | Deliveries |
| `/delivery/sessions/:id/dispatch` | SessionDispatchPage | OWNER, ADMIN, CHECKER | Deliveries |
| `/delivery/sessions/:id/checklist` | SessionChecklistPage | DELIVERY_PARTNER, CHECKER | Deliveries |
| `/delivery/sessions/:id/register` | DeliveryRegistrationPage | CHECKER | Deliveries |
| `/delivery/sessions/:id/reconciliation` | ReconciliationPage | CHECKER | Deliveries |
| `/delivery/edit/:deliveryId` | DeliveryEditPage | OWNER | Deliveries |
| `/payments` | PaymentListPage | OWNER, ADMIN | Payments |
| `/payments/new` | PaymentFormPage | OWNER, ADMIN | Payments |
| `/payments/bills/generate` | BillGeneratePage | OWNER, ADMIN | Payments |
| `/payments/bills` | BillListPage | OWNER, ADMIN | Payments |
| `/payments/outstanding` | OutstandingPage | OWNER, ADMIN | Payments |
| `/reports/dashboard` | DashboardPage | All | Reports |
| `/reports/route-delivery` | RouteDeliveryReportPage | OWNER, ADMIN | Reports |
| `/reports/revenue` | RevenueReportPage | OWNER | Reports |
| `/reports/consumption/:customerId` | ConsumptionReportPage | OWNER, ADMIN, CHECKER | Reports |
| `/reports/token-utilization` | TokenUtilizationPage | OWNER, ADMIN | Reports |
| `/reports/collection-efficiency` | CollectionEfficiencyPage | OWNER, ADMIN | Reports |

### FR-6: API Client Architecture

| ID | Requirement | Details |
|---|---|---|
| FR-6.1 | Axios Instance | Create `src/api/client.ts` with baseURL `/api/v1`, timeout 30s, and the auth interceptor. |
| FR-6.2 | Module Clients | One file per router module: `api/auth.ts`, `api/customers.ts`, `api/routes.ts`, etc. Each exports typed functions. Each module client normalizes its own responses to handle backend's inconsistent response formats (envelope vs direct vs paginated). |
| FR-6.3 | TanStack Query Hooks | One file per module: `hooks/useCustomers.ts`, `hooks/useRoutes.ts`, etc. Each exports `useQuery`/`useMutation` hooks wrapping the API functions. |
| FR-6.4 | TypeScript Types | Create `src/types/` mirroring backend Pydantic schemas. One file per module: `types/auth.ts`, `types/customer.ts`, etc. |

### FR-7: UI Component Patterns

| ID | Requirement | Details |
|---|---|---|
| FR-7.1 | Layout | `AppLayout` with sidebar (collapsible), top header bar (user info, logout), and main content area. |
| FR-7.2 | Data Tables | Reusable `DataTable` component with sorting, pagination, loading skeleton, empty state, and error state. |
| FR-7.3 | Forms | Consistent form patterns with field validation, submit button with loading state, and server error display. |
| FR-7.4 | Modals | `ConfirmDialog` for destructive actions. `SlideOver` or `Drawer` for detail views (optional). |
| FR-7.5 | Status Badges | Reusable badge components for delivery status, session status, payment status, subscription status. |
| FR-7.6 | Page Header | Each page has a title, description, and action buttons (Create, Refresh, etc.) consistent layout. |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Page Load | Initial bundle < 300KB (gzipped). Page transition < 1s. |
| NFR-2 | API Responsiveness | TanStack Query staleTime 30s for master data, 5s for operational data. |
| NFR-3 | Error Handling | All API errors caught and displayed as toast notifications. 5xx errors show "Server error. Please try again." |
| NFR-4 | Browser Support | Modern browsers: Chrome, Firefox, Edge, Safari (last 2 versions). |
| NFR-5 | Responsiveness | Sidebar collapses on < 768px. Tables horizontally scrollable on mobile. |
| NFR-6 | Security | No tokens in URL. No sensitive data in localStorage beyond the JWT. All API calls go through the proxied `/api` path. |
| NFR-7 | Accessibility | Forms use proper labels. Tables use proper semantic markup. Color is not the only indicator (status text + badge). |

---

## Business Rules

| ID | Rule |
|---|---|
| BR-1 | Only OWNER and ADMIN can create/update/delete master data (customers, routes, milk types, employees, users). |
| BR-2 | CHECKER can view master data but cannot create/update/delete. |
| BR-3 | DELIVERY_PARTNER can only view their assigned route checklist. |
| BR-4 | Only OWNER can reopen closed sessions and edit previous deliveries. |
| BR-5 | A session cannot be closed until reconciliation is balanced. |
| BR-6 | Token registration during delivery requires sheet validation (sequence check, duplicate check); warnings require checker acknowledgment. |
| BR-7 | Customer primary phone must be unique across active customers. |
| BR-8 | Soft delete is used for all master records (set `is_active = false`). |
| BR-9 | Token book payment is independent of delivery — payment and delivery are separate workflows. |
| BR-10 | Reports are generated from finalized (closed) data only. |

---

## Validation Rules

| Field | Rule | Client | Server |
|---|---|---|---|
| username | Required, 3-100 chars | ✓ | ✓ |
| password | Required, min 6 chars | ✓ | ✓ |
| customer_name | Required, 2-100 chars | ✓ | ✓ |
| primary_phone | Required, exactly 10 digits | ✓ | ✓ |
| alternate_phone | Optional, exactly 10 digits | ✓ | ✓ |
| route_id | Required, must reference active route | ✗ (send ID) | ✓ |
| milk_type name | Required, unique | ✓ | ✓ |
| subscription quantity | Must be >= 0 | ✓ | ✓ |
| token_sheet_number | Required for token registration, must be > 0 | ✓ | ✓ |
| delivery_status | Must be one of: DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, CANCELLED | ✓ | ✓ |
| payment amount | Required, > 0 | ✓ | ✓ |
| shift | Must be MORNING or EVENING | ✓ | ✓ |
| session close | Must be balanced | ✗ | ✓ |

---

## Edge Cases

| ID | Edge Case | Handling |
|---|---|---|
| EC-1 | Token expired mid-session | Axios 401 interceptor catches it. Show toast "Session expired", redirect to login, preserve attempted URL in `sessionStorage` for redirect after login. |
| EC-2 | Network offline | TanStack Query retries (default 3). After retries exhausted, show error toast. No offline mode. |
| EC-3 | Concurrent edit on delivery | Backend returns 409 with `ConcurrentEditError`. Toast "This delivery was modified by another user. Please refresh." |
| EC-4 | Duplicate phone on customer create | Backend returns 400. Show inline error on the phone field. |
| EC-5 | Session already exists for route+date+shift | Backend returns 400. Toast and prevent creation. |
| EC-6 | Token sheet already used | Backend returns 400. Show warning toast and block submission. |
| EC-7 | Empty list states | DataTable shows "No records found" illustration with a Create button if the user has permission. |
| EC-8 | Delete confirmation | All soft-delete actions (customer, route, etc.) trigger a confirm dialog with the name of the entity being deleted. |
| EC-9 | Session cannot be closed when unbalanced | Show detailed reconciliation summary with the difference highlighted in red. Explain which side is off. |
| EC-10 | Large datasets | Pagination on all list endpoints. Default page size 50. Expected volume: < 2,000 customers, < 50 routes, < 200 sessions/day. Standard pagination sufficient; no virtual scrolling needed. Search/filter support where backend provides. |

---

## Data Requirements

All data types on the frontend should mirror the backend Pydantic response schemas. Below are the key TypeScript interfaces to define.

### Type Layout (per module)

```
src/types/
  auth.ts        — LoginRequest, LoginResponse, User, ChangePasswordRequest
  route.ts       — RouteCreate, RouteUpdate, RouteResponse
  customer.ts    — CustomerCreate, CustomerUpdate, CustomerResponse, CustomerSummary
  milk-type.ts   — MilkTypeCreate, MilkTypeUpdate, MilkTypeResponse, MilkTypeSummary
  employee.ts    — EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeCredentials
  subscription.ts — SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionList, SubscriptionDetail
  delivery-exception.ts — DeliveryExceptionCreate, DeliveryExceptionUpdate, DeliveryExceptionResponse
  token-identity.ts — TokenIdentityCreate, TokenIdentityUpdate, TokenIdentityResponse, TokenIdentityList
  token-book.ts  — TokenBookIssueCreate, TokenBookIssueResponse, TokenBookPaymentCreate, etc.
  delivery-session.ts — DeliverySessionCreate, DeliverySessionResponse, DeliverySessionDetail, etc.
  daily-delivery.ts — DailyDeliveryUpdate, DailyDeliveryResponse, TokenRegistrationRequest, etc.
  payment.ts     — CustomerPaymentCreate, CustomerPaymentResponse, BillGenerateRequest, BillResponse, OutstandingBalance
  reports.ts     — RouteDeliveryReport, RevenueReport, CustomerConsumptionReport, TokenUtilizationReport, OperationalDashboard
  common.ts      — PaginatedResponse, ApiError, ApiResponse<T>
```

### Key Type Patterns

```typescript
// Standard API response envelope (as used by backend)
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

// Some endpoints return data directly (list endpoints return arrays)
// Auth endpoints return token objects
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  role: "OWNER" | "ADMIN" | "CHECKER" | "DELIVERY_PARTNER" | "EMPLOYEE";
}

// Paginated list response (delivery sessions use this pattern)
export interface PaginatedResponse<T> {
  sessions?: T[];        // sessions list endpoint
  deliveries?: T[];      // deliveries list endpoint  
  data?: T[];            // reports use this
  total: number;
  page?: number;
  page_size?: number;
}
```

---

## API Considerations

### Current API Endpoint Map (All at root, to be migrated to `/api/v1`)

| Module | Method | Current Path | New Path |
|---|---|---|---|
| Auth | POST | /auth/login | /api/v1/auth/login |
| Auth | GET | /auth/me | /api/v1/auth/me |
| Auth | PUT | /auth/change-password | /api/v1/auth/change-password |
| Auth | GET | /auth/owner-dashboard | /api/v1/auth/owner-dashboard |
| Users | GET | /users/ | /api/v1/users/ |
| Users | POST | /users/ | /api/v1/users/ |
| Routes | GET | /routes/ | /api/v1/routes/ |
| Routes | POST | /routes/ | /api/v1/routes/ |
| Routes | GET | /routes/{id} | /api/v1/routes/{id} |
| Routes | PUT | /routes/{id} | /api/v1/routes/{id} |
| Routes | DELETE | /routes/{id} | /api/v1/routes/{id} |
| Customers | GET | /customers/ | /api/v1/customers/ |
| Customers | POST | /customers/ | /api/v1/customers/ |
| Customers | GET | /customers/{id} | /api/v1/customers/{id} |
| Customers | PUT | /customers/{id} | /api/v1/customers/{id} |
| Customers | DELETE | /customers/{id} | /api/v1/customers/{id} |
| Milk Types | GET | /milk-types/ | /api/v1/milk-types/ |
| Milk Types | POST | /milk-types/ | /api/v1/milk-types/ |
| Milk Types | GET | /milk-types/{id} | /api/v1/milk-types/{id} |
| Milk Types | PUT | /milk-types/{id} | /api/v1/milk-types/{id} |
| Milk Types | DELETE | /milk-types/{id} | /api/v1/milk-types/{id} |
| Employees | GET | /employees/ | /api/v1/employees/ |
| Employees | POST | /employees/ | /api/v1/employees/ |
| Employees | GET | /employees/{id} | /api/v1/employees/{id} |
| Employees | PUT | /employees/{id} | /api/v1/employees/{id} |
| Employees | PUT | /employees/{id}/credentials | /api/v1/employees/{id}/credentials |
| Employees | DELETE | /employees/{id} | /api/v1/employees/{id} |
| Subscriptions | GET | /subscriptions/ | /api/v1/subscriptions/ |
| Subscriptions | POST | /subscriptions/ | /api/v1/subscriptions/ |
| Subscriptions | GET | /subscriptions/{id} | /api/v1/subscriptions/{id} |
| Subscriptions | GET | /subscriptions/customer/{id} | /api/v1/subscriptions/customer/{id} |
| Subscriptions | PUT | /subscriptions/{id} | /api/v1/subscriptions/{id} |
| Subscriptions | DELETE | /subscriptions/{id} | /api/v1/subscriptions/{id} |
| Delivery Exceptions | GET | /delivery-exceptions/ | /api/v1/delivery-exceptions/ |
| Delivery Exceptions | POST | /delivery-exceptions/ | /api/v1/delivery-exceptions/ |
| Delivery Exceptions | GET | /delivery-exceptions/{id} | /api/v1/delivery-exceptions/{id} |
| Delivery Exceptions | GET | /delivery-exceptions/subscription/{id} | /api/v1/delivery-exceptions/subscription/{id} |
| Delivery Exceptions | PUT | /delivery-exceptions/{id} | /api/v1/delivery-exceptions/{id} |
| Delivery Exceptions | DELETE | /delivery-exceptions/{id} | /api/v1/delivery-exceptions/{id} |
| Token Books | POST | /token-books/identities/ | /api/v1/token-books/identities/ |
| Token Books | GET | /token-books/identities/ | /api/v1/token-books/identities/ |
| Token Books | GET | /token-books/identities/{id} | /api/v1/token-books/identities/{id} |
| Token Books | GET | /token-books/identities/customer/{id} | /api/v1/token-books/identities/customer/{id} |
| Token Books | PUT | /token-books/identities/{id} | /api/v1/token-books/identities/{id} |
| Token Books | DELETE | /token-books/identities/{id} | /api/v1/token-books/identities/{id} |
| Token Books | POST | /token-books/issues/ | /api/v1/token-books/issues/ |
| Token Books | GET | /token-books/issues/ | /api/v1/token-books/issues/ |
| Token Books | GET | /token-books/issues/{id} | /api/v1/token-books/issues/{id} |
| Token Books | GET | /token-books/issues/identity/{id} | /api/v1/token-books/issues/identity/{id} |
| Token Books | PUT | /token-books/issues/{id} | /api/v1/token-books/issues/{id} |
| Token Books | DELETE | /token-books/issues/{id} | /api/v1/token-books/issues/{id} |
| Token Books | POST | /token-books/payments/ | /api/v1/token-books/payments/ |
| Token Books | GET | /token-books/payments/ | /api/v1/token-books/payments/ |
| Token Books | GET | /token-books/payments/{id} | /api/v1/token-books/payments/{id} |
| Token Books | GET | /token-books/payments/issue/{id} | /api/v1/token-books/payments/issue/{id} |
| Token Books | PUT | /token-books/payments/{id} | /api/v1/token-books/payments/{id} |
| Token Books | DELETE | /token-books/payments/{id} | /api/v1/token-books/payments/{id} |
| Deliveries | POST | /deliveries/sessions/ | /api/v1/deliveries/sessions/ |
| Deliveries | GET | /deliveries/sessions/ | /api/v1/deliveries/sessions/ |
| Deliveries | GET | /deliveries/sessions/{id} | /api/v1/deliveries/sessions/{id} |
| Deliveries | POST | /deliveries/sessions/{id}/start | /api/v1/deliveries/sessions/{id}/start |
| Deliveries | POST | /deliveries/sessions/{id}/dispatch | /api/v1/deliveries/sessions/{id}/dispatch |
| Deliveries | POST | /deliveries/sessions/{id}/close | /api/v1/deliveries/sessions/{id}/close |
| Deliveries | GET | /deliveries/sessions/{id}/checklist | /api/v1/deliveries/sessions/{id}/checklist |
| Deliveries | GET | /deliveries/sessions/{id}/reconciliation | /api/v1/deliveries/sessions/{id}/reconciliation |
| Deliveries | GET | .../reconciliation/summary | /api/v1/deliveries/sessions/{id}/reconciliation/summary |
| Deliveries | GET | .../reconciliation/customers | /api/v1/deliveries/sessions/{id}/reconciliation/customers |
| Deliveries | POST | .../reconciliation/validate | /api/v1/deliveries/sessions/{id}/reconciliation/validate |
| Deliveries | POST | .../reconciliation/submit | /api/v1/deliveries/sessions/{id}/reconciliation/submit |
| Deliveries | POST | .../reconciliation/cash-sales | /api/v1/deliveries/sessions/{id}/reconciliation/cash-sales |
| Deliveries | DELETE | .../reconciliation/cash-sales/{id} | /api/v1/deliveries/sessions/{id}/reconciliation/cash-sales/{id} |
| Deliveries | GET | /deliveries/sessions/{id}/report | /api/v1/deliveries/sessions/{id}/report |
| Delivery Edit | PUT | /deliveries/{id} | /api/v1/deliveries/{id} |
| Delivery Edit | POST | /deliveries/unplanned | /api/v1/deliveries/unplanned |
| Delivery Edit | POST | /deliveries/{id}/register-token | /api/v1/deliveries/{id}/register-token |
| Delivery Edit | POST | /deliveries/validate-token | /api/v1/deliveries/validate-token |
| Delivery Edit | GET | /deliveries/customer/{id}/token-status | /api/v1/deliveries/customer/{id}/token-status |
| Delivery Edit | PUT | /deliveries/{id}/edit | /api/v1/deliveries/{id}/edit |
| Delivery Edit | GET | /deliveries/{id}/warnings | /api/v1/deliveries/{id}/warnings |
| Delivery Edit | GET | /deliveries/session/{id} | /api/v1/deliveries/session/{id} |
| Delivery Edit | POST | /deliveries/session/{id}/reopen | /api/v1/deliveries/session/{id}/reopen |
| Delivery Edit | GET | /deliveries/session/{id}/edit-history | /api/v1/deliveries/session/{id}/edit-history |
| Payments | POST | /payments/ | /api/v1/payments/ |
| Payments | GET | /payments/ | /api/v1/payments/ |
| Payments | GET | /payments/{id} | /api/v1/payments/{id} |
| Payments | GET | /payments/customer/{id} | /api/v1/payments/customer/{id} |
| Payments | PUT | /payments/{id} | /api/v1/payments/{id} |
| Payments | DELETE | /payments/{id} | /api/v1/payments/{id} |
| Payments | POST | /payments/bills/generate | /api/v1/payments/bills/generate |
| Payments | GET | /payments/bills/ | /api/v1/payments/bills/ |
| Payments | GET | /payments/bills/{id} | /api/v1/payments/bills/{id} |
| Payments | GET | /payments/bills/customer/{id} | /api/v1/payments/bills/customer/{id} |
| Payments | PUT | /payments/bills/{id}/status | /api/v1/payments/bills/{id}/status |
| Payments | GET | /payments/outstanding/{id} | /api/v1/payments/outstanding/{id} |
| Reports | GET | /reports/route-delivery | /api/v1/reports/route-delivery |
| Reports | GET | /reports/revenue | /api/v1/reports/revenue |
| Reports | GET | /reports/collection-efficiency | /api/v1/reports/collection-efficiency |
| Reports | GET | /reports/customer/{id}/consumption | /api/v1/reports/customer/{id}/consumption |
| Reports | GET | /reports/token-utilization | /api/v1/reports/token-utilization |
| Reports | GET | /reports/dashboard | /api/v1/reports/dashboard |

### Important API Notes

1. **Response format inconsistency**: Some endpoints return `{"success": true, "data": {...}}`, others return the model directly, and list endpoints return arrays. The API client layer must handle this per endpoint.
2. **Auth returns**: `{"access_token": "...", "token_type": "bearer"}` — no user info. Must call `/auth/me` separately.
3. **Delivery sessions use custom list format**: `{"sessions": [...], "total": N}` — not a plain array.
4. **Reports use envelope format**: `{"data": [...], "total": N, "page": 1, "page_size": 50, "generated_at": "..."}`.
5. **No refresh token endpoint is actually used** based on current code — the backend has a `/auth/refresh` path documented but not implemented. Token expiry handling should use the 401 interceptor approach.

---

## Database Impact

**No backend database changes are required for the frontend.** All necessary data is already exposed through the existing API. However, the following database-adjacent observations are important:

| Item | Impact |
|---|---|
| No new tables needed | All required data is already modeled |
| Enum/lookup data | Routes, milk types, employees are reference data needed in dropdowns. Frontend must cache these (TanStack Query with long staleTime). |
| Sequence numbers | Customer code, employee code, token numbers are auto-generated server-side. Frontend does not generate them. |
| Soft delete flag | Frontend must handle `is_active: false` — show inactive records with a visual indicator, or provide a "Show inactive" toggle. |

---

## UI Considerations

### Layout Structure

```
┌─────────────────────────────────────────────┐
│  Header: Logo | Page Title | User | Logout   │
├──────────┬──────────────────────────────────┤
│          │                                   │
│ Sidebar  │          Main Content             │
│ (collaps)│                                   │
│          │                                   │
│ - Dashboard                                  │
│ - Master Data  ▶                             │
│   - Routes                                   │
│   - Customers                                │
│   - Milk Types                               │
│   - Employees                                │
│ - Operations   ▶                             │
│   - Subscriptions                            │
│   - Exceptions                               │
│   - Token Identities                         │
│   - Token Book Issues                        │
│   - Token Book Payments                      │
│ - Delivery     ▶                             │
│   - Sessions                                 │
│   - Checklist                                │
│ - Finance      ▶                             │
│   - Payments                                 │
│   - Bills                                    │
│   - Outstanding                              │
│ - Reports      ▶                             │
│   - Dashboard                                │
│   - Route Delivery                           │
│   - Revenue                                  │
│   - Consumption                              │
│   - Token Utilization                        │
│   - Collection Efficiency                    │
└──────────┴──────────────────────────────────┘
```

### Color Palette (Tailwind CSS Default)

- **Primary**: indigo-600 (buttons, links, active nav)
- **Success**: emerald-500 (delivered, paid, balanced, active)
- **Warning**: amber-500 (pending, partial, unconfirmed)
- **Danger**: red-500 (not delivered, cancelled, overdue, unbalanced)
- **Info**: sky-500 (info badges, in-progress states)
- **Neutral**: slate-50 (background), slate-800 (text)

### Status Badge Mapping

| Status | Color |
|---|---|
| ACTIVE | emerald |
| INACTIVE | slate |
| DELIVERED | emerald |
| PENDING_TOKEN | amber |
| CASH_SALE | sky |
| NOT_DELIVERED | red |
| CANCELLED | red |
| PLANNED | slate |
| STARTED | sky |
| COMPLETED | indigo |
| CLOSED | emerald |
| BALANCED | emerald |
| UNBALANCED | red |
| PAID | emerald |
| PARTIAL | amber |
| OVERDUE | red |
| PREPAID | indigo |
| POSTPAID | amber |

### Loading & Error Patterns

1. **Page load**: Use React Suspense with skeleton components (table rows, card placeholders).
2. **Action loading**: Button shows spinner icon + disabled state during mutations.
3. **Error toasts**: `react-hot-toast` for API errors. Auto-dismiss after 5s.
4. **Form errors**: Inline below the field. Server validation errors mapped to the corresponding field.
5. **Empty state**: Illustration + "No [items] found" + CTA button if permitted.

---

## Security Considerations

| ID | Consideration | Mitigation |
|---|---|---|
| SC-1 | JWT stored in localStorage | Acceptable for this scope. In production, consider httpOnly cookies. Document this as a known pattern. |
| SC-2 | XSS via user input | Backend sanitizes. Frontend uses React's default escaping. No `dangerouslySetInnerHTML`. |
| SC-3 | CSRF | Not applicable — JWT in Authorization header (not cookie-based). |
| SC-4 | Role escalation | All protected routes also check role on the client. Server enforces role regardless. Client-side guards are UX convenience, not security. |
| SC-5 | Token interception | Use HTTPS in production. Dev uses HTTP (localhost is acceptable). |

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Backend response format inconsistent across endpoints | High — API client needs per-endpoint handling | Medium | Create a thin wrapper per module that normalizes responses |
| Backend lacks some filtering/sorting capabilities | Medium — frontend may need to filter client-side | Low | If missing, document as backend gap for future enhancement |
| Large number of endpoints to cover (~80+) | Medium — phase planning critical | High | Strict phase prioritization; build list+create before detail/edit |
| Role-based permission matrix complex | Medium — sidebar and route guards must match backend exactly | Medium | Single source of truth: a permissions config object |
| No refresh token mechanism | Medium — users may need to re-login every 30 min | High | Document. Can add refresh later. For now, frequent re-login is acceptable for v1. |

---

## Assumptions

| ID | Assumption |
|---|---|
| A-1 | Backend will be modified to add CORS and `/api/v1` prefix before frontend development starts. |
| A-2 | Backend `/auth/me` endpoint returns `{id, username, role}` which is sufficient for role-based routing. |
| A-3 | The existing backend is running at `http://localhost:8000` during development. |
| A-4 | PostgreSQL database is already set up and seeded with test data. |
| A-5 | No refresh token endpoint will be implemented in Phase 1. Token expiry (30 min) will result in 401 redirect to login. |
| A-6 | The frontend will not implement offline support — network connectivity is assumed. |
| A-7 | Tailwind CSS will be used for styling (utility-first, no component library). |
| A-8 | All list endpoints support at minimum the query params `skip` and `limit` (or equivalent pagination). |

---

## Open Questions

| Q# | Question | Decision Needed By |
|---|---|---|
| Q1 | Should the old root-level routes be removed or kept for backward compatibility? | Backend dev / Phase 1 |
| Q2 | Should we add a refresh token endpoint to avoid 30-min forced re-login? | Phase 1 or Phase 8 |
| Q3 | Should the frontend use a lightweight component library (shadcn/ui, Radix) or pure Tailwind? | 🔒 Resolved: Pure Tailwind CSS |
| Q4 | For the delivery registration flow, should it be a single-page wizard or a tabbed interface? | 🔒 Resolved: All-in-one scrollable page with Dispatch → Register → Reconciliation → Close sections |
| Q5 | Should CSV download from reports open in a new tab or trigger a download via blob? | Before Phase 7 |
| Q6 | Is there a need for a "Switch Role" feature for the Owner to view as Checker? | Future consideration |
| Q7 | Should toast notifications be used for success confirmation, or inline success banners? | Before Phase 1 |

---

## Acceptance Criteria

| # | Criteria | Verification |
|---|---|---|
| AC-1 | Backend CORS allows `http://localhost:5173` | 200 response from frontend to backend |
| AC-2 | All API routes accessible under `/api/v1/` | Curl test against new prefix |
| AC-3 | `GET /api/v1/health` returns 200 | Curl test |
| AC-4 | React app starts with `npm run dev` on port 5173 | Manual check |
| AC-5 | Login page renders, form submits, token stored in localStorage | End-to-end flow |
| AC-6 | Protected routes redirect to `/login` when unauthenticated | Manual test |
| AC-7 | Unauthorized role sees 403 page/redirect | Role-specific test |
| AC-8 | Sidebar navigation only shows links for user's role | Log in as each role and verify |
| AC-9 | Customer list page loads and displays data | Visual check |
| AC-10 | Create customer form validates required fields and submits | Fill form, check network tab |
| AC-11 | Delivery session creation flow works end-to-end | Create → dispatch → register → reconcile → close |
| AC-12 | Dashboard page loads with operational KPIs | Visual check |
| AC-13 | Error toasts appear on API failure | Trigger 400/500, verify toast |
| AC-14 | 401 globally redirects to login with toast | Wait for token expiry, make request |

---

## Implementation Notes

### Phase 1: Backend Prep + Frontend Scaffold + Auth

**Backend tasks:**
1. Add `CORSMiddleware` to `app/main.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. Create an umbrella `api_router = APIRouter(prefix="/api/v1")` at `app/routers/__init__.py` or in `main.py`. Include sub-routers under it.
3. Add `@app.get("/api/v1/health")` endpoint returning status.
4. Keep existing root routes but add deprecation log.

**Frontend tasks:**
1. `npm create vite@latest frontend -- --template react-ts`
2. Install dependencies
3. Configure Vite proxy in `vite.config.ts`
4. Create folder structure
5. Implement `AuthContext`, `api/client.ts` with interceptor
6. Implement `LoginPage`
7. Implement `ProtectedRoute`, `RoleGuard`
8. Implement `AppLayout` with sidebar (static links for Phase 1)
9. Implement `DashboardPage` (basic welcome + role display)
10. Set up TanStack Query provider
11. Set up toast provider

### Phase 2: Master Data Pages

Build list + create + edit + delete for:
- Routes
- Customers
- Milk Types
- Employees
- Users (list + create only, since user management is simple)

For each module:
1. `types/<module>.ts` — TypeScript interfaces
2. `api/<module>.ts` — API client functions
3. `hooks/use<Module>.ts` — TanStack Query hooks
4. Pages: `ListPage`, `FormPage` (create/edit combined)

### Phase 3: Subscription & Exception Pages

1. Subscription list (with customer/milk-type/route info)
2. Subscription create/edit form (select customer, select milk type, morning/evening qty)
3. Exception list (with subscription, customer, route info)
4. Exception create form (select subscription, exception type, date range)

### Phase 4: Token Book Pages

1. Token Identity list + create
2. Token Book Issue list + create (link to identity, issue number)
3. Token Book Payment list + create (link to issue, amount paid)

### Phase 5: Delivery Management Pages

This is the most complex phase — build the Checker's daily workflow. The session detail page uses an all-in-one scrollable layout.

1. **Session List** — filterable by date, route, status
2. **Session Create** — select route, date, shift, delivery partner
3. **Session Detail (all-in-one scrollable)** — single page with sections:
   - **Dispatch Section** — enter total milk loaded (shown only when status=PLANNED)
   - **Checklist/Register Section** — table of expected customers. For each row: status dropdown, token sheet input, token validation, warning acknowledgment, add unplanned delivery button
   - **Reconciliation Section** — loaded vs registered vs cash vs returned. Enter cash sales and returned milk. View balance status. Submit/Validate buttons.
   - **Close Section** — close session button (shown only when balanced)
   - **Summary Section** — session report after close (read-only)

### Phase 6: Payment Pages

1. Payment list with filters (customer, mode, date range)
2. Payment create form
3. Bill list and generate form
4. Outstanding balance view

### Phase 7: Report Pages

1. Dashboard → Display the `OperationalDashboard` KPIs in cards/grid
2. Route Delivery Report → date range picker + route selector + table
3. Revenue Report → date range + charts (optional, at least a table)
4. Customer Consumption → customer selector + date range + trend display
5. Token Utilization → table with utilization percentage bars
6. Collection Efficiency → table with aging columns

### Phase 8: Polish

1. Global error boundary
2. Loading skeletons on all pages
3. Empty state illustrations
4. Responsive sidebar (hamburger on mobile)
5. Form autofocus and keyboard navigation
6. Confirmation dialogs on delete/close/cancel actions
7. Performance: React.memo on table rows, lazy load route pages
8. 404 page for unknown routes

---

## Frontend Project Structure (Final)

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance + interceptors
│   │   ├── auth.ts
│   │   ├── routes.ts
│   │   ├── customers.ts
│   │   ├── milk-types.ts
│   │   ├── employees.ts
│   │   ├── subscriptions.ts
│   │   ├── delivery-exceptions.ts
│   │   ├── token-books.ts
│   │   ├── delivery-sessions.ts
│   │   ├── deliveries.ts
│   │   ├── payments.ts
│   │   └── reports.ts
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── DataTable.tsx
│   │   │   ├── ConfirmDialog.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── guards/
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── RoleGuard.tsx
│   │   └── forms/
│   │       ├── CustomerForm.tsx
│   │       ├── RouteForm.tsx
│   │       └── ... etc
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useRoutes.ts
│   │   ├── useCustomers.ts
│   │   ├── useMilkTypes.ts
│   │   ├── useEmployees.ts
│   │   ├── useSubscriptions.ts
│   │   ├── useDeliveryExceptions.ts
│   │   ├── useTokenBooks.ts
│   │   ├── useDeliverySessions.ts
│   │   ├── useDeliveries.ts
│   │   ├── usePayments.ts
│   │   └── useReports.ts
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── ChangePasswordPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── NotFoundPage.tsx
│   │   ├── ForbiddenPage.tsx
│   │   ├── users/
│   │   ├── routes/
│   │   ├── customers/
│   │   ├── milk-types/
│   │   ├── employees/
│   │   ├── subscriptions/
│   │   ├── delivery-exceptions/
│   │   ├── token-books/
│   │   ├── delivery/
│   │   ├── payments/
│   │   └── reports/
│   ├── providers/
│   │   ├── AuthProvider.tsx
│   │   └── QueryProvider.tsx
│   ├── types/
│   │   ├── auth.ts
│   │   ├── route.ts
│   │   ├── customer.ts
│   │   ├── milk-type.ts
│   │   ├── employee.ts
│   │   ├── subscription.ts
│   │   ├── delivery-exception.ts
│   │   ├── token-identity.ts
│   │   ├── token-book.ts
│   │   ├── delivery-session.ts
│   │   ├── daily-delivery.ts
│   │   ├── payment.ts
│   │   ├── reports.ts
│   │   └── common.ts
│   ├── config/
│   │   └── permissions.ts          # Role-permission mapping
│   ├── lib/
│   │   ├── utils.ts                # cn(), formatDate(), etc.
│   │   └── constants.ts            # Status enums, color maps
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css                   # Tailwind directives
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── .gitignore
```

### Vite Proxy Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### Backend `main.py` Changes (Outline)

```python
# app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# ... existing imports ...

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 umbrella router
api_v1 = APIRouter(prefix="/api/v1")

# Include all sub-routers under api_v1
api_v1.include_router(user_router)
api_v1.include_router(auth_router)
# ... all other routers ...

app.include_router(api_v1)

# Health endpoint
@api_v1.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Keep legacy root routes (deprecated)
app.include_router(legacy_user_router)  # if keeping backward compat
# ... etc ...

@app.get("/")
def home():
    return {"message": "Milk Management API"}
```

---

## Vite Configuration Summary

The `vite.config.ts` proxy is the critical piece linking frontend and backend during development. It forwards all `/api/*` requests to the backend running on port 8000, which means:

- The frontend Axios `baseURL` should be `/api/v1` (not `http://localhost:8000/api/v1`).
- CORS is handled by the Vite proxy during development, **but** the backend CORS middleware is still needed for any direct access (e.g., from Postman, or if the frontend is served separately).
- In production, a reverse proxy (nginx/Caddy) would serve the built frontend from `/` and proxy `/api/*` to the backend.

---

## Dependencies (npm)

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "axios": "^1.7.0",
    "@tanstack/react-query": "^5.50.0",
    "react-hot-toast": "^2.4.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.4.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@tanstack/react-query-devtools": "^5.50.0"
  }
}
```

---

## Definition of Done

A phase is considered complete when:

1. All pages in the phase render without console errors.
2. All CRUD operations work end-to-end with real API calls.
3. Role guards correctly restrict access.
4. Error toasts appear on API failures.
5. Loading states display during data fetching.
6. Empty states display when no data exists.
7. Form validation shows inline errors for invalid inputs.
8. The sidebar navigation is correct for each role tested.
9. No TypeScript compilation errors.
10. Build succeeds with `npm run build`.
