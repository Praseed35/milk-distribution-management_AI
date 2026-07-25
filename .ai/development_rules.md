# Development Rules

## Before Coding

1. Read `.ai/PROJECT_CONTEXT.md` and `.ai/ARCHITECTURE.md`
2. Read the relevant `docs/` files for the feature area
3. Understand the current architecture and patterns
4. Explain implementation plan before coding
5. Wait for approval

## While Coding

### Architecture Rules
- Services are **module-level functions**, not classes
- Services accept `db: Session` as first parameter
- Services return **SQLAlchemy model objects** (not schemas)
- Services raise **custom exceptions** for business rule violations
- Routers catch exceptions and map to HTTP status codes
- **No repository layer** - services query models directly

### File Naming
- Models: `app/models/{entity_name}.py` (snake_case, singular)
- Schemas: `app/schemas/{entity_name}.py` (snake_case, singular)
- Services: `app/services/{entity_name}_service.py` (snake_case, singular, underscore service)
- Routers: `app/routers/{entity_name_plural}.py` (snake_case, plural)
- Exceptions: `app/exceptions/{entity_name}.py` (snake_case, singular)
- Tests: `tests/test_{entity_name_plural}.py` (snake_case, plural)

### Coding Style
- Import each symbol on its own line (per project convention)
- Explicit formatting with one attribute per line for models/schemas
- Use `Field(...)` with explicit constraints
- Use `ConfigDict(from_attributes=True)` on all Response schemas
- No type hints on service return types for simple cases (per project convention)

### Database Rules
- Every table must have `is_active` boolean for soft delete
- Every table (except users) must have `created_at` and `updated_at`
- Use `ForeignKey("table_name.id")` for relationships
- Use `relationship("ModelName", back_populates="field")` for ORM relationships
- Generate Alembic migration for every model change

### API Rules
- Use kebab-case for URL paths: `/delivery-exceptions/`
- Use plural nouns: `/customers/`, `/subscriptions/`
- Create endpoints: `status_code=201`
- List endpoints: `response_model=list[Schema]`
- Detail endpoints: `response_model=DetailSchema`
- Soft-delete endpoints: return the deactivated object

### Schema Rules
- Create: All required fields, no optional (except optional FKs)
- Update: All fields optional (partial update)
- Response: Includes id, is_active, timestamps
- ListResponse: Flat fields from joined queries
- DetailResponse: Nested objects (CustomerSummaryResponse, etc.)
- Use Summary schemas for nested objects in detail responses

### Exception Rules
- One file per domain: `app/exceptions/{domain}.py`
- Naming: `{Entity}{Reason}Error` (e.g., `RouteNotFoundError`)
- Constructor with descriptive message
- Router catches and maps: NotFound -> 404, Duplicate -> 400, Invalid -> 400

### Test Rules
- One test file per module
- Classes per endpoint group: `TestCreate`, `TestGet`, `TestUpdate`, `TestDelete`
- Test success, error, edge cases, validation failures
- Use seed fixtures for test data
- Each test runs in rolled-back transaction

## After Coding

1. Update documentation in `.ai/` directory
2. Verify all imports are correct
3. Run `pytest` - all tests must pass
4. If model changes, create Alembic migration
5. Keep commits small and focused

## Never

- Break business rules
- Break API compatibility (additive changes only)
- Delete or overwrite history
- Introduce duplicate logic
- Skip the service layer
- Put business logic in routers
- Put business logic in models
- Skip validation in schemas
- Return raw database objects without checking is_active
- Hardcode values that should be configurable
- Modify existing test data in seed script (add new, don't change existing)
