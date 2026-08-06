# CURRENT_STATE.md - Project Snapshot

> Snapshot of the project as of August 6, 2026 — Sprints 1–7 backend complete; Sprint 8 AI BI (specs/010) fully complete incl. E2E + quickstart (all tasks T001–T037); Frontend Phases 1–7 + AI Insights page complete (Phase 3–4 = Sprint 10, Phase 5 Delivery Management per specs/007, Phase 6 Payment Management per specs/008, Phase 7 Reports Pages per specs/009 — Sprint 13, commit 4489d6a; AI Insights per specs/010). Verified against source Aug 6, 2026.

---

## Quick Facts

| Metric | Value |
|--------|-------|
| Total Tables | **17** (16 model files: users, routes, customers, milk_types, employees, subscriptions, delivery_exceptions, token_identities, token_book_issues, token_book_payments, delivery_sessions, daily_deliveries, session_edits, token_sheet_warnings, customer_bills, customer_bill_items, customer_payments) |
| Total API Endpoints | **~90** (39 original + 26 delivery + 14 payment + 6 reports + 5 AI) |
| Total Test Files | **14** (auth, users, routes, customers, milk_types, employees, subscriptions, delivery_exceptions, token_books, daily_delivery, delivery_edit, payments, reports, ai) |
| Test Status | **466 passed, 0 failed** (plus pre-existing server-dependent `scripts/test_subscriptions.py`, needs live server) |
| Sprints Code-Complete | **8** (1, 2, 3, 4-core, 5, 6, 7, 8-AI) |
| Sprints Tested | **8** (1, 2, 3, 4-core, 5, 6, 7, 8-AI) |
| Frontend Status | **Phases 1–7 + AI Insights complete** — Phase 1 (Setup/Auth/Layout) + Phase 2 (Master Data CRUD) [Sprint 9]; Phase 3 (Subscriptions & Exceptions) + Phase 4 (Token Books) [Sprint 10]; Phase 5 (Delivery Management) [specs/007]; Phase 6 (Payment Management) [specs/008]; Phase 7 (Reports Pages) [specs/009, commit 4489d6a]; AI Insights `/reports/ai` [specs/010]. Phase 8 (Polish) pending |
| Next Priority | **Frontend Phase 8: Polish & Testing** (feature phases complete; AI E2E spec T035 + quickstart T036 done — full spec 010 checklist green) |
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
| app/constants/ | 3 | Enum definitions (roles, shifts, statuses) — note: UserRole enum missing ADMIN/EMPLOYEE (see TECH_DEBT B4) |
| app/models/ | 16 (17 classes) | SQLAlchemy models (CustomerBillItem lives in customer_bill.py) |
| app/schemas/ | 16 | Pydantic schemas (incl. delivery, payment, reports, ai) |
| app/routers/ | 14 | API routers (incl. deliveries, delivery_edit, payments, reports, ai) |
| app/services/ | 14 + ai/ (6) + reports/ (8) | Business logic (incl. delivery_*, payment_service, ai/*, reports) |
| app/exceptions/ | 13 + base | Custom exceptions (incl. delivery, delivery_edit, payment, ai) |
| tests/ | 14 test files + conftest | Test suite (466 tests) |
| alembic/versions/ | 13 | Database migrations (merged heads + payment tables + report indexes + delivery_exceptions.shift) |
| scripts/ | 4 | seed.py, seed_history.py, test_subscriptions.py, e2e_backend.py (E2E DB reset + API on :8001) |
| frontend/src/ | ~115 files | React SPA (Phases 1–7 + AI Insights: 6 report pages + AI page + 5 AI components + types/api/hooks) |

---

## Quick Start for New AI Session

1. **Read this file** (`CURRENT_STATE.md`) for a 30-second overview
2. **Read `PROJECT_CONTEXT.md`** for complete understanding
3. **Read `ARCHITECTURE.md`** for system design
4. **Read `DATABASE.md`** for schema details
5. **Read `API_REFERENCE.md`** for endpoint details
6. **Run tests**: `pytest` to verify everything works
7. **Start coding**: Follow patterns in existing services/routers
8. **Frontend work**: Phases 1–7 + AI Insights complete. Read `specs/010-ai-insights-module/tasks.md` (Sprint 14 AI — T001–T037 all done, incl. E2E T035 + quickstart T036) and `specs/004-react-frontend/tasks.md` (Phase 8 — pending) for task lists

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

# Seed 30 days of operational history (sessions, deliveries, bills, payments) for the AI pages:
python -m scripts.seed_history

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

- Date: August 6, 2026
- Last Sprint Code Completed: Sprint 8 AI BI (specs/010, all tasks T001–T037 incl. E2E + quickstart); frontend `npm run build` + oxlint green
- Last Sprint Fully Tested: Sprint 8 (AI — 87 tests in `tests/test_ai.py`, incl. edge-case coverage); Frontend E2E suite green (52 Playwright specs across 9 spec files, incl. new `frontend/e2e/ai.spec.ts` + setup/owner.setup.ts)
- Test Files: 14 backend + 9 frontend Playwright spec files
- Tests: 466 backend + 52 E2E
- Tables: 17
- Frontend: Phases 1–7 + AI Insights complete (Phase 8 Polish pending)
- Known Bugs: 1 — **revenue report returns empty JSON envelope on cache hit** (`app/routers/reports.py`; see TECH_DEBT B3). All 466 backend tests + 52 E2E tests (incl. `frontend/e2e/ai.spec.ts`, T035) are green. Quickstart T036 validated (stats/RBAC/degradation/regression; live-LLM smoke is manual). `scripts/e2e_backend.py` sets both `REPORT_CACHE_DISABLED=1` and `AI_LLM_DISABLED=1`.
