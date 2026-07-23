---
name: Database Migration
description: Create safe Alembic migrations
invokable: true
---

Create or update Alembic migrations.

Rules:

- Read the existing models.
- Understand the schema changes.
- Generate safe migrations.
- Preserve existing data.
- Avoid destructive operations unless explicitly requested.

Verify:

- Foreign keys
- Constraints
- Indexes
- Default values
- Rollback compatibility

Return the migration and explain the schema changes.