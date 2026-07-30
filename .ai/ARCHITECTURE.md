# ARCHITECTURE.md - System Architecture

> Detailed architecture documentation for the Milk Management ERP Backend.

---

## 1. Application Entry Point

**File**: `app/main.py`

```python
app = FastAPI()
# 13 routers registered (line 30-40):
#   user, auth, route, customer, milk_type, subscription,
#   employee, delivery_exception, token_book, deliveries,
#   delivery_edit, payments, reports
# GET "/" returns {"message": "Milk Management API"}
```

The app is a standard FastAPI application with no middleware, no CORS, no startup/shutdown events. All routers are registered at module level via `app.include_router()`.

**Delivery routers**:
- `deliveries` (prefix `/deliveries/sessions`) — session lifecycle + reconciliation
- `delivery_edit` (prefix `/deliveries`) — delivery CRUD + token registration + edit

---

## 2. Dependency Injection

### Database Session
**File**: `app/dependencies.py`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Every router endpoint receives `db: Session = Depends(get_db)`.

### Authentication
**File**: `app/core/auth.py`

```python
def get_current_user(token, db) -> User:
    # Decodes JWT, looks up user by username
```

### Role Authorization
**File**: `app/core/roles.py`

```python
def require_role(allowed_roles: list):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(403, "Access denied")
        return current_user
    return role_checker
```

Usage in router:
```python
@router.post("/")
def create(..., current_user=Depends(require_role(["OWNER"]))):
```

---

## 3. Security Pipeline

**File**: `app/core/security.py`

```
Password -> bcrypt hash -> stored in DB
Login -> verify password -> create JWT (sub=username, role=role)
Request -> decode JWT -> lookup user -> inject as current_user
```

**JWT Configuration** (`app/core/config.py`):
- Algorithm: HS256
- Expiry: 30 minutes
- Secret: hardcoded `milk_management_secret_key_2026`
- Token URL: `auth/login` (for Swagger UI OAuth2)

---

## 4. Service Pattern

All services follow the same pattern:

```python
# Module-level functions (not a class)
def create(db: Session, data: CreateSchema) -> Model:
    # 1. Validate foreign key exists and is active
    # 2. Check business rules (duplicates, constraints)
    # 3. Raise custom exception if violated
    # 4. Create model instance
    # 5. db.add() + db.commit() + db.refresh()
    # 6. Return model object

def get_all(db: Session) -> list[Model]:
    # Query with is_active == True filter
    # For complex modules, use joined queries returning list[dict]

def get_by_id(db: Session, id: int) -> Model:
    # Query by id + is_active == True
    # Raise NotFound if missing

def update_by_id(db: Session, id: int, data: UpdateSchema) -> Model:
    # Find existing + is_active
    # Validate constraints
    # Update fields
    # commit + refresh

def delete_by_id(db: Session, id: int) -> Model:
    # Find existing + is_active
    # Set is_active = False
    # commit + refresh
```

### Response Patterns

**Simple modules** (Routes, MilkTypes, Users): Return model objects directly. Pydantic `from_attributes=True` handles serialization.

**Complex modules** (Subscriptions, DeliveryExceptions, TokenBooks): Return manually constructed dicts from joined queries, because the response needs data from multiple tables.

---

## 5. Exception Flow

```
Service raises DomainException
    -> Router catches it
    -> Maps to HTTPException with appropriate status code
    -> FastAPI returns JSON error response
```

**Exception naming convention**: `{Entity}{Reason}Error` (e.g., `DuplicateRouteCodeError`, `RouteNotFoundError`)

**Note**: Some exceptions extend `BusinessException` (from `base.py`), others extend `Exception` directly. This is inconsistent.

---

## 6. Data Flow Diagrams

### Customer Creation
```
POST /customers/
  -> customers.py router
  -> customer_service.create(db, CustomerCreate)
    -> Validate route exists and is active
    -> Validate phone not duplicate
    -> Validate primary != alternate phone
    -> Auto-generate customer_code (C{NNNNN})
    -> Create Customer instance
    -> db.add + commit + refresh
  <- Return Customer object
  <- HTTP 200 with CustomerResponse
```

### Subscription Detail Retrieval
```
GET /subscriptions/{id}
  -> subscriptions.py router
  -> subscription_service.get_by_id(db, subscription_id)
    -> Joined query: Subscription + Customer + MilkType
    -> Construct nested dict:
       { id, customer: {...}, milk_type: {...}, quantities, status, dates }
  <- HTTP 200 with SubscriptionDetailResponse
```

### Token Book Payment Creation
```
POST /token-books/payments/
  -> token_books.py router
  -> token_book_service.create_payment(db, TokenBookPaymentCreate)
    -> Validate TokenBookIssue exists
    -> Validate amount_paid <= book_price
    -> Calculate balance = book_price - amount_paid
    -> Auto-determine status: PAID/PARTIAL/PENDING
    -> Create TokenBookPayment instance
    -> db.add + commit + refresh
  <- HTTP 201 with TokenBookPaymentResponse
```

