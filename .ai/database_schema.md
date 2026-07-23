# Database Schema

## Purpose

This document defines the complete logical database design for the Milk Distribution
Management System.

It is the single source of truth for:

- Database entities
- Relationships
- Business constraints
- Foreign keys
- Entity responsibilities

The AI MUST understand this document before creating any database model,
repository, service, migration or API.

---

# Database Design Principles

The project follows a normalized relational database design.

Rules

- Every table has a UUID primary key.
- Every table contains audit timestamps.
- Business history must never be deleted.
- Soft delete is preferred.
- Foreign keys must be enforced.
- Every transaction must be auditable.
- Business logic never belongs inside database models.

Standard Columns

Every table should contain whenever applicable:

id
created_at
updated_at
created_by
updated_by
is_active

---

# Domain Overview

Authentication

↓

Users

↓

Routes

↓

Customers

↓

Subscriptions

↓

Token Books

↓

Daily Delivery

↓

Delivery Exceptions

↓

Cash Sales

↓

Payments

↓

Reconciliation

↓

Reports

---

# Authentication Domain

## User

Purpose

Represents every authenticated system user.

Fields

- id
- username
- email
- password_hash
- full_name
- phone
- role
- is_active
- created_at
- updated_at

Relationships

User

↓

Many Routes

↓

Many Deliveries

Business Rules

- Username must be unique.
- Email must be unique.
- Password never stored in plain text.

---

## Role

Purpose

Defines system permissions.

Examples

Owner

Checker

Delivery Partner

Administrator

Business Rules

Roles control API authorization only.

---

# Master Data

## Route

Purpose

Represents a milk delivery route.

Fields

- id
- route_code
- route_name
- description
- delivery_partner_id
- is_active

Relationships

Route

↓

Many Customers

↓

Many Deliveries

↓

Many Reports

Business Rules

Route code must be unique.

Customers cannot belong to multiple routes.

---

## Milk Type

Purpose

Represents a milk product.

Examples

500 ml

1 Litre

Fields

- id
- code
- name
- volume_ml
- is_active

Business Rules

Milk types are immutable.

Historical transactions must preserve original milk type.

---

# Customer Domain

## Customer

Purpose

Represents a customer.

Fields

- id
- customer_code
- name
- phone
- address
- route_id
- status

Relationships

Customer

↓

Many Subscriptions

↓

Many Token Books

↓

Many Daily Deliveries

↓

Many Payments

Business Rules

One customer belongs to exactly one route.

Customer may own multiple token books.

Customer may have multiple subscriptions.

Historical deliveries remain after customer becomes inactive.

---

# Subscription Domain

## Subscription

Purpose

Represents recurring milk requirements.

Fields

- id
- customer_id
- milk_type_id
- quantity
- start_date
- end_date
- status

Relationships

Customer

↓

Many Subscriptions

Business Rules

Customer may have multiple subscriptions.

Inactive subscriptions never generate deliveries.

Subscription history is immutable.

---

# Token Accounting

## Token Book

Purpose

Represents a physical token booklet.

Fields

- id
- customer_id
- token_number
- milk_type_id
- total_sheets
- issued_date
- status

Relationships

Customer

↓

Many Token Books

Business Rules

One customer may own multiple books.

Same token number may exist for different milk types.

Books are never deleted.

---

## Token Sheet

Purpose

Represents one detachable token.

Fields

- id
- token_book_id
- sheet_number
- status

Business Rules

Sheet numbers are unique inside a token book.

Status

Unused

Collected

Pending

Cancelled

Lost

---

## Token Ledger

Purpose

Maintains immutable token history.

Fields

- id
- token_sheet_id
- delivery_id
- operation
- timestamp

Business Rules

Ledger is append only.

Never update historical entries.

---

# Daily Operations

## Daily Delivery

Purpose

Represents actual milk delivery.

Fields

- id
- route_id
- customer_id
- delivery_date
- milk_type_id
- quantity
- delivery_status

Relationships

Route

↓

Many Deliveries

Business Rules

Delivery record never changes after completion.

Corrections create adjustment records.

---

## Delivery Exception

Purpose

Stores delivery deviations.

Examples

Customer absent

Holiday

Emergency delivery

Extra delivery

Business Rules

Exceptions never modify original delivery schedule.

---

# Finance

## Cash Sale

Purpose

Represents milk sold without subscription.

Fields

- id
- route_id
- customer_name
- milk_type_id
- quantity
- amount

Business Rules

Cash sales are independent of subscriptions.

---

## Payment

Purpose

Represents customer payment.

Fields

- id
- customer_id
- amount
- payment_method
- payment_date

Business Rules

Supports

Partial payment

Advance payment

Postpaid payment

Payment history is immutable.

---

# Reporting

## Route Reconciliation

Purpose

Stores daily balancing information.

Formula

Loaded Milk

=

Delivered Milk

+

Cash Sale

+

Returned Milk

Business Rules

Route cannot close until reconciliation balances.

---

# Future Modules

Version 2

- Mobile Application
- QR Tokens
- GPS Tracking
- Route Optimization
- Multi Branch
- Inventory
- Customer Notifications
- AI Analytics
- Predictive Demand

---

# AI Instructions

When creating new features

Always identify

1. Domain

2. Entity

3. Relationships

4. Business Rules

5. Required Foreign Keys

6. Migration Impact

Never create isolated tables.

Always integrate with the existing domain model.

Never violate business relationships.

Never bypass the Service layer.