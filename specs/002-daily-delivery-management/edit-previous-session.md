# Feature: Edit Previous Delivery Session & Token Sheet Return

---

## 1. Business Scenario

### The Problem

A customer has a token book (bag book token sheet). On Day 1:

1. Customer tells delivery partner: "No milk today"
2. Partner **forgets** and puts milk in the bag anyway
3. Partner collects the token sheet from the customer
4. Today's reconciliation works smoothly (token sheet registered)

On Day 2, the customer complains:

> "I said don't put milk yesterday, but you put milk in the bag. I want my token sheet back."

### What Needs to Happen

The **Owner** must be able to:

1. **Reopen** the previous day's closed route
2. **Edit** the delivery record: change from `DELIVERED` to `NOT_DELIVERED`
3. **Return** the token sheet to the customer's token book
4. **Recalculate** reconciliation for that day
5. **Close** the route again

The customer can then **reuse that same token sheet** in their next delivery session without needing to provide a new one.

---

## 2. Token Sheet Return Mechanism

### Important: Physical Token vs System Reference

**Physical Token Sheet (Customer Has):**
- Only has **sheet number** (1, 2, 3...)
- Does NOT have issue number
- Does NOT have book ID
- Customer only knows the sheet number

**System Reference (ERP Tracks):**
- Sheet number
- Issue number (internal reference)
- Book ID (database identifier)
- Status (ACTIVE, COMPLETED)

When customer says "Here's Sheet #5", the system must find which active book contains Sheet #5.

### How Token Sheets Work

Each customer has a **Token Book** with numbered sheets. Each sheet represents one unit of prepaid milk delivery.

```
Token Book Example:
├── Sheet #1 → Used on Jan 1
├── Sheet #2 → Used on Jan 2
├── Sheet #3 → Used on Jan 3 (THIS ONE NEEDS TO BE RETURNED)
├── Sheet #4 → Used on Jan 4
├── Sheet #5 → Not yet used
└── ...
```

### The `current_sheet` Field

The `token_book_issues` table has a `current_sheet` field that tracks how many sheets have been used:

```python
# token_book_issues table
current_sheet = Column(Integer, default=0)  # Number of sheets used
```

When a token sheet is registered during delivery:
- `current_sheet` is **incremented** by 1
- Example: If `current_sheet = 5`, it means 5 sheets have been used

### Token Sheet Return Logic

When a delivery is corrected from `DELIVERED` to `NOT_DELIVERED`:

1. **Remove the token registration** for that delivery
2. **Decrement `current_sheet`** on the token book issue by 1
3. This effectively "returns" the sheet to the customer

```
Before Correction:
  Token Book Issue: current_sheet = 5 (5 sheets used)
  Sheet #3 was registered on Day 1

After Correction:
  Token Book Issue: current_sheet = 4 (4 sheets used)
  Sheet #3 is now AVAILABLE for reuse
```

### Sheet Reuse

