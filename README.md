# Milk Distribution ERP

Full-stack ERP for milk distribution with a FastAPI backend and React frontend.

## Features

- **Customer Management** - Registration with auto-generated customer codes, route assignment
- **Subscription Management** - Link customers to milk types with morning/evening shift quantities
- **Delivery Exceptions** - Temporary modifications to subscriptions (vacation, no milk, holiday)
- **Route Management** - Delivery routes that group customers geographically
- **Milk Type Management** - Product catalog (e.g., "Full Cream Milk 1000ml", "Toned Milk 500ml")
- **User Authentication** - JWT-based authentication with role-based access control
- **Employee Management** - Employee records with optional user linking

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic v2

### Frontend (`frontend/`)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS v4
- **Routing**: React Router v7
- **Data Fetching**: TanStack Query v5 + Axios
- **Notifications**: react-hot-toast
- **Error Tracking**: Sentry (optional)

## Project Structure

```
app/                # FastAPI backend
├── core/           # Security, auth, config, roles
├── constants/      # Enum definitions (roles, shifts, statuses)
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response schemas
├── routers/        # FastAPI route handlers
├── services/       # Business logic layer
├── exceptions/     # Custom exception classes
├── database.py     # Engine, SessionLocal, Base
├── dependencies.py # get_db(), oauth2_scheme
└── main.py         # FastAPI app creation + router registration

frontend/           # React SPA
└── src/
    ├── api/        # Axios API functions per module
    ├── components/ # Reusable UI, layout, guards
    ├── hooks/      # TanStack Query hooks per module
    ├── pages/      # Page components grouped by module
    ├── providers/  # AuthProvider, QueryProvider
    ├── types/      # TypeScript interfaces
    └── lib/        # Utility functions
```

## Setup

### Backend

```bash
pip install -r requirements.txt
# Configure database in alembic.ini
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `GET /auth/owner-dashboard` - Owner-only dashboard

### Users
- `GET /users/` - List all users
- `POST /users/` - Create new user

### Routes
- `GET /routes/` - List active routes
- `GET /routes/{id}` - Get route by ID
- `POST /routes/` - Create route
- `PUT /routes/{id}` - Update route
- `DELETE /routes/{id}` - Soft-delete route

### Customers
- `GET /customers/` - List active customers
- `GET /customers/{id}` - Get customer by ID
- `POST /customers/` - Create customer (auto-generates code)
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Soft-delete customer

### Milk Types
- `GET /milk-types/` - List active milk types
- `GET /milk-types/{id}` - Get milk type by ID
- `POST /milk-types/` - Create milk type
- `PUT /milk-types/{id}` - Update milk type
- `DELETE /milk-types/{id}` - Soft-delete milk type

### Subscriptions
- `GET /subscriptions/` - List active subscriptions
- `GET /subscriptions/{id}` - Get subscription detail
- `GET /subscriptions/customer/{id}` - Get by customer
- `POST /subscriptions/` - Create subscription
- `PUT /subscriptions/{id}` - Update subscription
- `DELETE /subscriptions/{id}` - Deactivate subscription

### Delivery Exceptions
- `GET /delivery-exceptions/` - List active delivery exceptions
- `GET /delivery-exceptions/{id}` - Get exception detail with subscription info
- `GET /delivery-exceptions/subscription/{id}` - Get exceptions by subscription
- `POST /delivery-exceptions/` - Create delivery exception
- `PUT /delivery-exceptions/{id}` - Update delivery exception
- `DELETE /delivery-exceptions/{id}` - Cancel delivery exception

## Testing

```bash
pytest
```

## Default Users (after seeding)

| Username | Password | Role |
|----------|----------|------|
| owner | owner123 | OWNER |
| checker1 | checker123 | CHECKER |
| delivery1 | delivery123 | DELIVERY_PARTNER |
| admin | admin123 | OWNER |
| employee1 | emp123 | EMPLOYEE |

## Frontend Status (Sprint 9)

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Setup, Auth, Layout | ✅ Complete |
| 2 | Master Data CRUD (Routes, Customers, Milk Types, Employees, Users) | ✅ Complete |
| 3 | Subscriptions & Exceptions | ⏳ Pending |
| 4 | Token Books | ⏳ Pending |
| 5 | Delivery Sessions | ⏳ Pending |
| 6 | Payments | ⏳ Pending |
| 7 | Reports | ⏳ Pending |
| 8 | Testing | ⏳ Pending |