### Delivery Session Lifecycle
```
POST /deliveries/sessions/
  -> deliveries.py router
  -> delivery_service.create_session(db, route_id, date, shift, partner_id)
    -> Validate route exists
    -> Validate employee exists
    -> Check no duplicate session (route+date+shift)
    -> Create DeliverySession (status=PLANNED)
    -> db.add + commit + refresh
  <- HTTP 201 with DeliverySessionResponse

POST /deliveries/sessions/{id}/dispatch
  -> deliveries.py router
  -> delivery_service.record_dispatch(db, session_id, total_milk_loaded)
    -> Validate session exists and is PLANNED
    -> Validate dispatch not already recorded
    -> Set total_milk_loaded, status=STARTED
    -> commit + refresh
  <- HTTP 200 with DeliverySessionResponse

GET /deliveries/sessions/{id}/checklist
  -> deliveries.py router
  -> Queries DailyDelivery records for session
  -> Constructs ChecklistCustomer list with name, address, phone, milk_type, quantity
  <- HTTP 200 with DeliveryChecklistResponse

POST /deliveries/sessions/{id}/close
  -> deliveries.py router
  -> delivery_reconciliation.calculate_reconciliation(db, session_id)
    -> Sum token registered, cash sales, returned milk
    -> Calculate difference = loaded - accounted
    -> Check if |difference| < 0.01
  -> delivery_service.close_session(db, session_id, is_balanced)
    -> Validate session is COMPLETED
    -> Raise SessionNotBalancedError if not balanced
    -> Set status=CLOSED, reconciliation_status=BALANCED
  <- HTTP 200 with DeliverySessionResponse
```

### Token Registration
```
POST /deliveries/{id}/register-token
  -> delivery_edit.py router
  -> delivery_registration.register_token(db, delivery_id, sheet_number, ...)
    -> Validate delivery exists
    -> delivery_registration.validate_token_sheet(db, customer_id, milk_type_id, sheet_number)
      -> Check for active token book
      -> Check sheet number in range
      -> Check sheet not already used
      -> Detect non-sequential / out-of-order sheets
      -> Detect old books with remaining sheets
      -> Return is_valid, warnings, requires_acknowledgment
    -> If warnings require acknowledgment, check acknowledged_warnings list
    -> Update delivery: set token_sheet_number, status=DELIVERED, delivered_quantity=planned
    -> Update book: current_sheet = sheet_number + 1
    -> commit + refresh
  <- HTTP 200 with TokenRegistrationResponse
```

### Reconciliation Calculation
```
GET /deliveries/sessions/{id}/reconciliation
  -> deliveries.py router
  -> delivery_reconciliation.calculate_reconciliation(db, session_id)
    -> Query all active deliveries for session
    -> token_registered = SUM(delivered_quantity WHERE status=DELIVERED)
    -> cash_sales = SUM(delivered_quantity WHERE status=CASH_SALE)
    -> returned_milk = session.total_returned_milk
    -> loaded_milk = session.total_milk_loaded
    -> total_accounted = token_registered + cash_sales + returned_milk
    -> difference = loaded_milk - total_accounted
    -> is_balanced = abs(difference) < 0.01
  <- HTTP 200 with ReconciliationResponse
```

---

## 7. Authentication Flow

```
1. Client: POST /auth/login {username, password}
   -> auth_service.login()
   -> Verify credentials against DB
   -> Generate JWT with {sub: username, role: role, exp: now+30min}
   <- {access_token: "...", token_type: "bearer"}

2. Client: GET /auth/me  (Header: Authorization: Bearer <token>)
   -> oauth2_scheme extracts token
   -> get_current_user() decodes JWT, looks up User
   <- {id, username, role}

3. Client: GET /auth/owner-dashboard  (Header: Authorization: Bearer <token>)
   -> require_role(["OWNER"]) checks user.role
   <- 200 if OWNER, 403 if not
```

---

## 8. Database Connection

**File**: `app/database.py`

