# CURRENT_STATE.md - Project Snapshot

> Snapshot of the project as of July 2026.

---

## Quick Facts

| Metric | Value |
|--------|-------|
| Total Tables | 10 |
| Total API Endpoints | ~40 |
| Total Tests | 218 |
| Test Status | All passing |
| Sprints Completed | 3 (1, 2, 4-core) |
| Next Sprint | Sprint 3 (Daily Delivery) |
| Database | PostgreSQL localhost:5432/milk_managemen_ai |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (30min, HS256) |
| Python Version | 3.10+ (uses `str | None` syntax) |

---

## File Count by Directory

| Directory | Files | Purpose |
|-----------|-------|---------|
| app/core/ | 4 | Security, auth, config, roles |
| app/constants/ | 3 | Enum definitions |
| app/models/ | 10 (+ __init__) | SQLAlchemy models |
| app/schemas/ | 10 (+ __init__) | Pydantic schemas |
| app/routers/ | 9 (+ __init__) | API routers |
| app/services/ | 9 (+ __init__) | Business logic |
| app/exceptions/ | 9 (+ __init__, + base) | Custom exceptions |
| tests/ | 10 test files + conftest | Test suite |
| alembic/versions/ | 8 | Database migrations |
| scripts/ | 2 | Seed + test helper |

---

## Quick Start for New AI Session

1. **Read this file** (`CURRENT_STATE.md`) for a 30-second overview
2. **Read `PROJECT_CONTEXT.md`** for complete understanding
3. **Read `ARCHITECTURE.md`** for system design
4. **Read `DATABASE.md`** for schema details
5. **Read `API_REFERENCE.md`** for endpoint details
6. **Run tests**: `pytest` to verify everything works
7. **Start coding**: Follow patterns in existing services/routers

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
8. Register router in `app/main.py`
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

- Date: July 26, 2026
- Last Sprint Completed: Sprint 4 (Core Token Book Management)
- Test Count: 218
- Tables: 10
