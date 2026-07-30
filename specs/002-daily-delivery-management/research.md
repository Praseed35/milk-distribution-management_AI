# Research: Daily Delivery Management

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Overview

This document captures technical research and design decisions for implementing the Daily Delivery Management feature.

---

## Decision 1: Delivery Session State Machine

**Decision**: Use explicit state transitions with validation

**Rationale**: The delivery session has a clear lifecycle (PLANNED→STARTED→COMPLETED→CLOSED) with specific rules for each transition. Explicit state machine prevents invalid transitions and makes business rules enforceable.

**Alternatives Considered**:
- Status field without validation: Rejected - allows invalid transitions
- Event sourcing: Rejected - overkill for this use case

**Implementation**:
```python
# Valid transitions
VALID_TRANSITIONS = {
    "PLANNED": ["STARTED"],
    "STARTED": ["COMPLETED"],
    "COMPLETED": ["CLOSED", "PLANNED"],  # PLANNED for reopen
    "CLOSED": ["COMPLETED"]  # Reopen
}
```

---

## Decision 2: Reconciliation Calculation Strategy

**Decision**: Calculate on-demand, not stored

**Rationale**: Reconciliation is a simple formula (Loaded = Token + Cash + Returned). Calculating on-demand ensures consistency and avoids stale data. The formula is fast enough for real-time calculation.

**Alternatives Considered**:
- Stored reconciliation values: Rejected - requires update on every change
- Event-driven updates: Rejected - complexity not justified

**Implementation**:
```python
def calculate_reconciliation(session_id):
    loaded = get_dispatch_quantity(session_id)
    token = sum(delivery.quantity for delivery in get_token_deliveries(session_id))
    cash = sum(delivery.quantity for delivery in get_cash_deliveries(session_id))
    returned = get_returned_milk(session_id)
    
    total = token + cash + returned
    is_balanced = (loaded == total)
    difference = loaded - total
    
    return {
        "loaded": loaded,
        "token_registered": token,
        "cash_sales": cash,
        "returned_milk": returned,
        "total_accounted": total,
        "difference": difference,
        "is_balanced": is_balanced
    }
```

---

## Decision 3: Optimistic Locking Implementation

**Decision**: Use version column for conflict detection

**Rationale**: Optimistic locking is sufficient for this use case (low concurrency, short transactions). Pessimistic locking would cause unnecessary blocking.

**Alternatives Considered**:
- Pessimistic locking: Rejected - causes blocking, not needed
- Last-write-wins without detection: Rejected - data loss risk

**Implementation**:
```python
# In delivery_session model
version = Column(Integer, default=1, nullable=False)

# In service layer
def update_delivery(db, delivery_id, updates, expected_version):
    delivery = db.query(DailyDelivery).filter(DailyDelivery.id == delivery_id).first()
    
    if delivery.version != expected_version:
        raise ConcurrentEditError("Session was modified by another user. Please reload and try again.")
    
    for key, value in updates.items():
        setattr(delivery, key, value)
    
    delivery.version += 1
    db.commit()
```

---

## Decision 4: Token Sheet Validation Logic

**Decision**: Multi-step validation with warnings

**Rationale**: Token registration requires validating customer, book, sheet number, and sequence. Some validations are hard errors (invalid book), others are warnings (non-sequential).

**Alternatives Considered**:
- Simple validation: Rejected - doesn't handle real-world edge cases
- Strict sequential only: Rejected - prevents legitimate transactions

**Validation Steps**:
1. Customer exists and is active → ERROR if not
2. Milk type matches delivery → ERROR if not
3. Active token book exists → ERROR if not
4. Sheet number within book range → ERROR if not
5. Sheet not already used → ERROR if duplicate
6. Sheet sequence check → WARNING if non-sequential
7. New book usage check → WARNING if old book has remaining sheets

---

## Decision 5: Audit Trail Strategy

**Decision**: Separate audit tables for each entity type

