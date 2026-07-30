# Feature: Token Sheet Edge Cases & Warning System

---

## 1. Overview

This specification covers real-world token sheet scenarios that require special handling and warning notifications to the Checker during registration.

**Key Scenarios:**
1. Customer changes mind (unplanned delivery with token)
2. Non-sequential token sheets
3. New book issued before old one finishes

---

## 2. Important: Physical Token vs System Reference

### Physical Token Sheet (What Customer Has)

The physical token sheet that customers hold has:
- **Sheet Number**: 1, 2, 3, 4, 5... (printed on the sheet)
- **NO Issue Number**: Issue numbers are NOT printed on physical sheets
- **NO Book ID**: Customers don't know which book batch their sheet is from

**Example Physical Token Sheet:**
```
╔═══════════════════════════════════════════════════╗
║           RAJESH MILK DISTRIBUTION                ║
║                                                   ║
║     Token Sheet Number: 5                         ║
║                                                   ║
║     Milk Type: Full Cream (1000ml)                ║
║                                                   ║
║     Customer: Mrs. Sharma                         ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

**Note:** Only the sheet number (5) is visible. No issue number.

### System Reference (What ERP Tracks)

The ERP system tracks:
- **Issue Number**: Internal reference (Issue #1, Issue #2, Issue #3...)
- **Book ID**: Database identifier
- **Sheet Range**: Which sheets belong to which book
- **Status**: ACTIVE, COMPLETED, etc.

**Example System Record:**
```
Token Book Issues for Mrs. Sharma (Full Cream):
═══════════════════════════════════════════════════
│ Issue # │ Book ID │ Sheets    │ Used │ Status  │
├─────────┼─────────┼───────────┼──────┼─────────┤
│ 1       │ 456     │ 1-30      │ 30   │ COMPLETED│
│ 2       │ 457     │ 1-30      │ 20   │ ACTIVE  │
│ 3       │ 458     │ 1-30      │ 0    │ ACTIVE  │
═══════════════════════════════════════════════════
```

### How Registration Works

When customer provides Sheet #5:

1. **Customer says:** "Here's Sheet #5"
2. **Checker enters:** Sheet number 5
3. **System finds:** Which active book contains Sheet #5
4. **System validates:** Is Sheet #5 available in that book?
5. **System registers:** Links to correct book issue

**System Logic:**
```python
def find_book_for_sheet(customer_id, milk_type_id, sheet_number):
    """
    Find which active book contains the given sheet number.
    """
    # Get all active books for this customer + milk type
    active_books = get_active_books(customer_id, milk_type_id)
    
    for book in active_books:
        # Check if this sheet number belongs to this book
        # Each book has sheets 1-30 (or configured range)
        if 1 <= sheet_number <= 30:  # Assuming 30 sheets per book
            return book  # Return the active book
    
    return None  # No active book found
```

### Key Points

| Aspect | Physical Token | System Reference |
|--------|----------------|------------------|
| Sheet Number | ✅ Visible to customer | ✅ Stored in database |
| Issue Number | ❌ NOT visible | ✅ Internal reference |
| Book ID | ❌ NOT visible | ✅ Database identifier |
| Customer Knows | Only sheet number | N/A |
| System Tracks | Sheet number + book | Complete hierarchy |

---

## 3. Scenario 1: Customer Changes Mind (Unplanned with Token)

### Business Situation

A customer was marked as "NOT_DELIVERED" or had a delivery exception (VACATION, NO_MILK) for today. During the delivery route, the customer changes their mind and wants milk. They provide a token sheet.

**Example:**
```
Morning Planning:
├── Mrs. Gupta marked as VACATION (no delivery planned)
└── System skipped her from today's list

During Delivery (7:00 AM):
├── Suresh passes Mrs. Gupta's house
├── Mrs. Gupta calls out: "Wait! I changed my mind, I want milk today!"
├── Mrs. Gupta provides Token Sheet #5
├── Suresh delivers 1L Full Cream Milk
└── Suresh marks: UNPLANNED DELIVERY with TOKEN
```

### System Behavior

**During Registration:**
```
Priya (Checker) selects: ADD UNPLANNED DELIVERY

Customer Search:
├── Search by: "Gupta"
├── Found: Mrs. Gupta (Customer ID: C00005)
├── Note: She was on VACATION today

