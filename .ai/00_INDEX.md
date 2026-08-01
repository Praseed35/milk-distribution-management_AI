# .ai/ Directory Index - Quick Navigation for AI Assistants

> Start here when joining this project.

---

## Essential Files (Read These First)

| File | Purpose | When to Read |
|------|---------|--------------|
| **`PROJECT_CONTEXT.md`** | Complete project overview, all modules, patterns, status | First file to read |
| **`ARCHITECTURE.md`** | System design, layering, security, data flow | Before any coding |
| **`DATABASE.md`** | All **17** tables with columns, constraints, relationships | Before DB changes |
| **`API_REFERENCE.md`** | Every endpoint with request/response schemas | Before API changes |
| **`BUSINESS_RULES.md`** | All business domain rules enforced in code | Before feature work |
| **`current_state.md`** | Quick snapshot, file counts, patterns, templates | Quick reference |

## Planning and Status Files

| File | Purpose |
|------|---------|
| `TODO.md` | Sprint-based development roadmap |
| `TECH_DEBT.md` | Known issues and improvement opportunities |
| `feature_status.md` | Module completion status |
| `module_map.md` | Module dependency graph |

## Development Guidelines

| File | Purpose |
|------|---------|
| `development_rules.md` | Coding conventions and development process |
| `database_schema.md` | Database design principles and planned tables |

## Legacy/Reference Files (numbered prefix)

| File | Purpose |
|------|---------|
| `01_README.md` | Original project README |
| `02_project_context.md` | Earlier version of project context |
| `03_architecture.md` | Earlier version of architecture |
| `04_folder_structure.md` | Folder structure reference |
| `05_business_rules.md` | Earlier business rules |
| `06_coding_rules.md` | Earlier coding rules |
| `07_service_patterns.md` | Service pattern guide |
| `08_database_guidelines.md` | Database guidelines |
| `09_authentication_flow.md` | Auth flow documentation |
| `10_error_handling.md` | Error handling patterns |
| `11_naming_conventions.md` | Naming convention guide |
| `12_business_workflows.md` | Business workflow documentation |
| `13_api_design_guidelines.md` | API design guidelines |
| `14_testing_guidelines.md` | Testing approach |
| `15_deployment_and_environment.md` | Deployment guide |
| `16_module_implementation_guide.md` | Module implementation guide |

---

## For AI Assistants

### If starting a new feature:
1. Read `PROJECT_CONTEXT.md`
2. Read `ARCHITECTURE.md`
3. Read `DATABASE.md` for schema understanding
4. Read `BUSINESS_RULES.md` for domain rules
5. Follow `development_rules.md` for coding patterns

### If debugging an issue:
1. Read `DATABASE.md` for schema details
2. Read `API_REFERENCE.md` for expected behavior
3. Read `BUSINESS_RULES.md` for constraints
4. Check `TECH_DEBT.md` for known issues

### If continuing development:
1. Read `TODO.md` for sprint roadmap
2. Read `feature_status.md` for module status
3. Read `CURRENT_STATE.md` for patterns and templates
4. Read `module_map.md` for dependency understanding

---

## Last Updated: August 1, 2026

**Note**: All 14 backend modules (Master Data → Reports & Analytics) implemented and tested. **379 tests passing across 13 test files** (13th migration `a1b2c3d4e5f6` added `shift` to `delivery_exceptions`). Frontend: **Phases 1–6 complete** — Phase 1–2 (Sprint 9, commit `d14589b4`), Phase 3–4 (Sprint 10, commit `f536667f`), Phase 5 Delivery Management (specs/007 all tasks done, incl. backend fixes: `POST /deliveries/sessions/{id}/complete`, server-side OWNER RBAC on edit/reopen, checklist auto-generation on session create), Phase 6 Payment Management (specs/008, all 20 tasks done: payments/bills/outstanding pages + 7 E2E specs). Full Playwright E2E suite (38 specs) is green. Phases 7–8 (Reports, Polish) pending. See `feature_status.md` for detailed completion status.
