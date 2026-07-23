# Overall Project Explanation - Milk Distribution ERP

## Table of Contents

1. [Project Introduction](#1-project-introduction)
2. [Real-World Company Perspective](#2-real-world-company-perspective)
3. [Customer Registration Workflow](#3-customer-registration-workflow)
4. [Subscription Management](#4-subscription-management)
5. [Shift Management](#5-shift-management)
6. [Daily Delivery Operations](#6-daily-delivery-operations)
7. [Token Management System](#7-token-management-system)
8. [Token Collection & Settlement](#8-token-collection--settlement)
9. [Reconciliation Process](#9-reconciliation-process)
10. [Payment Management](#10-payment-management)
11. [Reporting & Analytics](#11-reporting--analytics)
12. [AI Business Intelligence](#12-ai-business-intelligence)
13. [Roles & Responsibilities](#13-roles--responsibilities)
14. [Current Implementation Status](#14-current-implementation-status)
15. [Technology Stack](#15-technology-stack)

---

## 1. Project Introduction

**Milk Distribution ERP** is a specialized enterprise resource planning system built for milk distribution businesses that operate using **physical token books** for daily milk delivery and payment collection.

This is **NOT** a generic billing or inventory software. It is specifically designed around the **actual workflow** followed by milk distributors in real-world operations.

### The Problem Being Solved

Most milk distribution companies still use **handwritten registers** for their daily operations:

- Customer records maintained in notebooks
- Token books tracked manually
- Daily reconciliation done on paper
- Payment collection tracked in memory or loose papers
- No historical data for business analysis
- Errors in counting and reconciliation
- Difficulty tracking pending collections

**This ERP replaces those manual registers with a structured digital system while keeping the workflow familiar to employees.**

---

## 2. Real-World Company Perspective

### How a Typical Milk Distribution Company Operates

Imagine a real milk distribution company (let's call it "FreshMilk Distributors"):

```
Company Structure:
├── Owner (Business Owner)
├── Office Staff / Checker (1-2 people)
├── Delivery Partners (3-10 people)
└── Customers (50-500 households)
```

### Daily Business Flow (Real World)

**Early Morning (4:00 AM - 5:00 AM):**
1. Milk arrives from the dairy/farm
2. Owner or Checker loads milk into delivery containers
3. Each Delivery Partner receives their assigned milk quota
4. Delivery Partner gets the delivery list for their route

**Morning Shift (5:00 AM - 9:00 AM):**
1. Delivery Partner goes door-to-door delivering milk
2. Collects token sheets from customers who have them
3. Collects cash from customers paying for today's milk
4. Notes customer requests (extra milk, no milk tomorrow, vacation)
5. Returns to office with remaining milk, collected tokens, and cash

**Office Processing (9:00 AM - 12:00 PM):**
1. Checker receives tokens, cash, and remaining milk from Delivery Partner
2. Checker registers each customer's token sheet in the register
3. Marks customers who didn't provide tokens as "Pending"
4. Records cash sales
5. Records returned milk
6. Reconciles: Total Milk Loaded = Token Milk + Cash Sales + Returned Milk
7. If mismatch found, investigates with Delivery Partner
8. Closes the route when balanced

**Afternoon/Evening:**
1. Same process repeats for Evening Shift (4:00 PM - 8:00 PM)
2. Owner reviews daily reports
3. Checks outstanding payments
4. Plans for next day

### Why This System Is Unique

Unlike standard delivery apps (like food delivery), milk distribution has unique characteristics:

1. **Subscription-Based**: Customers get milk daily, not on-demand
2. **Token Book System**: Payment is through physical token books (like prepaid coupons)
3. **Two Shifts**: Morning and Evening deliveries are separate operations
4. **Same Customer, Multiple Products**: A customer might get 1L packet in morning, 500ml in evening
5. **Pending Tokens**: Customers can submit token sheets later (flexibility)
6. **Advance Credits**: Customers can give extra tokens for future delivery
7. **Unplanned Deliveries**: Sometimes customers change their mind and want milk even if they said "no milk tomorrow"

---

## 3. Customer Registration Workflow

### What Happens When a New Customer Joins

**Real-World Scenario:**
> A new customer, Mrs. Sharma, calls the milk distribution company and wants to start receiving milk.

**Step-by-Step Process:**

```
Step 1: Customer Information Collection
├── Customer Name: "Mrs. Priya Sharma"
├── Primary Phone: "9876543210"
├── Alternate Phone: "9876543211" (optional)
├── Address: "42, Green Valley Apartments, Sector 5"
├── Assigned Route: "Route A - Sector 5"
└── Remarks: "Preferred delivery before 7 AM"
```

**Step 2: System Validation**
The ERP validates:
- Phone number is unique (no duplicate customers)
- Primary and alternate phone numbers are different
- Assigned route exists and is active
- Customer code is auto-generated (e.g., "CUST-001")

**Step 3: Customer Creation**
```json
{
    "customer_code": "CUST-001",
    "customer_name": "Mrs. Priya Sharma",
    "primary_phone": "9876543210",
    "alternate_phone": "9876543211",
    "address": "42, Green Valley Apartments, Sector 5",
    "route_id": 1,
    "remarks": "Preferred delivery before 7 AM",
    "is_active": true
}
```

**Step 4: Subscription Setup**
After registration, the customer sets up their milk subscription:
- What milk type? (250ml, 500ml, 1L, 2L)
- How many packets in morning?
- How many packets in evening?

**Database Tables Involved:**
- `customers` - Stores customer information
- `routes` - Stores delivery routes
- `subscriptions` - Stores customer milk subscriptions

### Key Business Rules for Customer Registration

1. Every customer must belong to exactly one delivery route
2. Primary phone number must be unique across all customers
3. Customer code is automatically generated (no manual entry)
4. Customers can be temporarily deactivated without deleting history (soft delete)
5. A customer can have multiple subscriptions (different milk types)

---

## 4. Subscription Management

### What is a Subscription?

A subscription defines **what milk a customer receives regularly**.

**Real-World Example:**
> Mrs. Sharma wants:
> - Morning: 1 packet of 1 Liter milk
> - Evening: 1 packet of 500ml milk

**Database Record:**
```
Subscription Record:
├── Customer: Mrs. Sharma (CUST-001)
├── Milk Type: 1 Liter
├── Morning Quantity: 1
├── Evening Quantity: 0
├── Status: ACTIVE
└── Start Date: 2026-07-23

Subscription Record 2:
├── Customer: Mrs. Sharma (CUST-001)
├── Milk Type: 500ml
├── Morning Quantity: 0
├── Evening Quantity: 1
├── Status: ACTIVE
└── Start Date: 2026-07-23
```

### Subscription Rules

1. **Multiple Milk Types Allowed**: A customer can subscribe to 1L milk AND 500ml milk
2. **Separate Morning/Evening**: Each shift has its own quantity
3. **Active/Inactive Status**: Subscriptions can be paused and resumed
4. **Effective Dates**: Subscriptions have start and optional end dates

### Delivery Exceptions (Temporary Changes)

Customers frequently request temporary changes:

| Exception Type | Example | Effect |
|---------------|---------|--------|
| No Milk | "No milk tomorrow" | Excludes from tomorrow's delivery |
| Extra Milk | "2 extra packets tomorrow" | Adds to tomorrow's delivery |
| Vacation | "No milk for 5 days" | Excludes for the vacation period |
| Resume | "Resume milk from Monday" | Reactivates after vacation |
| Quantity Change | "Only 500ml tomorrow" | Temporarily changes quantity |

**Important:** Delivery Exceptions are **temporary**. After the exception period ends, the original subscription automatically becomes active again.

### How Subscriptions Drive Delivery

The ERP uses subscriptions to **automatically generate** the daily delivery list:

```
Daily Delivery Generation Logic:
│
├── Get all active customers on the route
├── For each customer:
│   ├── Check active subscriptions
│   ├── Check for delivery exceptions
│   ├── Apply exceptions (if any)
│   └── Calculate: Morning Quantity, Evening Quantity
├── Generate delivery list
└── Send to Delivery Partner
```

---

## 5. Shift Management

### What Are Shifts?

Milk distribution operates on **fixed delivery shifts**. Version 1 supports two shifts:

| Shift | Typical Timing | Description |
|-------|---------------|-------------|
| **Morning** | 5:00 AM - 9:00 AM | Most common shift, high demand |
| **Evening** | 4:00 PM - 8:00 PM | Second shift, moderate demand |

### Shift Independence

**Each shift operates completely independently.** This is a critical business rule.

**Example:**
```
Morning Shift:
├── Dispatch: 110 Liters
├── Delivered: 95 Liters
├── Cash Sales: 8 Liters
├── Returned: 7 Liters
└── Reconciliation: 95 + 8 + 7 = 110 ✓ BALANCED

Evening Shift:
├── Dispatch: 85 Liters
├── Delivered: 72 Liters
├── Cash Sales: 5 Liters
├── Returned: 8 Liters
└── Reconciliation: 72 + 5 + 8 = 85 ✓ BALANCED
```

**Each shift has its own:**
- Delivery Schedule
- Milk Dispatch
- Reconciliation
- Route Closing

### How Shifts Affect Subscriptions

A customer's subscription specifies quantities for each shift:

```
Customer: Mr. Kumar
├── Subscription: 1 Liter Milk
│   ├── Morning Quantity: 1
│   └── Evening Quantity: 1
│
├── Delivery Exception (Tomorrow):
│   ├── Morning: 2 packets (extra milk for guests)
│   └── Evening: 0 (going out for dinner)
```

### Token Collection Across Shifts

**Critical Rule:** Token collection is **independent** of delivery timing.

**Supported Scenarios:**
| Delivery Shift | Token Submitted | Valid? |
|---------------|----------------|--------|
| Morning | Morning same day | ✅ Yes |
| Morning | Evening same day | ✅ Yes |
| Morning | Next day morning | ✅ Yes |
| Evening | Next day morning | ✅ Yes |
| Morning + Evening | Together | ✅ Yes |

This flexibility means customers don't have to provide token sheets at the exact time of delivery.

---

## 6. Daily Delivery Operations

### Complete Daily Workflow

```
PHASE 1: PLANNING (Early Morning)
│
├── ERP generates delivery list from subscriptions
├── Applies delivery exceptions
├── Creates per-route delivery schedules
│
PHASE 2: DISPATCH (Before Route Starts)
│
├── Owner/Checker loads milk into containers
├── Records dispatch: Route + Partner + Total Milk
├── Delivery Partner receives:
│   ├── Physical milk containers
│   ├── Delivery list (paper or mobile)
│   └── Token book collection pouch
│
PHASE 3: DELIVERY (During Shift)
│
├── Delivery Partner visits each customer
├── For each customer:
│   ├── Delivers milk
│   ├── Collects token sheet (if available)
│   ├── Collects cash (if paying today)
│   ├── Notes customer requests
│   └── Moves to next customer
│
PHASE 4: RETURN (After Route Completion)
│
├── Delivery Partner returns to office
├── Hands over:
│   ├── Collected token sheets
│   ├── Cash collected
│   ├── Remaining milk
│   └── Customer requests
│
PHASE 5: OFFICE PROCESSING (After Return)
│
├── Checker opens today's delivery route
├── Registers each customer:
│   ├── Token Sheet (if collected)
│   ├── Pending Token (if not collected)
│   ├── Cash Sale (if cash payment)
│   └── Not Delivered (if skipped)
├── Adds unplanned deliveries (if any)
├── Enters cash sales total
├── Enters returned milk total
├── Runs reconciliation
├── Fixes any mismatches
└── Closes the route
```

### Delivery Status Types

| Status | Meaning | When Used |
|--------|---------|-----------|
| **Delivered** | Milk delivered, token received | Customer provided token sheet |
| **Pending Token** | Milk delivered, no token yet | Customer will provide later |
| **Cash Sale** | Milk sold for cash | Customer paid with cash |
| **Not Delivered** | Scheduled but not delivered | Customer unavailable/refused |
| **Cancelled** | Cancelled before dispatch | Delivery exception applied |

### Delivery Sources

| Source | Description | Example |
|--------|-------------|---------|
| **Planned** | Auto-generated from subscriptions | Regular daily delivery |
| **Unplanned** | Manually added by Checker | Customer changed mind, wants milk today |

**Unplanned Delivery Example:**
```
Yesterday: Customer said "No milk tomorrow"
Today's schedule: Customer EXCLUDED

During delivery: Customer calls Delivery Partner, says "Please send milk"
Delivery Partner: Delivers milk anyway

Checker Action:
├── Clicks "Add Unplanned Delivery"
├── Searches by customer name/phone/token number
├── Records: Milk Type, Quantity, Shift, Reason
├── Delivery marked as "Unplanned"
└── Original schedule preserved for audit
```

---

## 7. Token Management System

### What is a Token Book?

A **Token Book** is a physical booklet given to customers. Each page (sheet) in the book represents one unit of milk delivery payment.

**Real-World Example:**
```
Token Book #1205
├── Customer: Mrs. Sharma
├── Milk Type: 1 Liter
├── Total Sheets: 30
├── Sheets Used: 12
├── Sheets Remaining: 18
└── Status: Active
```

### Token Identity

A **Token Identity** uniquely identifies a customer's token book type. It consists of:

```
Token Identity = Customer + Milk Type + Token Number

Example:
├── Customer: Mrs. Sharma
├── Milk Type: 1 Liter
├── Token Number: 1205
└── UNIQUE COMBINATION

Note: Same customer can have DIFFERENT Token Identities:
├── Mrs. Sharma + 1 Liter + Token #1205
└── Mrs. Sharma + 500ml + Token #1205 (different milk type = different identity)
```

### Token Book Lifecycle

```
Step 1: Token Identity Creation
├── Owner creates token identity for customer
├── Assigns: Customer + Milk Type + Token Number
│
Step 2: Token Book Issue
├── Owner issues physical token book
├── Records: Issue date, payment mode (Prepaid/Postpaid)
├── Book status: "Active"
│
Step 3: Daily Token Collection
├── Customer provides token sheet with each delivery
├── Checker registers the sheet number
├── Token Ledger updated
│
Step 4: Book Completion
├── All sheets used
├── Book status: "Completed"
├── New book issued if needed
```

### Token Book Payment Modes

| Mode | Description | When Used |
|------|-------------|-----------|
| **Prepaid** | Customer pays for book upfront | New customers, default option |
| **Postpaid** | Customer pays after using the book | Trusted, regular customers |

**Payment Status:**
| Status | Meaning |
|--------|---------|
| **Pending** | No payment received yet |
| **Partial** | Some amount paid |
| **Paid** | Full payment received |

---

## 8. Token Collection & Settlement

### How Token Collection Works

**During Delivery:**
1. Delivery Partner delivers milk to customer
2. Customer provides token sheet (tears from book)
3. Delivery Partner collects the sheet
4. At office, Checker registers the sheet number

**During Office Processing:**
```
Checker Registration Options for Each Customer:

Option 1: TOKEN SHEET
├── Milk delivered ✅
├── Token received ✅
├── Enter sheet number: 11
└── System validates: Token #, milk type, sequence

Option 2: PENDING TOKEN
├── Milk delivered ✅
├── Token NOT received ❌
├── Mark as "Pending"
└── Customer will provide later

Option 3: CASH SALE
├── Milk delivered ✅
├── Customer pays cash
├── Record as cash sale
└── No token involved

Option 4: NOT DELIVERED
├── Milk NOT delivered ❌
├── Customer unavailable/refused
└── Record as skipped
```

### Pending Token Settlement

**Real-World Scenario:**
> Mrs. Sharma was not home during morning delivery. Delivery Partner left milk but didn't get the token sheet. Mrs. Sharma promises to provide it in the evening.

```
Day 1, Morning:
├── Milk Delivered: 1 Liter
├── Token: NOT RECEIVED
├── Status: Pending Token
└── Pending Balance: +1 sheet

Day 1, Evening (or any future time):
├── Mrs. Sharma provides the token sheet
├── Checker registers: Sheet #11
├── Pending Cleared
└── Pending Balance: 0
```

### Advance Token Collection

**Real-World Scenario:**
> Mr. Kumar is going on vacation next week. He gives 5 extra token sheets today for future delivery.

```
Today's Delivery: 1 Liter
Token Sheets Provided: 6 (1 for today + 5 advance)

Result:
├── Today's delivery settled ✅
├── Advance Credit: 5 sheets
├── Future deliveries automatically use advance credit
└── No need to provide tokens for next 5 days
```

### Token Ledger

The **Token Ledger** maintains a permanent record of all token transactions for each Token Identity.

```
Token Ledger Entry Types:
├── Token Received (customer provided sheet)
├── Pending Created (milk delivered, no token)
├── Pending Cleared (pending token submitted)
└── Manual Adjustment (correction by owner)

Balance Calculation:
├── Negative Balance = Customer owes sheets
├── Positive Balance = Customer has advance credit
└── Zero Balance = Account settled
```

### Critical Business Rules

1. **Half-liter tokens cannot settle one-liter balances** (and vice versa)
2. **Different milk types are reconciled independently**
3. **Same token book can be used across both shifts**
4. **Pending tokens can be submitted any time** (no deadline)
5. **Advance credits remain until consumed**

---

## 9. Reconciliation Process

### What is Reconciliation?

Reconciliation is the **end-of-day verification** that ensures every liter of milk dispatched has been properly accounted for.

### The Reconciliation Equation

```
Loaded Milk = Token Milk Registered + Cash Sales + Returned Milk

Example:
├── Loaded Milk: 110 Liters
├── Token Registered: 95 Liters (from all token sheets)
├── Cash Sales: 8 Liters (from cash payments)
├── Returned Milk: 7 Liters (milk brought back)
│
├── Total Accounted: 95 + 8 + 7 = 110 Liters
└── Status: ✅ BALANCED
```

### Step-by-Step Reconciliation

```
Step 1: Complete Token Registration
├── Checker registers all customers
├── Each customer marked as: Token/Pending/Cash/Not Delivered
│
Step 2: Enter Cash Sales Total
├── Checker enters total cash sale liters
├── Example: 8 Liters
│
Step 3: Enter Returned Milk Total
├── Checker enters total returned milk
├── Example: 7 Liters
│
Step 4: System Calculates
├── Auto-calculates: Total Token Milk = 95 Liters
├── Applies formula: 95 + 8 + 7 = 110
├── Compares with Loaded Milk: 110
│
Step 5: Result
├── If equal: ✅ BALANCED → Route can be closed
└── If not equal: ❌ DIFFERENCE → Correction needed
```

### Correction Mode (When Reconciliation Fails)

**Real-World Scenario:**
```
Loaded Milk: 110 L
Token Registered: 94 L
Cash Sales: 8 L
Returned Milk: 7 L
Total: 109 L
Difference: 1 L ❌

Checker Investigation:
├── "Was any token sheet forgotten?"
├── "Was a customer missed?"
├── "Was cash collected but not recorded?"
├── "Was additional milk delivered?"
│
Checker Actions:
├── Edit token registrations
├── Change Pending to Token Sheet (if customer provides late)
├── Correct cash sales amount
├── Correct returned milk amount
├── Add unplanned deliveries
│
After Correction:
├── Token Registered: 95 L
├── Cash Sales: 8 L
├── Returned Milk: 7 L
├── Total: 110 L ✅ BALANCED
└── Route can be closed
```

### Route Closing Rules

**A route CANNOT be closed until:**
1. Every customer has been processed
2. Reconciliation is balanced
3. Cash sales are entered
4. Returned milk is entered

**After closing:**
- Token Ledger is finalized
- Daily reports are generated
- Route becomes **read-only**
- **Only the Owner can reopen** a closed route

---

## 10. Payment Management

### Token Book Payments

When a customer receives a token book, payment is recorded:

```json
{
    "token_book_issue_id": 1,
    "payment_mode": "PREPAID",
    "book_price": 350.00,
    "amount_paid": 350.00,
    "balance_amount": 0.00,
    "payment_status": "PAID",
    "payment_date": "2026-07-23",
    "collected_by": "owner_001"
}
```

### Payment Types

| Type | Description |
|------|-------------|
| **Prepaid** | Full payment before book issuance |
| **Postpaid** | Payment after book completion |
| **Partial** | Installment payments allowed |

### Outstanding Payments

The system tracks:
- Customers with pending payments
- Partial payment history
- Overdue amounts
- Payment collection trends

---

## 11. Reporting & Analytics

### Report Categories

| Category | Examples |
|----------|---------|
| **Dashboard** | Today's summary, active customers, pending tokens |
| **Customer Reports** | Customer list, subscription report, payment history |
| **Route Reports** | Route performance, customer distribution |
| **Delivery Reports** | Daily delivery, unplanned deliveries, exceptions |
| **Token Reports** | Active books, pending tokens, token history |
| **Payment Reports** | Daily collection, outstanding payments |
| **Reconciliation Reports** | Daily reconciliation, route closing status |
| **Business Analytics** | Revenue trends, customer growth, milk demand |

### Sample Daily Report

```
Daily Report - 23 July 2026
═══════════════════════════════════════

Morning Shift:
├── Total Customers: 120
├── Delivered: 115
├── Pending Tokens: 8
├── Cash Sales: 3
├── Not Delivered: 5
├── Milk Dispatched: 110 L
├── Milk Delivered: 95 L
├── Cash Sales: 8 L
├── Returned: 7 L
└── Reconciliation: ✅ BALANCED

Evening Shift:
├── Total Customers: 95
├── Delivered: 88
├── Pending Tokens: 5
├── Cash Sales: 2
├── Not Delivered: 7
├── Milk Dispatched: 85 L
├── Milk Delivered: 72 L
├── Cash Sales: 5 L
├── Returned: 8 L
└── Reconciliation: ✅ BALANCED

Financial Summary:
├── Token Sheets Collected: 167
├── Cash Collected: ₹2,400
├── Pending Tokens: 13
└── Outstanding Payments: ₹4,500
```

---

## 12. AI Business Intelligence

### What the AI Module Does

The AI module goes beyond standard reporting. It **analyzes patterns** and **generates recommendations**.

### AI Data Sources

```
Customer Information ←────┐
Customer Subscriptions ←──┤
Daily Deliveries ←────────┤
Token Registrations ←─────┤
Payment History ←─────────┼──→ AI Engine
Route Information ←───────┤
Milk Dispatch ←───────────┤
Reconciliation Records ←──┘
```

### AI Intelligence Categories

#### 1. Customer Intelligence

| Pattern Detected | AI Suggestion |
|-----------------|---------------|
| Customer regularly buys extra milk | "Consider increasing subscription quantity" |
| Frequent pending tokens | "Review token collection with customer" |
| Long-term inactive customer | "Contact customer to confirm status" |
| High milk consumption | "Consider offering premium services" |

#### 2. Delivery Intelligence

| Pattern Detected | AI Suggestion |
|-----------------|---------------|
| Frequent unplanned deliveries | "Update subscription to match actual consumption" |
| Frequent delivery exceptions | "Review if subscription needs modification" |
| Route imbalance | "Redistribute customers between routes" |

#### 3. Token Intelligence

| Pattern Detected | AI Suggestion |
|-----------------|---------------|
| High pending token balance | "Follow up to improve collection" |
| Frequent advance tokens | "Recommend prepaid subscription plans" |
| Low collection efficiency | "Review token submission process" |

#### 4. Payment Intelligence

| Pattern Detected | AI Suggestion |
|-----------------|---------------|
| Long overdue payments | "Prioritize payment collection" |
| Late payment pattern | "Consider changing to prepaid books" |
| Consistent on-time payments | "Eligible for postpaid issuance" |

### AI Business Health Score

The AI generates an overall **Business Health Score** based on:
- Collection efficiency
- Customer retention
- Delivery accuracy
- Reconciliation success rate
- Revenue trends

### Predictive Analytics

| Prediction Type | Description |
|----------------|-------------|
| **Milk Demand Forecast** | Predicts tomorrow's/next week's requirement |
| **Customer Growth** | Estimates future customer additions |
| **Revenue Forecast** | Predicts upcoming revenue |
| **Payment Collection** | Predicts outstanding collection |

### Important: AI Decision Support Rule

**AI recommendations are ADVISORY ONLY.**

```
AI may recommend:
├── "Increase customer subscription"
├── "Merge delivery routes"
├── "Issue new token book"
└── "Contact inactive customer"

BUT:
├── AI NEVER changes business records automatically
├── Final decision belongs to Owner/authorized staff
└── Human oversight is always required
```

---

## 13. Roles & Responsibilities

### Role Hierarchy

```
                     OWNER
                       │
         ┌─────────────┴─────────────┐
         │                           │
      CHECKER               DELIVERY PARTNER
         │
         ▼
    CUSTOMER (Future)
```

### Owner Responsibilities

| Area | Tasks |
|------|-------|
| **Business Setup** | Configure routes, milk types, business rules |
| **Customer Management** | Create/update/deactivate customers |
| **Token Management** | Create token identities, issue books |
| **Financial Management** | Record payments, view outstanding |
| **Reports & Analytics** | Access all reports, AI insights |
| **Administration** | Manage users, reopen routes |

### Checker Responsibilities

| Area | Tasks |
|------|-------|
| **Token Registration** | Register token sheets, pending tokens |
| **Cash Sale Recording** | Record cash sales |
| **Unplanned Delivery** | Add unplanned deliveries |
| **Reconciliation** | Perform end-of-day reconciliation |
| **Route Closing** | Close balanced routes |
| **Corrections** | Fix reconciliation differences |

### Delivery Partner Responsibilities

| Area | Tasks |
|------|-------|
| **Physical Delivery** | Deliver milk to customers |
| **Token Collection** | Collect token sheets from customers |
| **Cash Collection** | Collect cash payments |
| **Customer Requests** | Note customer requests |
| **Return Milk** | Return remaining milk to office |

**Important:** Delivery Partner does NOT perform ERP data entry (no token registration, no reconciliation).

### Permission Matrix

| Module | Owner | Checker | Delivery Partner |
|--------|:-----:|:-------:|:----------------:|
| User Management | ✅ | ❌ | ❌ |
| Customer Management | ✅ | View | View Assigned |
| Route Management | ✅ | View | View |
| Subscriptions | ✅ | View | View |
| Token Registration | ✅ | ✅ | ❌ |
| Cash Sale Registration | ✅ | ✅ | Collect Only |
| Reconciliation | View | ✅ | ❌ |
| Route Closing | ✅ | ✅ | ❌ |
| Reports | ✅ | Limited | Limited |

---

## 14. Current Implementation Status

### Completed Modules (Sprint 1 & 2)

| Module | Status | Components |
|--------|--------|------------|
| Authentication | ✅ Complete | JWT Login, Role-Based Access |
| User Management | ✅ Complete | CRUD, Roles |
| Customer Management | ✅ Complete | CRUD, Soft Delete |
| Route Management | ✅ Complete | CRUD |
| Milk Type Management | ✅ Complete | CRUD |
| Employee Management | ✅ Complete | CRUD, Leave Requests |
| Customer Subscriptions | ✅ Complete | CRUD, Customer/MilkType Validation |

### In-Progress Modules (Sprint 4 & 5)

| Module | Status | Notes |
|--------|--------|-------|
| Token Book Management | 🔄 Partial | Router/Service files exist but empty |
| Cash Sales | 🔄 Partial | Model exists but empty |
| Milk Allocation | 🔄 Partial | Model/Service exist but empty |
| Reconciliation | 🔄 Partial | Service file exists but empty |

### Not Yet Implemented

| Module | Sprint | Priority |
|--------|--------|----------|
| Delivery Exceptions | Sprint 2 | High |
| Daily Delivery Generation | Sprint 3 | High |
| Milk Dispatch | Sprint 3 | High |
| Token Identity Management | Sprint 4 | High |
| Token Registration | Sprint 4 | High |
| Token Ledger | Sprint 4 | High |
| Payment Management | Sprint 6 | Medium |
| Reports API | Sprint 7 | Medium |
| AI Business Intelligence | Sprint 8 | Low |
| React Frontend | Sprint 9 | High |
| Testing & Deployment | Sprint 10 | High |

### Key Empty Files (To Be Implemented)

```
app/services/
├── delivery_service.py      (empty - needs implementation)
├── reconciliation_service.py (empty - needs implementation)
└── token_service.py         (empty - needs implementation)

app/routers/
├── token_books.py           (empty - needs implementation)
├── cash_sales.py            (empty - needs implementation)
├── milk_allocation.py       (empty - needs implementation)
├── dashboard.py             (empty - needs implementation)
└── reports.py               (empty - needs implementation)

app/models/
├── token_book.py            (empty - needs implementation)
├── cash_sale.py             (empty - needs implementation)
├── milk_allocation.py       (empty - needs implementation)
└── reconciliation.py        (empty - needs implementation)
```

---

## 15. Technology Stack

### Backend

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Web framework |
| **Python 3** | Programming language |
| **SQLAlchemy 2** | ORM (Object-Relational Mapping) |
| **Alembic** | Database migrations |
| **Pydantic v2** | Data validation |
| **PostgreSQL** | Database |
| **JWT** | Authentication |

### Architecture Pattern

```
HTTP Request
    ↓
Router Layer (FastAPI endpoints)
    ↓
Authentication Layer (JWT validation)
    ↓
Service Layer (Business logic)
    ↓
Database Layer (SQLAlchemy ORM)
    ↓
JSON Response
```

### Folder Structure

```
milk-management-ai/
├── app/
│   ├── api/           # API endpoints (versioned)
│   ├── common/        # Shared utilities
│   ├── constants/     # Roles, Shifts, Statuses
│   ├── core/          # Auth, Config, Security
│   ├── exceptions/    # Custom exceptions
│   ├── models/        # SQLAlchemy models
│   ├── repositories/  # (empty - future use)
│   ├── routers/       # FastAPI routers
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── alembic/           # Database migrations
├── scripts/           # Seed data, test scripts
├── tests/             # Test files
└── docs/              # Documentation
```

---

## Quick Reference Card

### For New Developers

1. **Read this document first** to understand the business context
2. **Understand the token system** - it's the core of the business
3. **Know the reconciliation formula** - it's the most critical business rule
4. **Understand shift independence** - morning and evening are separate operations
5. **Remember: delivery and payment are independent** - customers can pay later

### Key Business Formulas

```
Reconciliation: Loaded Milk = Token Milk + Cash Sales + Returned Milk
Token Balance: Advance Credits - Pending Tokens = Net Balance
Daily Delivery: Subscriptions + Exceptions - Cancellations = Delivery List
```

### Key Business Rules

1. Delivery and payment are independent
2. Token books are payment instruments, not delivery controllers
3. Customer subscriptions determine delivery
4. Daily reconciliation ensures accountability
5. Human decision-making remains important (AI assists, doesn't decide)
6. Minimize unnecessary data entry
7. Preserve complete business history

---

*This document provides a comprehensive overview of the Milk Distribution ERP system. For detailed API specifications, refer to `API Specification.md`. For database schema details, refer to `Database Design.md`.*
