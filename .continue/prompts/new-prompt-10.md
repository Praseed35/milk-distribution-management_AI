---
name: Optimize Code
description: Improve performance while preserving behavior
invokable: true
---

Analyze the implementation.

Look for:

- Slow SQLAlchemy queries
- N+1 queries
- Duplicate database access
- Unnecessary object creation
- Expensive loops
- Memory issues
- API performance
- Transaction optimization

Do not change business logic.

Suggest and implement only safe optimizations.

Explain every optimization.