Registration Details:
├── Customer: Mrs. Gupta
├── Milk Type: Full Cream 1L
├── Quantity: 1L
├── Source: UNPLANNED
├── Registration Method: TOKEN SHEET
├── Token Sheet: #5
├── Reason: "Customer changed mind, was on vacation"
└── Status: DELIVERED
```

**System Actions:**
1. Create unplanned delivery record
2. Register Token Sheet #5
3. Increment `current_sheet` on Mrs. Gupta's token book issue
4. Include in reconciliation as "Token Milk"
5. Log the unplanned delivery with reason

### API Endpoint

```
POST /deliveries/unplanned
```

**Request Body:**
```json
{
    "session_id": 123,
    "customer_id": 5,
    "milk_type_id": 1,
    "quantity": 1,
    "registration_method": "TOKEN_SHEET",
    "token_sheet_number": 5,
    "reason": "Customer changed mind, was on vacation"
}
```

**Response:**
```json
{
    "delivery_id": 789,
    "customer_name": "Mrs. Gupta",
    "status": "DELIVERED",
    "source": "UNPLANNED",
    "token_sheet_registered": true,
    "token_book_issue_id": 456,
    "new_current_sheet": 8,
    "message": "Unplanned delivery recorded. Token Sheet #5 registered."
}
```

---

## 4. Scenario 2: Non-Sequential Token Sheets

### Business Situation

Customers don't always provide token sheets in order. They might:
- Skip sheets and come back later
- Give sheets out of order
- Lose a sheet and continue with the next

**Example:**
```
Token Book for Mrs. Sharma (30 sheets):
├── Sheet #1 → Used Jan 1 ✓
├── Sheet #2 → Used Jan 2 ✓
├── Sheet #3 → Used Jan 3 ✓
├── Sheet #4 → Used Jan 4 ✓
├── Sheet #5 → Used Jan 5 ✓
├── Sheet #6 → Used Jan 6 ✓
├── Sheet #7 → LOST (customer lost it)
├── Sheet #8 → Used Jan 8 ✓ (skipped 7)
├── Sheet #9 → Used Jan 9 ✓
├── Sheet #10 → Used Jan 10 ✓
└── ...
```

### Warning System

When a non-sequential sheet is registered, the system shows a **WARNING** to the Checker.

**Warning Types:**

| Warning Code | Description | Severity |
|--------------|-------------|----------|
| `NON_SEQUENTIAL_SHEET` | Sheet number skips ahead | ⚠️ WARNING |
| `GAP_DETECTED` | Gap in sheet sequence | ℹ️ INFO |
| `SHEET_ALREADY_USED` | Duplicate registration attempt | 🚫 ERROR |
| `SHEET_OUT_OF_ORDER` | Sheet provided after higher numbers used | ⚠️ WARNING |

### Registration Flow with Warnings

**Scenario: Customer provides Sheet #8 when #7 is not used**

```
Priya registers Sheet #8 for Mrs. Sharma

System Validation:
├── Customer exists ✓
├── Token number valid ✓
├── Milk type matches ✓
├── Active token book exists ✓
├── Sheet not already used ✓
├── Previous book completed ✓
└── ⚠️ SEQUENCE CHECK: Sheet #7 not yet used

WARNING DISPLAYED:
═══════════════════════════════════════════════════
⚠️ WARNING: Non-sequential Sheet

Customer: Mrs. Sharma
Sheet Being Registered: #8
Last Used Sheet: #6
Sheets Not Yet Used: #7

This means:
• Sheet #7 was not used yet
• Customer is providing #8 before #7

Possible reasons:
• Customer lost Sheet #7
• Customer is providing from different book
• Customer made a mistake

Do you want to proceed?
═══════════════════════════════════════════════════
[Cancel] [Proceed with Registration]
```

**Checker Decision:**
- If Checker clicks "Proceed" → Sheet #8 is registered
- If Checker clicks "Cancel" → Registration cancelled

### Later: Customer provides Sheet #7

```
Priya registers Sheet #7 for Mrs. Sharma

System Validation:
├── Customer exists ✓
├── Token number valid ✓
├── Milk type matches ✓
├── Active token book exists ✓
├── Sheet not already used ✓
├── Previous book completed ✓
└── ⚠️ SEQUENCE CHECK: Sheet #8 already used

