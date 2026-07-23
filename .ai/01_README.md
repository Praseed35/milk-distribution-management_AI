# AI Knowledge Base

## Purpose

The `.ai` directory contains the permanent knowledge required for AI coding assistants working on the Milk Distribution Management System.

Every AI assistant must read these documents before generating, modifying, or reviewing code.

The goal is to ensure that all generated code follows the project's architecture, coding standards, and business workflow.

---

# Reading Order

Always read the files in the following order.

1. README.md
2. project_context.md
3. architecture.md
4. folder_structure.md
5. business_rules.md
6. coding_rules.md
7. service_patterns.md
8. database_guidelines.md
9. authentication_flow.md
10. error_handling.md
11. naming_conventions.md
12. coding_examples.md
13. migrations.md
14. testing.md
15. module_map.md
16. feature_status.md
17. development_rules.md
18. prompts.md

---

# Project Overview

Project Name

Milk Distribution Management System

Purpose

Digitize the workflow of traditional milk distribution businesses while preserving their existing business process.

The application models real-world operations such as:

- Customer management
- Route management
- Delivery planning
- Token book management
- Cash sales
- Milk allocation
- Reconciliation
- Reporting

The system prioritizes correctness, maintainability, and business accuracy over rapid feature development.

---

# Technology Stack

Backend

- Python 3
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Alembic
- Pydantic v2
- JWT Authentication

Frontend (Planned)

- React
- TypeScript

---

# Architecture Principles

The project follows a layered architecture.

```
HTTP Request
      │
      ▼
Router
      │
      ▼
Dependency Injection
      │
      ▼
Service
      │
      ▼
SQLAlchemy ORM
      │
      ▼
Database
```

Business logic belongs only inside the Service layer.

Routers should remain thin.

Models should only define ORM mappings.

Schemas should define request and response models.

---

# Folder Responsibilities

The application is organized as follows.

```
app/

common/
constants/
core/
exceptions/
models/
routers/
schemas/
services/
utils/

database.py
dependencies.py
main.py
```

Each folder has a single responsibility.

Never move code into another layer without approval.

---

# AI Responsibilities

Before writing code

- Read the relevant `.ai` documents.
- Understand the business workflow.
- Check the existing implementation.
- Reuse existing patterns.

While writing code

- Follow the project architecture.
- Keep routers thin.
- Place business logic inside services.
- Use SQLAlchemy ORM.
- Reuse existing utilities.
- Avoid duplicate code.
- Maintain consistent naming.

After writing code

- Verify imports.
- Update documentation if required.
- Ensure new code matches the existing style.
- Check for backward compatibility.

---

# General Rules

Always

- Preserve business workflow.
- Follow the current project architecture.
- Write maintainable code.
- Use type hints.
- Prefer reusable components.
- Keep functions focused on a single responsibility.

Never

- Invent business rules.
- Rewrite unrelated files.
- Introduce duplicate logic.
- Expose internal implementation details.
- Break existing APIs without approval.
- Modify architecture without approval.

---

# Documentation Strategy

The project uses two documentation systems.

## docs-v1/

Human-readable project documentation.

Contains

- Business documentation
- API specification
- Database design
- Workflows
- Architecture
- Roadmap

## .ai/

AI-specific documentation.

Contains

- Coding rules
- Architecture guidance
- Development workflow
- Naming conventions
- Examples
- Patterns
- AI instructions

Do not duplicate documentation between these folders.

---

# AI Goal

The AI should behave like a senior backend engineer.

Every change should

- respect the existing architecture,
- preserve business rules,
- minimize unnecessary modifications,
- and produce clean, maintainable, production-quality code.

When uncertain, prefer understanding the existing implementation over making assumptions.