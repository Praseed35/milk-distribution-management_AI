# Database: Milk Management AI

## Configuration

- **Engine:** PostgreSQL via SQLAlchemy 2.0
- **Connection:** `postgresql://postgres:admin@localhost:5432/milk_managemen_ai`
- **Pool:** Default SQLAlchemy pool (no NullPool in production; NullPool used in Alembic migrations)
- **Session:** `sessionmaker(autocommit=False, autoflush=False)`
- **Migrations:** Alembic with 5 versioned migrations

## Tables (Implemented)

### `users`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| username | String(100) | UNIQUE, NOT NULL |
| password_hash | String(255) | NOT NULL |
| role | String(50) | NOT NULL |
| is_active | Boolean | NOT NULL, DEFAULT true |

**No timestamps.** No relationship declarations.

### `routes`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, INDEX |
| route_code | String | UNIQUE, NOT NULL |
| route_name | String | UNIQUE, NOT NULL |
| description | String | NULLABLE |
| is_active | Boolean | NOT NULL, DEFAULT true |
| created_at | DateTime(tz) | server_default=now() |
| updated_at | DateTime(tz) | server_default=now(), onupdate=now() |

**Relationships:** `customers` → Customer (one-to-many, back_populates="route")

### `customers`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, INDEX |
| customer_code | String(20) | UNIQUE, NOT NULL |
| customer_name | String(100) | NOT NULL |
| primary_phone | String(15) | UNIQUE, NOT NULL |
| alternate_phone | String(15) | NULLABLE |
| address | String(255) | NULLABLE |
| route_id | Integer | FK → routes.id, NOT NULL |
| remarks | String(255) | NULLABLE |
| is_active | Boolean | NOT NULL, DEFAULT true |
| created_at | DateTime(tz) | server_default=now() |
| updated_at | DateTime(tz) | server_default=now(), onupdate=now() |

**Relationships:** `route` → Route (many-to-one), `subscriptions` → Subscription (one-to-many)

### `milk_types`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, INDEX |
| milk_name | String(100) | UNIQUE, NOT NULL |
| volume_ml | Integer | NOT NULL |
| description | String(255) | NULLABLE |
| is_active | Boolean | NOT NULL, DEFAULT true |
| created_at | DateTime(tz) | server_default=now() |
| updated_at | DateTime(tz) | server_default=now(), onupdate=now() |

**No relationships declared.** (Subscription references it via FK)

### `employees`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK |
| name | String(100) | NOT NULL |
| phone | String(20) | NOT NULL |
| address | String(255) | NULLABLE |
| is_active | Boolean | DEFAULT true |
| user_id | Integer | FK → users.id, NULLABLE |

**No timestamps.** No relationship declarations.

### `subscriptions`
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, INDEX |
| customer_id | Integer | FK → customers.id, NOT NULL |
| milk_type_id | Integer | FK → milk_types.id, NOT NULL |
| morning_quantity | Integer | NOT NULL, DEFAULT 0 |
| evening_quantity | Integer | NOT NULL, DEFAULT 0 |
| status | String(20) | NOT NULL, DEFAULT "ACTIVE" |
| start_date | DateTime(tz) | server_default=now(), NOT NULL |
| end_date | DateTime(tz) | NULLABLE |
| remarks | String(255) | NULLABLE |
| is_active | Boolean | NOT NULL, DEFAULT true |
| created_at | DateTime(tz) | server_default=now() |
| updated_at | DateTime(tz) | server_default=now(), onupdate=now() |

**Relationships:** `customer` → Customer (many-to-one), `milk_type` → MilkType (many-to-one, no back_populates)

## Entity Relationship Diagram

```
users ──────────────┐
                    │ (user_id, nullable)
employees ──────────┘
                    
routes ─────────────┐
                    │ (route_id)
customers ──────────┘
                    │
                    │ (customer_id)
subscriptions ──────┤
                    │ (milk_type_id)
milk_types ─────────┘
```

## Migration Chain

```
cd5183b67dae (initial: users + routes)
  → de893ed2ffb7 (add customers)
    → 1154a3a25414 (placeholder: schema change)
      → 4085a4134c96 (add milk_types + employees)
        → 2a032b2352b4 (add subscriptions)
```

## Tables Planned But Not Created

| Table | Purpose |
|-------|---------|
| token_books | Daily token accounting per customer |
| milk_allocations | Daily milk allocation per route/shift |
| cash_sales | Walk-in cash sales records |
| reconciliations | Payment and delivery reconciliation records |
| leave_requests | Employee leave management |

## Notable Issues

1. **No timestamps on users/employees** — `users` and `employees` lack `created_at`/`updated_at`
2. **String columns without length** — `routes.route_code` and `routes.route_name` use `String` without length constraint
3. **No DB-level indexes** — Only `id` columns are indexed; common query columns (customer_code, route_id, status) lack indexes
4. **No cascade rules** — FK relationships have no `ondelete`/`onupdate` cascade behavior defined
5. **Hardcoded credentials** — Database URL with password is hardcoded in `app/database.py` instead of using environment variables
