# Naming Conventions

## Purpose

This document defines the naming standards for the Milk Distribution Management System.

Consistent naming improves readability, maintainability, and AI-generated code quality.

Every AI assistant must follow these conventions.

---

# General Principles

Names should be

- Clear
- Descriptive
- Consistent
- Business-oriented

Avoid abbreviations unless they are universally understood.

Good

```
customer
delivery_partner
milk_allocation
cash_sale
```

Bad

```
cust
dp
alloc
cs
```

---

# Files

Use

snake_case

Examples

```
customer.py

customer_service.py

cash_sale.py

milk_allocation.py

token_book.py
```

Never

```
Customer.py

CustomerService.py

Customer-Service.py
```

---

# Directories

Use

snake_case

Examples

```
routers

services

schemas

exceptions

constants
```

---

# Classes

Use

PascalCase

Examples

```python
Customer

Route

TokenBook

CashSale

CustomerService

CustomerCreate
```

Never

```python
customer

customer_service

CUSTOMER
```

---

# Variables

Use

snake_case

Good

```python
customer

route

delivery_date

cash_sale
```

Bad

```python
Customer

customerName

cust
```

---

# Functions

Function names should describe an action.

Examples

```python
create_customer()

update_customer()

issue_token_book()

calculate_route_balance()

record_cash_sale()
```

Avoid

```python
do_work()

process()

run()

execute()
```

---

# Boolean Variables

Boolean names should answer a yes/no question.

Good

```python
is_active

is_verified

has_token_book

is_reconciled
```

Bad

```python
active

verified

token

status
```

---

# Constants

Use

UPPER_CASE

Examples

```python
DEFAULT_PAGE_SIZE

MAX_TOKEN_SHEETS

JWT_EXPIRATION_MINUTES
```

Never

```python
DefaultPageSize

maxToken

tokenLimit
```

---

# Enums

Use

PascalCase

Example

```python
class UserRole(Enum):

    OWNER

    CHECKER

    DELIVERY_PARTNER
```

---

# Database Tables

Plural

snake_case

Examples

```
customers

routes

employees

cash_sales

token_books

milk_allocations
```

---

# Database Columns

snake_case

Examples

```
customer_name

phone_number

route_id

created_at

updated_at
```

---

# Primary Keys

Always

```
id
```

Example

```
customers.id

routes.id
```

---

# Foreign Keys

Use

```
<entity>_id
```

Examples

```
customer_id

route_id

employee_id

token_book_id
```

---

# Routers

Router filenames

```
customer.py

route.py

employee.py

cash_sale.py
```

Router variables

```python
router = APIRouter()
```

Never

```python
customer_router = APIRouter()
```

---

# Services

Filename

```
customer_service.py
```

Class

```python
CustomerService
```

Methods

```python
create_customer()

update_customer()

delete_customer()

get_customer()
```

---

# Schemas

Request schemas

```python
CustomerCreate

CustomerUpdate

CustomerLogin
```

Response schemas

```python
CustomerResponse

CustomerListResponse

TokenBookResponse
```

Avoid vague names like

```python
CustomerData

CustomerDTO

CustomerInfo
```

---

# Exceptions

Class names

```python
CustomerNotFound

RouteInactive

TokenAlreadyUsed

DuplicateCustomer

InvalidMilkType
```

Avoid

```python
CustomerError

Error1

NotFound
```

---

# API Endpoints

Use plural resources.

Good

```
GET    /customers

GET    /customers/{id}

POST   /customers

PUT    /customers/{id}

DELETE /customers/{id}
```

Avoid

```
/getCustomer

/createCustomer

/deleteCustomer
```

---

# Response Variables

Good

```python
customer

customers

token_book

cash_sale
```

Avoid

```python
obj

result

item

data1
```

---

# Date & Time Fields

Use explicit names.

Examples

```
created_at

updated_at

delivery_date

payment_date

issued_at
```

Avoid

```
date

time

timestamp
```

---

# AI Checklist

Before introducing a new name

✔ Is it descriptive?

✔ Does it match existing conventions?

✔ Is it business-oriented?

✔ Does it avoid abbreviations?

✔ Does it use the correct casing?

Never

- Mix camelCase and snake_case.
- Use cryptic abbreviations.
- Invent inconsistent file names.
- Create duplicate names for different concepts.

---

# Golden Rule

A developer should understand the purpose of a file, class, function, or variable simply by reading its name.

Choose names that reflect the business domain, not implementation details.