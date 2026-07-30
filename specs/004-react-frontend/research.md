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
