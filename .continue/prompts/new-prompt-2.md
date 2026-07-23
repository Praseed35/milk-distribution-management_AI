---
name: Fix Bug
description: Analyze and fix bugs without breaking existing functionality
invokable: true
---

You are debugging a production FastAPI backend.

Before making changes:

1. Read all related files.
2. Understand the existing implementation.
3. Identify the root cause.
4. Do not implement temporary fixes.

Debugging workflow:

- Reproduce the issue.
- Identify the root cause.
- Explain the cause.
- Implement the smallest correct fix.
- Verify no existing functionality breaks.

When fixing:

- Preserve architecture.
- Preserve business rules.
- Preserve API contracts.
- Preserve database consistency.

Before finishing:

- Verify imports.
- Verify typing.
- Verify transactions.
- Verify tests.
- Explain the root cause and solution.---
name: New prompt
description: New prompt
invokable: true
---

Please write a thorough suite of unit tests for this code, making sure to cover all relevant edge cases