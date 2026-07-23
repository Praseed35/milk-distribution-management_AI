# Business Workflows

## Purpose

This document defines the operational workflows of the Milk Distribution Management System.

Unlike `business_rules.md`, which defines business constraints, this document describes the day-to-day operational processes followed by the company.

Every AI assistant must preserve these workflows when implementing features.

---

# Daily Business Cycle

The business operates on a daily cycle.

```
Prepare Milk

↓

Allocate Milk

↓

Load Vehicles

↓

Deliver Milk

↓

Collect Tokens

↓

Record Cash Sales

↓

Return Remaining Milk

↓

Checker Verification

↓

Route Reconciliation

↓

Close Daily Operations
```

Every module in the ERP supports one or more of these steps.

---

# Customer Registration Workflow

```
Owner

↓

Create Customer

↓

Assign Route

↓

Save Customer

↓

Customer becomes Active

↓

Eligible for Token Book Issuance
```

Rules

- Customer must belong to one route.
- Customer cannot receive deliveries without an active route.
- Customer record is never permanently deleted.

---

# Token Book Issuance Workflow

Token books are issued only by the Owner.

```
Select Customer

↓

Choose Milk Type

↓

Generate Token Book

↓

Assign Token Number

↓

Generate 30 Token Sheets

↓

Print / Issue Physical Book

↓

Book becomes Active
```

Rules

- Every book contains exactly 30 sheets.
- Every sheet is numbered from 1 to 30.
- Books remain active until all sheets are consumed or manually closed.

---

# Daily Milk Allocation Workflow

Milk allocation happens before deliveries begin.

```
Review Active Customers

↓

Calculate Expected Demand

↓

Include Manual Adjustments

↓

Allocate Milk by Route

↓

Approve Allocation

↓

Load Delivery Vehicle
```

Allocation must be completed before delivery starts.

---

# Delivery Workflow

```
Delivery Partner Starts Route

↓

Visit Customer

↓

Collect Token

↓

Deliver Milk

↓

Record Delivery

↓

Repeat for Remaining Customers

↓

Complete Route
```

Rules

- One token = one delivery.
- Used tokens cannot be reused.
- Completed deliveries are immutable.

---

# Extra Milk Workflow

Customers may request additional milk during delivery.

```
Customer Requests Extra Milk

↓

Delivery Partner Checks Available Stock

↓

Supply Extra Milk

↓

Record as Cash Sale

↓

Continue Route
```

Extra milk does not consume a token unless business rules change.

---

# Cash Sale Workflow

Cash sales are separate from token-based deliveries.

```
Walk-in Customer

OR

Existing Customer Needs Extra Milk

↓

Record Milk Type

↓

Record Quantity

↓

Calculate Amount

↓

Collect Payment

↓

Save Cash Sale
```

Cash sales affect route reconciliation.

---

# Token Collection Workflow

After completing deliveries, collected tokens are handed to the Checker.

```
Delivery Partner

↓

Submit Collected Tokens

↓

Checker Verifies

↓

Mark Tokens as Collected

↓

Store for Audit
```

Collected tokens cannot be modified after verification.

---

# Payment Collection Workflow

Payments may occur independently of delivery.

```
Customer Pays

↓

Select Customer

↓

Enter Amount

↓

Choose Payment Method

↓

Save Payment

↓

Update Outstanding Balance
```

Rules

- Partial payments are allowed.
- Advance payments are allowed.
- Payment history is immutable.

---

# Route Reconciliation Workflow

Every delivery route must be reconciled before closing.

```
Loaded Milk

↓

Delivered Milk

↓

Cash Sales

↓

Returned Milk

↓

Calculate Difference

↓

Balanced?

↓

Yes → Close Route

No → Investigate Difference
```

Routes must not close while unbalanced.

---

# Checker Verification Workflow

The Checker verifies operational accuracy.

```
Review Deliveries

↓

Verify Tokens

↓

Verify Cash Sales

↓

Verify Returned Milk

↓

Approve Reconciliation
```

Checker cannot modify historical records.

---

# Daily Closing Workflow

```
All Routes Completed

↓

All Routes Reconciled

↓

Reports Generated

↓

Daily Summary Created

↓

Business Day Closed
```

No further operational changes should be made after the day is closed without authorized adjustment procedures.

---

# Exception Workflows

## Lost Token Book

```
Customer Reports Loss

↓

Owner Verifies

↓

Mark Existing Book as Lost

↓

Issue New Book

↓

Retain Lost Book History
```

---

## Delivery Partner Leave

```
Leave Request

↓

Owner Approval

↓

Assign Substitute Delivery Partner

↓

Continue Delivery Schedule
```

---

## Customer Route Change

```
Select Customer

↓

Assign New Route

↓

Update Future Deliveries

↓

Preserve Historical Route Assignments
```

Historical deliveries must continue to reference the original route.

---

# Audit Trail

The following actions should always be traceable:

- Customer creation
- Route assignment
- Token book issuance
- Delivery completion
- Cash sale recording
- Payment recording
- Reconciliation
- User login
- Role changes

---

# AI Instructions

Before implementing a feature:

1. Identify which business workflow is affected.
2. Preserve the sequence of operational steps.
3. Do not skip mandatory verification stages.
4. Maintain historical records for every workflow.
5. Ensure every workflow remains auditable.

Never:

- Bypass token collection.
- Skip reconciliation.
- Allow route closure without verification.
- Delete workflow history.
- Merge unrelated workflows.

---

# Golden Rule

The ERP exists to digitize the company's existing operations—not to redefine them.

Every feature should support, simplify, or automate the established business workflow while preserving its integrity.