WARNING DISPLAYED:
═══════════════════════════════════════════════════
⚠️ WARNING: Out-of-order Sheet

Customer: Mrs. Sharma
Sheet Being Registered: #7
Sheets Already Used: #8, #9, #10

This means:
• Higher-numbered sheets were already used
• Customer is now providing a lower number

This is unusual but allowed.
Do you want to proceed?
═══════════════════════════════════════════════════
[Cancel] [Proceed with Registration]
```

### Database Changes

Add tracking for sheet sequence:

```sql
-- Add to daily_deliveries table
ALTER TABLE daily_deliveries ADD COLUMN sheet_sequence_status VARCHAR(20);
-- Values: SEQUENTIAL, NON_SEQUENTIAL, GAP, OUT_OF_ORDER

-- Add new table for sheet warnings
CREATE TABLE token_sheet_warnings (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES daily_deliveries(id),
    warning_code VARCHAR(30) NOT NULL,
    warning_message TEXT NOT NULL,
    sheet_number INTEGER NOT NULL,
    expected_sheet INTEGER,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Service Logic

```python
def validate_sheet_sequence(
    db: Session,
    customer_id: int,
    milk_type_id: int,
    sheet_number: int,
    token_book_issue_id: int
) -> dict:
    """
    Validate sheet sequence and return warnings if non-sequential.
    """
    
    # Get all registered sheets for this book issue
    registered_sheets = (
        db.query(DailyDelivery.token_sheet_number)
        .filter(
            DailyDelivery.token_book_issue_id == token_book_issue_id,
            DailyDelivery.delivery_status == "DELIVERED",
            DailyDelivery.token_sheet_number.isnot(None)
        )
        .order_by(DailyDelivery.token_sheet_number)
        .all()
    )
    
    registered_numbers = [s[0] for s in registered_sheets]
    
    # Check for warnings
    warnings = []
    
    if not registered_numbers:
        # First sheet in this book
        return {"warnings": [], "is_first_sheet": True}
    
    max_registered = max(registered_numbers)
    min_registered = min(registered_numbers)
    
    # Check if sheet is non-sequential
    if sheet_number > max_registered + 1:
        warnings.append({
            "code": "NON_SEQUENTIAL_SHEET",
            "message": f"Sheet #{sheet_number} skips ahead. "
                      f"Last used sheet was #{max_registered}. "
                      f"Sheets #{max_registered + 1} to #{sheet_number - 1} not yet used.",
            "severity": "WARNING",
            "expected_sheet": max_registered + 1
        })
    
    # Check if sheet is out of order (lower than already used)
    if sheet_number < max_registered:
        warnings.append({
            "code": "SHEET_OUT_OF_ORDER",
            "message": f"Sheet #{sheet_number} is lower than already used sheets "
                      f"(#{', #'.join(map(str, sorted(registered_numbers)))}). "
                      f"This is unusual but allowed.",
            "severity": "WARNING",
            "expected_sheet": max_registered + 1
        })
    
    # Check for gaps
    if len(registered_numbers) > 0:
        expected_sheets = set(range(min_registered, max_registered + 1))
        used_sheets = set(registered_numbers)
        missing_sheets = expected_sheets - used_sheets
        
        if missing_sheets and sheet_number not in missing_sheets:
            warnings.append({
                "code": "GAP_DETECTED",
                "message": f"Sheets not yet used: #{', #'.join(map(str, sorted(missing_sheets)))}. "
                          f"Consider collecting these before proceeding.",
                "severity": "INFO"
            })
    
    return {
        "warnings": warnings,
        "registered_count": len(registered_numbers),
        "max_registered": max_registered
    }
```

---

## 5. Scenario 3: New Book Before Old One Finishes

### Business Situation

Sometimes a new token book is issued before the old one is fully used. This can happen when:
- Customer requests a new book (maybe lost old one)
- Owner issues replacement book
- Customer switches to different milk type

**Example:**
```
Token Book #SM-001 (Old Book):
├── Issue Date: Jan 1
├── Total Sheets: 30
├── Sheets Used: 20 (current_sheet = 20)
├── Sheets Remaining: 10
└── Status: ACTIVE

Token Book #SM-002 (New Book):
├── Issue Date: Jan 15
├── Total Sheets: 30
├── Sheets Used: 0
└── Status: ACTIVE

Customer provides Sheet #5 from NEW BOOK (#SM-002)
System detects: Old book still has 10 unused sheets!
```

### Warning System

When a sheet from a new book is registered while the old book is still active, the system shows a **WARNING** to the Checker.

**Warning Displayed:**
```
═══════════════════════════════════════════════════
⚠️ WARNING: New Book Used Before Old Book Finished

Customer: Mrs. Sharma
Sheet Being Registered: #5 (from NEW Book #SM-002)

Old Book Status:
├── Book: #SM-001
├── Issued: Jan 1
├── Sheets Used: 20/30
├── Sheets Remaining: 10
└── Status: ACTIVE

New Book Status:
├── Book: #SM-002
├── Issued: Jan 15
├── Sheets Used: 0/30
└── Status: ACTIVE

This means:
• Customer has 10 unused sheets in old book
• Customer is now using new book

Possible reasons:
• Customer lost old book
• Owner issued replacement
• Customer switching books

Do you want to proceed?
═══════════════════════════════════════════════════
[Cancel] [Proceed with Registration]
```

### Database Changes

Add tracking for book transitions:

```sql
-- Add to daily_deliveries table
ALTER TABLE daily_deliveries ADD COLUMN is_new_book_usage BOOLEAN DEFAULT FALSE;
ALTER TABLE daily_deliveries ADD COLUMN old_book_issue_id INTEGER REFERENCES token_book_issues(id);

-- Add new table for book transition warnings
CREATE TABLE book_transition_warnings (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES daily_deliveries(id),
    new_book_issue_id INTEGER NOT NULL REFERENCES token_book_issues(id),
    old_book_issue_id INTEGER NOT NULL REFERENCES token_book_issues(id),
    old_book_remaining_sheets INTEGER NOT NULL,
    warning_message TEXT NOT NULL,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Service Logic

```python
def validate_book_usage(
    db: Session,
    customer_id: int,
    milk_type_id: int,
    token_book_issue_id: int
) -> dict:
    """
    Validate if customer is using new book before old one finishes.
    """
    
    # Get all active book issues for this customer + milk type
    active_books = (
        db.query(TokenBookIssue)
        .join(TokenIdentity)
        .filter(
            TokenIdentity.customer_id == customer_id,
            TokenIdentity.milk_type_id == milk_type_id,
            TokenBookIssue.status == "ACTIVE",
            TokenBookIssue.is_active == True
        )
        .order_by(TokenBookIssue.issue_date)
        .all()
    )
    
    if len(active_books) <= 1:
        # Only one active book, no warning needed
        return {"warnings": [], "is_new_book": False}
    
    # Find the book being used
    current_book = None
    old_books = []
    
    for book in active_books:
        if book.id == token_book_issue_id:
            current_book = book
        else:
            old_books.append(book)
    
    if not current_book:
        return {"warnings": [], "is_new_book": False}
    
    # Check if there are older books with remaining sheets
    warnings = []
    
    for old_book in old_books:
        # Calculate remaining sheets (assuming 30 sheets per book)
        # In reality, you'd store total_sheets in the book issue
        total_sheets = 30  # This should come from book configuration
        remaining = total_sheets - old_book.current_sheet
        
        if remaining > 0:
            warnings.append({
                "code": "NEW_BOOK_BEFORE_OLD_FINISHED",
                "message": f"New book #{current_book.id} is being used, "
                          f"but old book #{old_book.id} still has "
                          f"{remaining} unused sheets.",
                "severity": "WARNING",
                "old_book_id": old_book.id,
                "old_book_remaining": remaining,
                "old_book_used": old_book.current_sheet,
                "old_book_total": total_sheets
            })
    
    return {
        "warnings": warnings,
        "is_new_book": True,
        "current_book": current_book,
        "old_books": old_books
    }
```

---

## 6. Combined Warning System

### Warning Display UI

When registering a token sheet, the system checks for ALL warnings and displays them together:

```
═══════════════════════════════════════════════════
⚠️ TOKEN REGISTRATION WARNINGS

Customer: Mrs. Sharma
Sheet Being Registered: #5
Book: #SM-002 (NEW)

WARNING 1: New Book Usage
├── Old book #SM-001 still has 10 unused sheets
├── Customer is now using new book #SM-002
└── Reason may be: Lost book, replacement, switch

WARNING 2: Non-sequential Sheet
├── Last sheet used from this book: #3
├── Sheet #4 not yet used
└── Customer is providing #5 before #4

Do you want to proceed?
═══════════════════════════════════════════════════
[Cancel] [Proceed with Warnings] [View Book Details]
```

### Warning Storage

All warnings are stored for audit purposes:

```sql
-- Token sheet warnings table
CREATE TABLE token_sheet_warnings (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES daily_deliveries(id),
    warning_code VARCHAR(30) NOT NULL,
    warning_message TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL,  -- INFO, WARNING, ERROR
    sheet_number INTEGER,
    book_issue_id INTEGER,
    metadata JSONB,  -- Additional warning details
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Warning Codes Reference

| Code | Description | Severity | Action |
|------|-------------|----------|--------|
| `NON_SEQUENTIAL_SHEET` | Sheet skips ahead in sequence | WARNING | Checker acknowledges |
| `SHEET_OUT_OF_ORDER` | Sheet provided after higher numbers used | WARNING | Checker acknowledges |
| `GAP_DETECTED` | Gap in sheet sequence | INFO | Information only |
| `SHEET_ALREADY_USED` | Duplicate registration attempt | ERROR | Cannot proceed |
| `NEW_BOOK_BEFORE_OLD_FINISHED` | New book used while old still active | WARNING | Checker acknowledges |
| `BOOK_EXPIRED` | Old book past expiration date | INFO | Information only |
| `SHEET_EXCEEDS_BOOK_SIZE` | Sheet number exceeds book total | ERROR | Cannot proceed |

---

## 7. Complete Workflow Examples

### Example 1: Customer Changes Mind with Token

```
Time: 7:00 AM (During Delivery)
═══════════════════════════════════════════════════

Suresh (Partner) arrives at Mrs. Gupta's house.
Mrs. Gupta was marked as VACATION today.

Mrs. Gupta: "Wait! I changed my mind. I want milk today!"
Mrs. Gupta provides: Token Sheet #5

Suresh: "OK, I'll add you as unplanned delivery."
Suresh delivers: 1L Full Cream Milk

Time: 9:30 AM (Registration)
═══════════════════════════════════════════════════

Priya (Checker) opens ERP:
├── Sees Mrs. Gupta was on VACATION
├── Sees UNPLANNED DELIVERY added by Suresh
├── Clicks: "Register Token"

Priya enters:
├── Customer: Mrs. Gupta
├── Token Sheet: #5
├── Reason: "Customer changed mind"

System validates:
├── Customer exists ✓
├── Token number valid ✓
├── Milk type matches ✓
├── Active token book exists ✓
├── Sheet not already used ✓
├── Sequence check: #4 not yet used → ⚠️ WARNING

Warning displayed:
"Sheet #5 skips ahead. Sheet #4 not yet used."

Priya clicks: "Proceed with Registration"

System registers:
├── Token Sheet #5 registered
├── current_sheet: 7 → 8
├── Delivery marked as DELIVERED
├── Unplanned delivery logged
└── Included in reconciliation

Time: 10:00 AM (Reconciliation)
═══════════════════════════════════════════════════

Reconciliation:
├── Token Milk: 4L (including Mrs. Gupta's unplanned)
├── Cash Sales: 2L
├── Returned Milk: 1L
├── Total: 7L
├── Loaded: 7L
└── Status: BALANCED ✓
```

### Example 2: Non-sequential Sheets Over Multiple Days

```
Day 1 (Jan 1):
├── Mrs. Sharma provides Sheet #1
├── Registered ✓
├── current_sheet: 0 → 1
└── No warnings (first sheet)

Day 2 (Jan 2):
├── Mrs. Sharma provides Sheet #2
├── Registered ✓
├── current_sheet: 1 → 2
└── No warnings (sequential)

Day 3 (Jan 3):
├── Mrs. Sharma provides Sheet #3
├── Registered ✓
├── current_sheet: 2 → 3
└── No warnings (sequential)

Day 4 (Jan 4):
├── Mrs. Sharma provides Sheet #5 (skipped #4!)
├── WARNING: "Sheet #5 skips ahead. #4 not yet used."
├── Checker proceeds
├── Registered ✓
├── current_sheet: 3 → 4
└── Warning logged

Day 5 (Jan 5):
├── Mrs. Sharma provides Sheet #4 (out of order!)
├── WARNING: "Sheet #4 is lower than already used sheets (#5)."
├── Checker proceeds
├── Registered ✓
├── current_sheet: 4 → 5
└── Warning logged

Day 6 (Jan 6):
├── Mrs. Sharma provides Sheet #6
├── Registered ✓
├── current_sheet: 5 → 6
└── No warnings (sequential from #5)
```

### Example 3: New Book Before Old Finishes

```
Token History:
═══════════════════════════════════════════════════

Book #SM-001 (Issued Jan 1):
├── 30 sheets total
├── Used: 20 sheets (current_sheet = 20)
├── Remaining: 10 sheets
└── Status: ACTIVE

Book #SM-002 (Issued Jan 15):
├── 30 sheets total
├── Used: 0 sheets
└── Status: ACTIVE

Day 15 (Jan 15):
═══════════════════════════════════════════════════

Mrs. Sharma provides Sheet #1 from NEW Book #SM-002

System Validation:
├── Customer exists ✓
├── Token number valid ✓
├── Milk type matches ✓
├── Active token book exists ✓
├── Sheet not already used ✓
├── ⚠️ NEW BOOK WARNING: Old book #SM-001 still has 10 sheets
└── No sequence warning (first sheet in new book)

Warning displayed:
"New book #SM-002 is being used, but old book #SM-001 
still has 10 unused sheets."

Checker clicks: "Proceed with Registration"

System registers:
├── Token Sheet #1 registered (from Book #SM-002)
├── Book #SM-002 current_sheet: 0 → 1
├── Book #SM-001 unchanged (still has 10 sheets)
├── Warning logged
└── Both books remain ACTIVE

Day 16 (Jan 16):
═══════════════════════════════════════════════════

Mrs. Sharma provides Sheet #2 from NEW Book #SM-002

System Validation:
├── All checks pass ✓
├── ⚠️ NEW BOOK WARNING: Old book still has 10 sheets
└── No sequence warning (sequential in new book)

Checker proceeds, registration successful
```

---

## 8. Business Rules

### Unplanned Delivery Rules

1. Unplanned deliveries can be added for **existing customers only**
2. If customer doesn't exist, Checker must create them first
3. Unplanned deliveries require a **reason** (mandatory)
4. Unplanned deliveries are **included in reconciliation**
5. Unplanned deliveries are **marked with source = UNPLANNED**
6. Original delivery schedule is **never modified**

### Non-sequential Sheet Rules

1. Non-sequential sheets are **allowed** (not blocked)
2. System shows **WARNING** for non-sequential sheets
3. Checker must **acknowledge** the warning before proceeding
4. All warnings are **logged for audit**
5. Checker has **final decision** on whether to accept
6. System does **not prevent** registration based on sequence

### New Book Rules

1. Multiple books can be **ACTIVE** simultaneously
2. System shows **WARNING** when new book used before old finishes
3. Checker must **acknowledge** the warning
4. Both books remain **ACTIVE** until explicitly completed
5. Old book can still be used after new book starts
6. System tracks **which book** each sheet came from

---

## 9. API Endpoints

### Validate Token Sheet (Before Registration)

```
POST /token-books/validate-sheet
```

**Request Body:**
```json
{
    "customer_id": 5,
    "milk_type_id": 1,
    "sheet_number": 5,
    "token_book_issue_id": 456
}
```

**Response:**
```json
{
    "is_valid": true,
    "warnings": [
        {
            "code": "NON_SEQUENTIAL_SHEET",
            "message": "Sheet #5 skips ahead. Sheet #4 not yet used.",
            "severity": "WARNING",
            "expected_sheet": 4
        }
    ],
    "can_proceed": true,
    "requires_acknowledgment": true
}
```

### Register Token Sheet with Warnings

```
POST /token-books/register-sheet
```

**Request Body:**
```json
{
    "delivery_id": 789,
    "sheet_number": 5,
    "token_book_issue_id": 456,
    "acknowledged_warnings": ["NON_SEQUENTIAL_SHEET"],
    "acknowledgment_reason": "Customer confirmed #4 is lost"
}
```

**Response:**
```json
{
    "delivery_id": 789,
    "sheet_registered": true,
    "token_book_issue_id": 456,
    "new_current_sheet": 8,
    "warnings_logged": 1,
    "message": "Token Sheet #5 registered. Warning logged for non-sequential sheet."
}
```

### Get Customer Token Book Status

```
GET /token-books/customer/{customer_id}/status
```

**Response:**
```json
{
    "customer_id": 5,
    "customer_name": "Mrs. Sharma",
    "token_books": [
        {
            "book_issue_id": 456,
            "book_number": "#SM-001",
            "issue_date": "2026-01-01",
            "status": "ACTIVE",
            "sheets_used": 20,
            "sheets_remaining": 10,
            "is_old_book": true
        },
        {
            "book_issue_id": 457,
            "book_number": "#SM-002",
            "issue_date": "2026-01-15",
            "status": "ACTIVE",
            "sheets_used": 0,
            "sheets_remaining": 30,
            "is_old_book": false
        }
    ],
    "has_old_book_with_remaining": true,
    "old_book_remaining": 10
}
```

---

## 10. UI/UX Requirements

### Registration Screen

When Checker enters a token sheet number:

1. **Real-time validation** as user types
2. **Warning icons** appear next to sheet number field
3. **Tooltip** shows warning details on hover
4. **Modal dialog** for multiple warnings
5. **Acknowledge checkbox** required before proceeding

### Warning Display

```
Token Sheet Registration
═══════════════════════════════════════════════════

Customer: [Mrs. Sharma]
Milk Type: [Full Cream 1L]
Token Book: [#SM-002 (NEW)]

Sheet Number: [5]

⚠️ Warning: Non-sequential Sheet
   Sheet #4 not yet used

☑️ I acknowledge this warning and want to proceed

Reason (optional): [Customer confirmed #4 is lost]

[Cancel] [Register Token]
═══════════════════════════════════════════════════
```

### Book Status Panel

Side panel showing customer's token book status:

```
Token Book Status
═══════════════════════════════════════════════════

Active Books:
├── Book #SM-001 (Jan 1)
│   ├── Used: 20/30
│   ├── Remaining: 10
│   └── ⚠️ OLD BOOK
│
└── Book #SM-002 (Jan 15)
    ├── Used: 0/30
    ├── Remaining: 30
    └── ✓ CURRENT BOOK

Last 5 Sheets Used:
├── #10 (Jan 10)
├── #9 (Jan 9)
├── #8 (Jan 8)
├── #7 (Jan 7)
└── #6 (Jan 6)

Next Expected: #11
═══════════════════════════════════════════════════
```

---

## 11. Testing Requirements

### Test Cases for Unplanned Delivery

1. Test adding unplanned delivery with token sheet
2. Test adding unplanned delivery with cash sale
3. Test adding unplanned delivery for non-existent customer (error)
4. Test unplanned delivery included in reconciliation
5. Test unplanned delivery audit trail

### Test Cases for Non-sequential Sheets

1. Test sequential sheet registration (no warning)
2. Test sheet skipping ahead (warning displayed)
3. Test out-of-order sheet (warning displayed)
4. Test gap detection (info displayed)
5. Test duplicate sheet registration (error)
6. Test warning acknowledgment required
7. Test warning logged in audit

### Test Cases for New Book Usage

1. Test single active book (no warning)
2. Test new book before old finishes (warning displayed)
3. Test multiple active books
4. Test old book can still be used
5. Test book completion tracking
6. Test book transition warning logged

### Integration Tests

1. Full workflow: Unplanned delivery → Registration → Reconciliation
2. Full workflow: Non-sequential sheets → Warnings → Registration
3. Full workflow: New book → Old book remaining → Warning → Registration
4. Multiple warnings in single registration
5. Warning acknowledgment and audit trail

---

## 12. Summary

This specification covers three critical edge cases in token sheet management:

1. **Customer Changes Mind**: Unplanned deliveries with token sheets are handled seamlessly
2. **Non-sequential Sheets**: System warns Checker but allows registration
3. **New Book Before Old Finishes**: System warns Checker about remaining sheets

The warning system provides:
- Real-time validation during registration
- Clear warning messages with severity levels
- Acknowledgment requirement for warnings
- Complete audit trail for all warnings
- Final decision authority for Checker

This ensures the system handles real-world scenarios while maintaining data integrity and providing transparency to operators.
