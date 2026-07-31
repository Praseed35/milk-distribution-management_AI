# Research: React Frontend for Milk Distribution ERP

## Technology Decisions

### Frontend Framework: React 18 + Vite 5 + TypeScript
- **Decision**: React 18 SPA with Vite 5 build tool and TypeScript
- **Rationale**: Vite is the recommended build tool for new React projects. TypeScript provides type safety matching the backend's Pydantic schemas. React 18 is stable and widely supported.
- **Alternatives considered**: Next.js (SSR overhead not needed for internal ERP), Create React App (deprecated), Vue/Svelte (team familiarity assumed with React)

### HTTP Client: Axios
- **Decision**: Axios with baseURL `/api/v1` and auth interceptor
- **Rationale**: Built-in interceptor pattern for JWT attachment and 401 handling. Cleaner API than fetch() for request/response transforms.
- **Alternatives considered**: fetch() (more boilerplate), ky (less ecosystem)

### Server State Management: TanStack Query (React Query v5)
- **Decision**: Use TanStack Query for all API data fetching
- **Rationale**: Built-in caching, background refetching, retry logic, loading/error states. Reduces boilerplate vs manual useEffect + useState patterns.
- **Alternatives considered**: Redux Toolkit Query (heavier), SWR (similar but less feature-rich)

### Styling: Tailwind CSS
- **Decision**: Tailwind CSS 3 with utility-first approach
- **Rationale**: No component library dependency. Consistent design system via Tailwind config. Small bundle with purging.
- **Alternatives considered**: shadcn/ui (component library dependency), Material UI (heavy, opinionated), plain CSS (inconsistent)

### Routing: React Router v6
- **Decision**: React Router v6 with nested layouts and route guards
- **Rationale**: Industry standard for React SPAs. Supports layout routes, loaders, and error boundaries.
- **Alternatives considered**: TanStack Router (newer, less ecosystem)

### Auth Flow: localStorage JWT + 401 interceptor
- **Decision**: Store JWT in localStorage, attach via Axios interceptor, redirect on 401
- **Rationale**: Simple, works within the existing backend auth model (30min expiry, no refresh token endpoint)
- **Alternatives considered**: httpOnly cookies (requires backend changes), sessionStorage (lost on tab close)

### Toast Notifications: react-hot-toast
- **Decision**: react-hot-toast for success/error/info toasts
- **Rationale**: Lightweight (~5KB), no dependencies, simple API
- **Alternatives considered**: sonner (newer, fewer features), react-toastify (heavier)

### Testing (deferred to Phase 8): Vitest + React Testing Library
- **Decision**: Vitest for unit tests, React Testing Library for component tests
- **Rationale**: Vitest is the standard for Vite projects. RTL encourages testing behavior over implementation.
- **Alternatives considered**: Jest (slower, requires separate config), Cypress (E2E, heavy for Phase 1)

## Backend Changes

### CORS Middleware
- **Decision**: Add `CORSMiddleware` allowing `http://localhost:5173` with credentials, all methods/headers
- **Rationale**: Required for direct frontend-to-backend access. Vite proxy handles dev CORS, but backend needs CORS for any external access.

### API Prefix `/api/v1`
- **Decision**: Create an umbrella `APIRouter(prefix="/api/v1")`, include all sub-routers under it. Keep existing root-level routers for backward compatibility.
- **Rationale**: Clean separation between old and new API paths. Frontend exclusively uses `/api/v1/`. Old paths remain for existing scripts but are deprecated.
- **Alternatives considered**: Mounting sub-app (complex), middleware-based rewriting (fragile)

### Health Endpoint
- **Decision**: Add `GET /api/v1/health` returning `{"status": "ok", "version": "1.0.0", "timestamp": "..."}`
- **Rationale**: Quick health check for frontend and monitoring tooling.

## Edge Cases from Spec

