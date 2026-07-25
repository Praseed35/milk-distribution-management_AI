# Milk Management AI

A FastAPI-based backend system for managing milk distribution operations.

## Features

- **Customer Management** - Registration with auto-generated customer codes, route assignment
- **Subscription Management** - Link customers to milk types with morning/evening shift quantities
- **Delivery Exceptions** - Temporary modifications to subscriptions (vacation, no milk, holiday)
- **Route Management** - Delivery routes that group customers geographically
- **Milk Type Management** - Product catalog (e.g., "Full Cream Milk 1000ml", "Toned Milk 500ml")
- **User Authentication** - JWT-based authentication with role-based access control
- **Employee Management** - Employee records with optional user linking

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic v2

## Project Structure

```
app/
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
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure database in `alembic.ini` or set environment variables

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Seed the database:
   ```bash
   python scripts/seed.py
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
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

| Username | Role |
|----------|------|
| owner | OWNER |
| checker1 | CHECKER |
| delivery1 | DELIVERY_PARTNER |
| admin | OWNER |