**Rationale**: Audit trails need to be immutable and comprehensive. Separate tables keep audit data isolated and make queries efficient.

**Alternatives Considered**:
- JSON audit log: Rejected - harder to query
- Column-level tracking: Rejected - complex, mixes concerns

**Implementation**:
```python
# session_edits table
class SessionEdit(Base):
    __tablename__ = "session_edits"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("delivery_sessions.id"))
    delivery_id = Column(Integer, ForeignKey("daily_deliveries.id"))
    edited_by = Column(Integer, ForeignKey("users.id"))
    edit_type = Column(String(30))  # STATUS_CHANGE, TOKEN_RETURN, QUANTITY_CHANGE
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# token_sheet_warnings table
class TokenSheetWarning(Base):
    __tablename__ = "token_sheet_warnings"
    
    id = Column(Integer, primary_key=True)
    delivery_id = Column(Integer, ForeignKey("daily_deliveries.id"))
    warning_code = Column(String(30))
    warning_message = Column(Text)
    sheet_number = Column(Integer)
    book_issue_id = Column(Integer, ForeignKey("token_book_issues.id"))
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Decision 6: Report Generation Strategy

**Decision**: Generate on-demand after route closure

**Rationale**: Reports are derived data that can be computed from delivery records. Generating on-demand ensures consistency and avoids storage overhead.

**Alternatives Considered**:
- Pre-generated reports: Rejected - storage overhead, staleness risk
- Real-time reports: Rejected - performance impact during operations

**Report Types**:
1. Delivery Report - All deliveries for the session
2. Route Summary - High-level metrics
3. Token Collection Report - All tokens registered
4. Pending Token Report - Tokens not yet received
5. Cash Sales Report - Cash transactions
6. Returned Milk Report - Undelivered milk
7. Daily Reconciliation Report - Balance sheet
8. Session Edit History - All edits made

---

## Decision 7: API Endpoint Organization

**Decision**: Separate routers for deliveries and delivery edits

**Rationale**: Delivery operations (registration, reconciliation) are different from edit operations (reopen, edit previous). Separating concerns makes the API clearer and easier to maintain.

**Endpoint Structure**:
```
/deliveries/
├── /sessions/
│   ├── POST /                    # Create session
│   ├── GET /                     # List sessions
│   ├── GET /{id}                 # Session detail
│   ├── POST /{id}/start          # Start session
│   ├── POST /{id}/dispatch       # Record dispatch
│   ├── POST /{id}/close          # Close session
│   └── POST /{id}/reopen         # Reopen session (Owner)
├── /sessions/{id}/checklist      # Get delivery checklist
├── /sessions/{id}/reconciliation # Get reconciliation
├── /sessions/{id}/report         # Get session report
├── /                             # Record delivery
├── /unplanned                    # Add unplanned delivery
└── /{id}/edit                    # Edit previous delivery
```

---

## Decision 8: Error Handling Strategy

**Decision**: Domain-specific exceptions with appropriate HTTP status codes

**Rationale**: Each domain has specific error conditions. Custom exceptions make error handling clear and provide meaningful messages to clients.

**Exception Types**:
```python
# Delivery exceptions
class SessionNotFoundError(Exception): pass  # 404
class SessionAlreadyClosedError(Exception): pass  # 400
class SessionNotBalancedError(Exception): pass  # 400
class DispatchAlreadyRecordedError(Exception): pass  # 400

# Edit exceptions
class OwnerRequiredError(Exception): pass  # 403
class ConcurrentEditError(Exception): pass  # 409
class TokenSheetReturnError(Exception): pass  # 400

# Validation exceptions
class InvalidTokenSheetError(Exception): pass  # 400
class TokenBookNotActiveError(Exception): pass  # 400
class SheetAlreadyUsedError(Exception): pass  # 400
```

---

## Summary

All technical decisions follow established project patterns and align with the constitution. No NEEDS CLARIFICATION items remain. The design is ready for implementation.
