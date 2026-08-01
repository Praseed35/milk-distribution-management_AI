# CURRENT_STATE.md - Project Snapshot

> Snapshot of the project as of August 1, 2026 — Sprints 1–7 backend complete; Frontend Phases 1–5 complete (Phase 3–4 = Sprint 10, Phase 5 Delivery Management per specs/007).

---

## Quick Facts

| Metric | Value |
|--------|-------|
| Total Tables | **17** (16 model files: users, routes, customers, milk_types, employees, subscriptions, delivery_exceptions, token_identities, token_book_issues, token_book_payments, delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings, customer_bills, customer_bill_items, customer_payments) |
| Total API Endpoints | **~85** (39 original + 26 delivery + 14 payment + 6 reports) |
| Total Test Files | **13** (auth, users, routes, customers, milk_types, employees, subscriptions, delivery_exceptions, token_books, daily_delivery, delivery_edit, payments, reports) |
| Test Status | **379 passed, 0 failed** |
| Sprints Code-Complete | **7** (1, 2, 3, 4-core, 5, 6, 7) |
| Sprints Tested | **7** (1, 2, 3, 4-core, 5, 6, 7) |
| Frontend Status | **Phases 1–5 complete** — Phase 1 (Setup/Auth/Layout) + Phase 2 (Master Data CRUD) [Sprint 9]; Phase 3 (Subscriptions & Exceptions) + Phase 4 (Token Books) [Sprint 10]; Phase 5 (Delivery Management) [specs/007]. Phases 6–8 (Payments, Reports, Polish) pending |
| Next Priority | **Frontend Phase 6: Payments pages** (then Phase 7 Reports, Phase 8 Polish) |
| Database | PostgreSQL localhost:5432/milk_managemen_ai |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (30min, HS256) |
| API Prefix | `/api/v1` (primary) + root-level legacy routes (deprecated, kept for backward compat) |
| CORS | Configured for http://localhost:5173 |
| Python Version | 3.10+ (uses `str \| None` syntax) |

---

## File Count by Directory (Actual)

| Directory | Files | Purpose |
|-----------|-------|---------|
| app/core/ | 4 | Security, auth, config, roles |
| app/constants/ | 3 | Enum definitions (roles, shifts, statuses) |
| app/models/ | 16 (17 classes) | SQLAlchemy models (CustomerBillItem lives in customer_bill.py) |
| app/schemas/ | 16 | Pydantic schemas (incl. delivery, payment, reports) |
| app/routers/ | 13 | API routers (incl. deliveries, delivery_edit, payments, reports) |
| app/services/ | 15 + reports/ (8) | Business logic (incl. delivery_*, payment_service, reports) |
| app/exceptions/ | 11 + base | Custom exceptions (incl. delivery, delivery_edit, payment) |
| tests/ | 13 test files + conftest | Test suite (379 tests) |
| alembic/versions/ | 13 | Database migrations (merged heads + payment tables + report indexes + delivery_exceptions.shift) |
| scripts/ | 2 | Seed + test helper |
| frontend/src/ | ~90 files | React SPA (Phases 1–5 complete; payments/reports page dirs empty) |

---

## Quick Start for New AI Session

1. **Read this file** (`CURRENT_STATE.md`) for a 30-second overview
2. **Read `PROJECT_CONTEXT.md`** for complete understanding
3. **Read `ARCHITECTURE.md`** for system design
4. **Read `DATABASE.md`** for schema details
5. **Read `API_REFERENCE.md`** for endpoint details
6. **Run tests**: `pytest` to verify everything works
7. **Start coding**: Follow patterns in existing services/routers
8. **Frontend work**: Phases 1–5 complete. Read `specs/004-react-frontend/tasks.md` (Phase 6–8 pending) and `specs/007-delivery-management-pages/tasks.md` (Phase 5 — all done) for task lists

---

## Key Patterns to Follow

### Adding a New Module
1. Create model in `app/models/{name}.py`
2. Add import to `app/models/__init__.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "add {name}"`
4. Create schemas in `app/schemas/{name}.py`
5. Create exceptions in `app/exceptions/{name}.py`
6. Create service in `app/services/{name}_service.py`
7. Create router in `app/routers/{name}.py`
8. Register router in `app/main.py` (both `api_v1` umbrella AND legacy root section)
9. Create tests in `tests/test_{name}.py`
10. Add seed data in `scripts/seed.py`

### Service Function Template
```python
def create(db: Session, data: CreateSchema) -> Model:
    # Validate FK exists
    existing = db.query(FKModel).filter(FKModel.id == data.fk_id).first()
    if not existing:
        raise ForeignKeyNotFoundError()
    if not existing.is_active:
        raise InactiveForeignKeyError()
    
    # Validate uniqueness
    duplicate = db.query(Model).filter(Model.field == data.field).first()
    if duplicate:
        raise DuplicateFieldError(data.field)
    
    # Create and save
    new = Model(field=data.field)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new
```

### Router Function Template
```python
@router.post("/", response_model=ResponseSchema, status_code=201)
def create(data: CreateSchema, db: Session = Depends(get_db)):
    try:
        return service.create(db, data)
    except ForeignKeyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Test Function Template
```python
class TestCreateEntity:
    def test_success(self, client, db_session, seed_fk):
        response = client.post("/entities/", json={...})
        assert response.status_code == 201
        assert response.json()["field"] == expected_value
    
    def test_not_found(self, client, db_session):
        response = client.post("/entities/", json={...})
        assert response.status_code == 404
    
    def test_validation_error(self, client, db_session):
        response = client.post("/entities/", json={...})
        assert response.status_code == 422
```

---

## Database Reset Commands

```bash
# After running tests, restore seed data:
python -m scripts.seed

# Full database reset:
alembic downgrade base
alembic upgrade head
python -m scripts.seed

# Create new migration after model changes:
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Last Updated

- Date: August 1, 2026
- Last Sprint Code Completed: Sprint 7 (Reports & Analytics) — backend; Sprint 10 (Frontend Phases 3–4) + Phase 5 Delivery Management — frontend
- Last Sprint Fully Tested: Sprint 7 (Reports & Analytics)
- Test Files: 13 (delivery + delivery_edit + payments + reports)
- Tests: 379
- Tables: 17
- Frontend: Phases 1–5 complete (of 8)
- Known Bugs: 0
