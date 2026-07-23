# Business Rules

## Purpose

This document defines the business rules of the Milk Distribution Management System.

These rules are based on the real operational workflow of a traditional milk distribution company.

The AI must never violate these rules.

Business correctness is always more important than implementation convenience.

---

# Business Overview

The company delivers milk to customers every day using predefined delivery routes.

Customers primarily purchase **physical token books** instead of paying for each delivery individually.

Delivery partners collect tokens during delivery and distribute milk accordingly.

The ERP digitizes this workflow while preserving the existing business process.

---

# Core Business Principles

The software must adapt to the existing business.

Never redesign the workflow without approval.

Historical records must always remain available.

Every operational activity should be auditable.

Every business transaction should be traceable.

---

# User Roles

## Owner

Responsible for overall business management.

Responsibilities

- Manage users
- Manage routes
- Manage customers
- Issue token books
- View reports
- Record payments
- Perform reconciliation
- Configure system settings

---

## Checker

Responsible for operational verification.

Responsibilities

- Verify collected tokens
- Record daily collections
- Verify milk allocation
- Verify reconciliation
- Generate operational reports

Checker cannot modify historical records.

---

## Delivery Partner

Responsible for daily milk delivery.

Responsibilities

- View assigned route
- Deliver milk
- Collect tokens
- Record cash sales
- View daily allocation
- Submit reconciliation

Delivery partners should only access their assigned routes.

---

# Customer Rules

A customer represents one delivery location.

Rules

- Every customer belongs to exactly one route.
- Customers may become inactive.
- Historical deliveries must remain visible.
- Customers cannot belong to multiple routes simultaneously.

---

# Route Rules

Routes define daily delivery areas.

Rules

One route

↓

Many customers

↓

One delivery partner

Routes should remain available even if temporarily inactive.

---

# Milk Types

Current supported milk types

- 500 ml
- 1 Liter

Future milk products should be configurable without changing existing logic.

Milk types must remain independent.

---

# Token Book System

The token system is the heart of the business.

The ERP records token usage but does not replace physical tokens.

## Token Book

Each customer may own multiple token books.

Example

Customer A

Book 1001

↓

500 ml

Book 1002

↓

1 Liter

Books remain active until fully consumed.

Books should never be deleted.

---

## Token Number

Token numbers identify physical books.

Rules

Token numbers must be unique.

Historical token numbers must never change.

---

## Token Sheets

Each token book contains

30 token sheets.

Each sheet represents

One delivery.

Sheet numbers

1

↓

30

Every sheet can be used only once.

Collected sheets become permanent history.

---

## Token Collection

Delivery partner collects tokens during delivery.

Checker later verifies collected tokens.

Collected tokens must never be edited.

Incorrect collections require adjustment records.

---

# Delivery Rules

Daily delivery is generated from

- Active customers
- Active token books
- Manual adjustments

Rules

Every delivery belongs to

- Customer
- Route
- Delivery date

Completed deliveries should never be modified.

Corrections create adjustment entries.

---

# Extra Milk

Customers may request additional milk.

Example

Regular

1 Liter

Requested

2 Liters

Extra quantity may be supplied if stock is available.

Extra milk should be recorded separately.

---

# Cash Sales

Milk may be sold without a token.

Examples

Walk-in customer

Neighbour

Emergency sale

Rules

Cash sales are independent of token books.

Cash sales affect reconciliation.

Cash sales must always include

- Milk type
- Quantity
- Amount
- Delivery date

---

# Milk Allocation

Milk allocation happens before delivery begins.

Allocation should consider

- Customer demand
- Active token books
- Previous consumption
- Manual adjustments

Allocation history should remain available.

---

# Leave Requests

Delivery partners may request leave.

Rules

Approved leave must not remove delivery history.

Alternative delivery assignment may be created.

---

# Reconciliation

Every route must balance before closing.

Formula

Loaded Milk

=

Delivered Milk

+

Cash Sales

+

Returned Milk

Every difference should be explained.

Unbalanced routes should remain open.

---

# Reports

The system should support

Operational Reports

Financial Reports

Customer Reports

Route Reports

Cash Sale Reports

Milk Allocation Reports

Reconciliation Reports

Reports are read-only.

Reports must never modify business data.

---

# Data Integrity

Never permanently delete

- Customers
- Token books
- Deliveries
- Cash sales
- Payments
- Reconciliation

Historical records are business assets.

---

# Future Features

The architecture should support

- Customer subscriptions
- Inventory management
- QR token books
- Mobile application
- AI demand prediction
- Route optimization
- WhatsApp notifications
- Multi-branch management

without redesigning the system.

---

# AI Instructions

Before implementing any feature

1. Understand the business workflow.
2. Identify the affected business module.
3. Preserve historical records.
4. Follow existing service patterns.
5. Reuse existing models.
6. Reuse existing exceptions.
7. Maintain backward compatibility.

Never

- Delete historical data.
- Reuse token sheets.
- Modify completed deliveries.
- Close unbalanced routes.
- Bypass authentication.
- Invent new business rules.
- Change the token workflow.

If uncertain, preserve the existing business process rather than introducing a new one.