| Edge Case | Approach |
|-----------|----------|
| Token expired mid-session | Axios 401 interceptor catches, clears token, redirects to login, preserves attempted URL in sessionStorage |
| Network offline | TanStack Query retries 3x, then shows error toast. No offline mode. |
| Concurrent edit on delivery | Backend returns 409. Toast "Modified by another user. Please refresh." |
| Duplicate phone | Backend 400. Show inline error on phone field. |
| Empty list states | DataTable shows "No records found" with optional Create button |
| Large datasets | Pagination (default page_size=50), search/filter where available |
| 30-min forced re-login | Accepted tradeoff for v1. Noted for refresh token enhancement. |

## Phase 3 Research: Subscriptions & Exceptions (verified against backend 2026-07-31)

### Response shape — plain arrays, no envelope
- **Decision**: `GET /subscriptions/` and `GET /delivery-exceptions/` return plain JSON arrays of flat list DTOs. The api modules type them as `SubscriptionListResponse[]` / `DeliveryExceptionListResponse[]` directly.
- **Rationale**: Verified in `app/routers/subscriptions.py` (response_model=`list[SubscriptionListResponse]`) and `app/routers/delivery_exceptions.py` (`list[DeliveryExceptionListResponse]`). No pagination envelope — frontend does not paginate these lists (client-side sort only).
- **Alternatives considered**: Treating list as `PaginatedResponse` (wrong — no `total`/`page` fields present).

### Subscription create/update field sets
- **Decision**: `SubscriptionCreate` = `customer_id, milk_type_id, morning_quantity, evening_quantity, status, remarks`. `SubscriptionUpdate` = `morning_quantity, evening_quantity, status, remarks`. **No `start_date`/`end_date` accepted on create** — these are response-only (server assigns `start_date`).
- **Rationale**: Verified against `app/schemas/subscription.py`. The earlier `data-model.md` draft included `start_date`/`end_date` on create — corrected. `morning_quantity`/`evening_quantity` default to 0 with `ge=0`.
- **Alternatives considered**: Keeping the draft create shape (would cause 422s — rejected).

### List vs Detail DTO split
- **Decision**: Use two TS interfaces per module. List: flat joined fields (`customer_name`, `customer_code`, `route_name`, `milk_type_name`, `milk_type_volume` for subscriptions; `customer_id`, `customer_code`, `customer_name`, `route_name` for exceptions). Detail: nested objects (`customer: CustomerSummaryResponse`, `milk_type: MilkTypeSummaryResponse`; `subscription: SubscriptionSummaryResponse` for exceptions).
- **Rationale**: Backend defines distinct `*ListResponse` and `*DetailResponse` schemas with different shapes. The edit form loads detail via `GET /subscriptions/{id}`; the table renders the list DTO.
- **Alternatives considered**: A single unified interface with optional fields (loses type safety — rejected).

### Exception field specifics
- **Decision**: `DeliveryExceptionCreate` = `subscription_id, exception_type, start_date, end_date?, reason?` — `end_date` and `reason` are optional. `exception_type` constrained to `VACATION | NO_MILK | HOLIDAY` (constant `EXCEPTION_TYPES` already in `lib/constants.ts`). Update adds optional `status`.
- **Rationale**: Verified against `app/schemas/delivery_exception.py`. Earlier draft marked `end_date`/`reason` required — corrected.

### Filtering strategy
- **Decision**: Customer filter on subscriptions uses the dedicated `GET /subscriptions/customer/{id}`; subscription filter on exceptions uses `GET /delivery-exceptions/subscription/{id}`. Route-level filtering is client-side (filter on `route_name` field) because backend list endpoints accept no query params.
- **Rationale**: Backend provides only these two filtered endpoints. Spec risk table row 2 ("backend lacks some filtering") applies; documented as a backend gap for future enhancement.
- **Alternatives considered**: Adding backend query params (out of Phase 3 scope — no backend changes in this phase).