```python
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/milk_managemen_ai"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

All models inherit from `Base`. Alembic uses `Base.metadata` for migration generation.

**Alembic** (`alembic/env.py`):
- Imports all models via `import app.models`
- Uses `Base.metadata` as target
- Connects via `alembic.ini` sqlalchemy.url

---

## 9. Migration History

9 migrations in chronological order:

| Migration | Description |
|-----------|-------------|
| `cd5183b67dae` | Initial schema (users, routes) |
| `de893ed2ffb7` | Add customers table |
| `4085a4134c96` | Add milk_types and employees tables |
| `b3c4d5e6f7a8` | Add employee fields (employee_code, role, route_id, user_id, timestamps) |
| `2a032b2352b4` | Add subscriptions table |
| `3f8a1b2c4d5e` | Create delivery_exceptions table |
| `4e5f6a7b8c9d` | Create token_books tables (3 tables) |
| **`5a6b7c8d9e0f`** | **Create delivery tables (delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings)** |
| `1154a3a25414` | Remove is_active in update customer (EMPTY — no upgrade/downgrade logic) |

---

## 10. Reports Module

**Files**: `app/routers/reports.py`, `app/schemas/reports.py`, `app/services/reports/`

### Architecture

Reports are read-only — no new database tables. All data is computed via SQL aggregation queries against existing tables.

```
Router (reports.py)
  └─→ Service (route_delivery.py, revenue.py, ...)
        └─→ SQLAlchemy aggregation queries on existing tables
        └─→ Returns list[dict] or dict
  └─→ Cache (cache.py)
        └─→ In-memory dict with TTL (300s dashboard/revenue, 60s others)
        └─→ Bypass with ?refresh=true
  └─→ CSV (common.py: generate_csv_response)
        └─→ io.StringIO + csv.DictWriter + StreamingResponse
```

### Report Types

| Endpoint | Route | Roles |
|----------|-------|-------|
| Route Delivery | `GET /reports/route-delivery` | OWNER, ADMIN, CHECKER, DELIVERY_PARTNER |
| Revenue | `GET /reports/revenue` | OWNER only |
| Collection Efficiency | `GET /reports/collection-efficiency` | OWNER, ADMIN |
| Customer Consumption | `GET /reports/customer/{id}/consumption` | OWNER, ADMIN, CHECKER |
| Token Utilization | `GET /reports/token-utilization` | OWNER, ADMIN |
| Operational Dashboard | `GET /reports/dashboard` | OWNER, ADMIN, CHECKER, DELIVERY_PARTNER |

### RBAC Strategy

- `DELIVERY_PARTNER` automatically scoped to assigned route via `Employee.route_id`
- Revenue (financial data) restricted to `OWNER` only
- Collection/token data restricted to `OWNER`/`ADMIN`
- Public (authenticated): route delivery, consumption, dashboard
- `?format=csv` triggers `StreamingResponse` with `Content-Disposition` header

---

## 11. Testing Architecture

**File**: `tests/conftest.py`

```
Session-scoped:
  setup_teardown_db -> drop_all + create_all (start) / drop_all + create_all (end)

Per-test:
  db_session -> begin transaction -> yield -> rollback
  client -> TestClient(app) with overridden get_db
  seed_* -> create test data within the rolled-back transaction
```

The key insight: every test runs inside a transaction that is rolled back, so the database state is always clean between tests, even though real PostgreSQL is used.

---

## 12. Constants and Enums

**File**: `app/constants/statuses.py`

Defines enums for status management. **Delivery service code imports these enums**, but they are not enforced as DB column type constraints (stored as plain strings).

| Enum | Values | Used In |
|------|--------|---------|
| SessionStatus | PLANNED, STARTED, COMPLETED, CLOSED | `delivery_service.py` (state machine) |
| PaymentStatus | PAID, PENDING, PARTIAL | Token book payments |
| TokenStatus | COLLECTED, PENDING, CARRY_FORWARD | Not used yet |
| DeliveryStatus | DELIVERED, PENDING_TOKEN, CASH_SALE, NOT_DELIVERED, SKIPPED, CANCELLED | `delivery_registration.py` |
| DeliverySource | PLANNED, UNPLANNED | `delivery_registration.py` |
| WarningCode | NON_SEQUENTIAL_SHEET, SHEET_OUT_OF_ORDER, GAP_DETECTED, SHEET_ALREADY_USED, NEW_BOOK_BEFORE_OLD_FINISHED | `delivery_registration.py` (token validation) |
| ReconciliationStatus | BALANCED, UNBALANCED, PENDING | `delivery_reconciliation.py` |
| ExceptionType | VACATION, NO_MILK, HOLIDAY | Delivery exceptions |
| ExceptionStatus | ACTIVE, COMPLETED, CANCELLED | Delivery exceptions |
| BookIssueStatus | WAITING, ACTIVE, COMPLETED | Token book issues |
| PaymentMode | PREPAID, POSTPAID | Token book payments |

**File**: `app/constants/roles.py`
```python
class UserRole(str, Enum):
    OWNER = "OWNER"
    CHECKER = "CHECKER"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"
```
Note: EMPLOYEE role is used in code but not defined in this enum.

**File**: `app/constants/shifts.py`
```python
class Shift(str, Enum):
    MORNING = "MORNING"
    EVENING = "EVENING"
```
Used in schema validation patterns but not enforced as DB constraint.

---

## 13. Frontend Readiness

**Current state**: Backend only. No CORS configured. No OpenAPI customization.

**For future React frontend**:
- CORS middleware needed in `main.py`
- API prefix (`/api/v1`) should be added
- Rate limiting not implemented
- No WebSocket support
- No file upload support