When the customer provides the same sheet (#3) in a future delivery:

1. Checker registers sheet #3
2. System validates: sheet number is valid, not already used
3. `current_sheet` is incremented back to 5
4. The sheet is consumed again

---

## 3. Database Changes

### New Table: `session_edits`

Tracks all edits to previous delivery sessions for audit purposes.

```sql
CREATE TABLE session_edits (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES delivery_sessions(id),
    delivery_id INTEGER NOT NULL REFERENCES daily_deliveries(id),
    edited_by INTEGER NOT NULL REFERENCES users(id),
    edit_type VARCHAR(30) NOT NULL,  -- DELIVERY_STATUS_CHANGE, TOKEN_RETURN, QUANTITY_CHANGE
    old_value JSONB NOT NULL,
    new_value JSONB NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Modified Table: `daily_deliveries`

Add fields to support token tracking:

```sql
ALTER TABLE daily_deliveries ADD COLUMN token_sheet_number INTEGER;
ALTER TABLE daily_deliveries ADD COLUMN token_book_issue_id INTEGER REFERENCES token_book_issues(id);
ALTER TABLE daily_deliveries ADD COLUMN is_edited BOOLEAN DEFAULT FALSE;
ALTER TABLE daily_deliveries ADD COLUMN last_edited_by INTEGER REFERENCES users(id);
ALTER TABLE daily_deliveries ADD COLUMN last_edited_at TIMESTAMP WITH TIME ZONE;
```

### Modified Table: `delivery_sessions`

Add field to track if session was reopened:

```sql
ALTER TABLE delivery_sessions ADD COLUMN reopened_by INTEGER REFERENCES users(id);
ALTER TABLE delivery_sessions ADD COLUMN reopened_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE delivery_sessions ADD COLUMN reopen_count INTEGER DEFAULT 0;
```

---

## 4. API Endpoints

### Reopen a Closed Session (Owner Only)

```
POST /deliveries/sessions/{session_id}/reopen
```

**Request Body:**
```json
{
    "reason": "Customer requested token sheet return for Day 1 delivery"
}
```

**Response:**
```json
{
    "session_id": 123,
    "status": "COMPLETED",
    "reopened_by": 1,
    "reopened_at": "2026-01-15T10:30:00Z",
    "message": "Session reopened. You can now edit delivery records."
}
```

**Business Rules:**
- Only Owner can reopen closed sessions
- Session status changes from `CLOSED` to `COMPLETED`
- Reopen count is incremented
- All edits are logged in `session_edits` table

### Edit a Delivery Record

```
PUT /deliveries/{delivery_id}/edit
```

**Request Body:**
```json
{
    "delivery_status": "NOT_DELIVERED",
    "return_token_sheet": true,
    "reason": "Customer said no milk, partner forgot and delivered anyway"
}
```

**Response:**
```json
{
    "delivery_id": 456,
    "old_status": "DELIVERED",
    "new_status": "NOT_DELIVERED",
    "token_sheet_returned": true,
    "token_book_issue_id": 789,
    "sheet_number": 3,
    "new_current_sheet": 4,
    "message": "Delivery corrected. Token sheet #3 returned to customer."
}
```

**Business Rules:**
- Session must be in `COMPLETED` status (reopened)
- Only Owner can edit previous sessions
- If `return_token_sheet = true`:
  - Token registration is removed
  - `current_sheet` on `token_book_issue` is decremented
  - Edit is logged in `session_edits`
- Reconciliation is recalculated automatically

### View Session Edit History

```
GET /deliveries/sessions/{session_id}/edit-history
```

**Response:**
```json
{
    "session_id": 123,
    "edits": [
        {
            "edit_id": 1,
            "delivery_id": 456,
            "customer_name": "Mrs. Sharma",
            "edit_type": "DELIVERY_STATUS_CHANGE",
            "old_value": {"status": "DELIVERED", "token_sheet": 3},
            "new_value": {"status": "NOT_DELIVERED", "token_sheet": null},
            "reason": "Customer said no milk, partner forgot",
            "edited_by": "Owner (Rajesh)",
            "edited_at": "2026-01-15T10:45:00Z"
        }
    ],
    "total_edits": 1
}
```

---

## 5. Business Rules

### Editing Rules

1. **Only Owner** can reopen closed sessions and edit previous deliveries
2. **Checker** can edit sessions that are still in `COMPLETED` status (same day, before closing)
3. **Delivery Partner** cannot edit any records
4. All edits must include a **reason** (mandatory field)
5. All edits are **permanently logged** in `session_edits` table
6. Original delivery records are **never deleted** (soft update with audit trail)

### Token Sheet Return Rules

1. Token sheet can only be returned if:
   - The delivery was originally `DELIVERED` with a token sheet registered
   - The token book issue is still `ACTIVE`
   - The sheet number is valid and was registered for that delivery

2. When a token sheet is returned:
   - `current_sheet` on `token_book_issue` is decremented by 1
   - The sheet becomes available for reuse
   - The customer can use the same sheet in future deliveries

3. Token sheet return does **not** affect:
   - Token book payment status
   - Token book issue status (remains ACTIVE)
   - Other customers' token sheets

### Reconciliation Rules

1. After editing a delivery, reconciliation is **automatically recalculated**
2. If the session was previously balanced, it may become unbalanced
3. Owner must **re-balance** and **close** the session again
4. The session status goes: `CLOSED` → `COMPLETED` (reopened) → `CLOSED` (reclosed)

### Audit Rules

1. Every edit creates an entry in `session_edits` table
2. Edit history cannot be deleted or modified
3. Reports include edit history for transparency
4. Owner can view all edits across all sessions

---

## 6. Complete Workflow Example

### Day 1: Normal Delivery (with mistake)

```
Morning Shift:
├── Customer: Mrs. Sharma (Route 1)
├── Subscription: 1L Full Cream Milk (Morning)
├── Token Book: #SM-001, Sheet #3
├── Partner delivers milk (FORGOT about "no milk" request)
├── Partner collects Sheet #3 from Mrs. Sharma
├── Checker registers: DELIVERED, Sheet #3
├── Token Book Issue: current_sheet = 5 → 6
├── Reconciliation: BALANCED
└── Route CLOSED
```

### Day 2: Customer Complaint

```
Mrs. Sharma calls Owner:
"I said no milk yesterday, but partner put milk in bag. 
 I want my token sheet back."

Owner action:
├── Reopens Day 1's session (reason: "Customer complaint")
├── Finds Mrs. Sharma's delivery record
├── Changes: DELIVERED → NOT_DELIVERED
├── Returns Token Sheet #3
├── Token Book Issue: current_sheet = 6 → 5
├── Reconciliation recalculated
├── Re-balances and closes session
└── Done!
```

### Day 3: Customer Uses Returned Sheet

```
Morning Shift:
├── Customer: Mrs. Sharma (Route 1)
├── Subscription: 1L Full Cream Milk (Morning)
├── Token Book: #SM-001, Sheet #3 (REUSED!)
├── Partner delivers milk
├── Partner collects Sheet #3 from Mrs. Sharma
├── Checker registers: DELIVERED, Sheet #3
├── Token Book Issue: current_sheet = 5 → 6
├── Reconciliation: BALANCED
└── Route CLOSED
```

---

## 7. UI/UX Requirements

### Session List View

- Show `CLOSED` sessions with "Reopen" button (Owner only)
- Show `COMPLETED` sessions with "Edit" button (Owner/Checker)
- Display edit count badge on sessions that have been edited

### Delivery Record Edit View

- Show original delivery details (read-only)
- Show editable fields:
  - Delivery Status (dropdown: DELIVERED, NOT_DELIVERED, CANCELLED)
  - Return Token Sheet (checkbox, only if status changes from DELIVERED)
  - Reason (text field, mandatory)
- Show token book information (read-only)
- Show current `current_sheet` value

### Confirmation Dialog

Before saving edits, show confirmation:

```
⚠️ Confirm Edit

You are about to make the following changes:

Customer: Mrs. Sharma
Date: January 14, 2026
Shift: Morning

Change: DELIVERED → NOT_DELIVERED
Return Token Sheet: Yes (Sheet #3)

This action will:
• Update the delivery record
• Return Sheet #3 to the customer's token book
• Recalculate reconciliation for this session

Reason: Customer said no milk, partner forgot

[Cancel] [Confirm Edit]
```

---

## 8. Technical Implementation Notes

### Service Layer Pattern

Follow existing patterns in `app/services/`:

```python
# app/services/delivery_edit_service.py

def reopen_delivery_session(
    db: Session, 
    session_id: int, 
    owner_id: int, 
    reason: str
) -> dict:
    """
    Reopen a closed delivery session for editing.
    Only Owner can perform this action.
    """
    pass

def edit_delivery_record(
    db: Session,
    delivery_id: int,
    editor_id: int,
    new_status: str,
    return_token_sheet: bool,
    reason: str
) -> dict:
    """
    Edit a delivery record and optionally return token sheet.
    """
    pass

def return_token_sheet(
    db: Session,
    delivery_id: int,
    editor_id: int,
    reason: str
) -> dict:
    """
    Return a token sheet to customer's token book.
    Decrements current_sheet on token_book_issue.
    """
    pass

def get_session_edit_history(
    db: Session,
    session_id: int
) -> list:
    """
    Get all edits for a delivery session.
    """
    pass
```

### Exception Handling

Follow existing pattern in `app/exceptions/`:

```python
# app/exceptions/delivery_edit.py

class SessionNotClosedError(Exception):
    """Session must be CLOSED to reopen"""
    pass

class OwnerRequiredError(Exception):
    """Only Owner can edit previous sessions"""
    pass

class TokenSheetReturnError(Exception):
    """Cannot return token sheet"""
    pass

class DeliveryNotDeliveredError(Exception):
    """Can only return tokens for DELIVERED records"""
    pass

class TokenBookNotActiveError(Exception):
    """Token book issue must be ACTIVE to return sheets"""
    pass
```

### Schema Pattern

Follow existing pattern in `app/schemas/`:

```python
# app/schemas/delivery_edit.py

class ReopenSessionRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)

class EditDeliveryRequest(BaseModel):
    delivery_status: str = Field(..., pattern="^(DELIVERED|NOT_DELIVERED|CANCELLED)$")
    return_token_sheet: bool = False
    reason: str = Field(..., min_length=5, max_length=500)

class SessionEditHistoryResponse(BaseModel):
    session_id: int
    edits: list[EditHistoryItem]
    total_edits: int

class EditHistoryItem(BaseModel):
    edit_id: int
    delivery_id: int
    customer_name: str
    edit_type: str
    old_value: dict
    new_value: dict
    reason: str
    edited_by: str
    edited_at: datetime
```

---

## 9. Testing Requirements

### Unit Tests

1. Test `reopen_delivery_session` - success case
2. Test `reopen_delivery_session` - session not CLOSED error
3. Test `reopen_delivery_session` - non-owner error
4. Test `edit_delivery_record` - status change only
5. Test `edit_delivery_record` - status change with token return
6. Test `return_token_sheet` - success case
7. Test `return_token_sheet` - token book not active error
8. Test `return_token_sheet` - delivery not DELIVERED error
9. Test `get_session_edit_history` - returns correct edits
10. Test reconciliation recalculation after edit

### Integration Tests

1. Full workflow: Close session → Reopen → Edit → Re-close
2. Token sheet return → Future delivery with same sheet
3. Multiple edits on same session
4. Edit history tracking across sessions

---

## 10. Migration Plan

### Phase 1: Database Changes

1. Create `session_edits` table
2. Add new columns to `daily_deliveries`
3. Add new columns to `delivery_sessions`
4. Create Alembic migration

### Phase 2: Service Layer

1. Create `delivery_edit_service.py`
2. Implement `reopen_delivery_session`
3. Implement `edit_delivery_record`
4. Implement `return_token_sheet`
5. Implement `get_session_edit_history`

### Phase 3: API Layer

1. Create `delivery_edit_router.py`
2. Add endpoints for reopen, edit, history
3. Add proper authentication and authorization

### Phase 4: Testing

1. Write unit tests
2. Write integration tests
3. Test with seed data

---

## 11. Summary

This feature enables the Owner to correct mistakes from previous delivery sessions by:

1. **Reopening** closed sessions
2. **Editing** delivery records (status, quantities)
3. **Returning** token sheets to customer's token book
4. **Tracking** all edits in an audit log
5. **Recalculating** reconciliation automatically

The token sheet return mechanism works by decrementing `current_sheet` on the `token_book_issue`, allowing customers to reuse the same sheet in future deliveries.

All edits are permanently logged for transparency and audit purposes.
