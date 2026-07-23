# Project Context

## Project Name

Milk Distribution Management System

---

# Purpose

The Milk Distribution Management System is an Enterprise Resource Planning (ERP) application designed for traditional milk distribution businesses.

The objective is to digitize daily operations while preserving the existing business workflow.

This project is **not** a generic inventory or e-commerce system. It models the real operational processes of a milk distribution company.

The software should adapt to the business—not force the business to change.

---

# Business Overview

Traditional milk distributors manage hundreds of customers using physical token books and manually maintained records.

Daily operations include:

- Planning milk allocation
- Delivering milk
- Collecting tokens
- Recording cash sales
- Processing payments
- Reconciling delivered milk
- Generating reports

The ERP digitizes these operations while maintaining complete historical records and business accuracy.

---

# Business Objectives

The system should help the business:

- Reduce manual paperwork
- Improve operational efficiency
- Track deliveries accurately
- Maintain customer subscriptions
- Record token usage
- Handle cash sales
- Support payment tracking
- Perform route reconciliation
- Generate operational and financial reports

---

# Core Business Modules

The project consists of the following domains.

### Authentication

- User login
- JWT authentication
- Role-based authorization

---

### Customer Management

Manage customer information.

Includes

- Customer registration
- Contact information
- Route assignment
- Customer status

---

### Route Management

Manage milk delivery routes.

Each customer belongs to one route.

Routes are assigned to delivery employees.

---

### Employee Management

Manage employees responsible for deliveries.

Includes

- Delivery staff
- Leave requests
- Shift assignments (future)

---

### Milk Allocation

Plan daily milk quantities before delivery.

Supports allocation based on:

- Customer subscriptions
- Manual adjustments
- Business exceptions

---

### Token Book Management

Customers purchase physical token books.

Each token represents milk collected during delivery.

The ERP records token usage but does not replace the physical token system.

---

### Cash Sales

Milk can be sold directly without subscriptions.

Cash sales must be recorded separately from subscription deliveries.

---

### Reconciliation

Every route must balance.

Example:

Loaded Milk

=

Delivered Milk

+

Cash Sales

+

Returned Milk

Routes should not be closed until reconciliation is complete.

---

### Reporting

Generate reports for:

- Customers
- Routes
- Deliveries
- Cash sales
- Milk allocation
- Reconciliation
- Business performance

---

# Business Philosophy

The project models real business operations.

The software must preserve existing workflows whenever possible.

Business correctness is more important than implementation convenience.

---

# Architecture Philosophy

The project follows a layered architecture.

```
HTTP Request
      │
      ▼
Router
      │
      ▼
Dependency Injection
      │
      ▼
Service
      │
      ▼
SQLAlchemy ORM
      │
      ▼
PostgreSQL
```

Business logic belongs inside the Service layer.

Routers should only:

- Accept requests
- Validate input
- Call services
- Return responses

---

# Technology Stack

Backend

- Python
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Alembic
- Pydantic v2

Frontend (Planned)

- React
- TypeScript

---

# Development Goals

The project should be:

- Modular
- Maintainable
- Testable
- Scalable
- Easy to extend

Future modules should integrate without major architectural changes.

---

# Future Enhancements

Planned features include:

- Mobile application
- AI-powered analytics
- Route optimization
- QR code token system
- Customer notifications
- Multi-branch support
- Business intelligence dashboards

---

# AI Responsibilities

Before implementing any feature:

1. Understand the business purpose.
2. Identify the affected module.
3. Reuse existing services and utilities.
4. Follow the current project architecture.
5. Preserve backward compatibility.
6. Avoid duplicate logic.

When uncertain, inspect the existing implementation before creating new code.

The AI should always prioritize business correctness, maintainability, and consistency over rapid code generation.