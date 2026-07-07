# Chapter 8 – API Specification

---

# 1. Introduction

The Milk Distribution ERP exposes a RESTful API developed using FastAPI. The API provides communication between the frontend, mobile applications, and backend services.

Each endpoint follows REST principles and returns JSON responses.

Authentication is performed using JWT tokens, and protected endpoints require a valid access token.

This chapter documents every API endpoint, including its purpose, request parameters, request body, response format, business logic, validations, and possible exceptions.

---

# 2. API Standards

All APIs follow the same standards.

**Base URL**

```
/api/v1
```

**Request Format**

```
JSON
```

**Response Format**

```
JSON
```

**Authentication**

Bearer JWT Token

**HTTP Methods**

* GET
* POST
* PUT
* DELETE

---

# 3. Response Format

Successful Response

```json
{
    "success": true,
    "message": "Customer created successfully.",
    "data": {}
}
```

Error Response

```json
{
    "success": false,
    "message": "Primary phone already exists."
}
```

---

# 4. Authentication Module

## Login

**Endpoint**

```
POST /auth/login
```

### Purpose

Authenticates a user and returns JWT tokens.

### Request Body

* username
* password

### Successful Response

Returns:

* Access Token
* Refresh Token
* User Information

### Possible Errors

* Invalid Username
* Invalid Password
* Inactive User

---

## Refresh Token

```
POST /auth/refresh
```

Purpose

Generate a new access token.

---

## Logout

```
POST /auth/logout
```

Purpose

Terminate the user session.

---

# 5. Customer Module

## Create Customer

```
POST /customers
```

### Purpose

Creates a new customer.

### Request Body

* Customer Name
* Primary Phone
* Alternate Phone
* Address
* Route
* Remarks

### Business Logic

* Verify Route Exists
* Verify Route Active
* Verify Unique Phone Number
* Generate Customer Code
* Save Customer

### Response

Returns newly created customer.

### Possible Errors

* Route Not Found
* Inactive Route
* Duplicate Phone Number
* Same Phone Number

---

## Get All Customers

```
GET /customers
```

### Purpose

Returns all active customers.

---

## Get Customer By ID

```
GET /customers/{customer_id}
```

### Purpose

Returns one customer.

### Possible Errors

* Customer Not Found

---

## Update Customer

```
PUT /customers/{customer_id}
```

### Purpose

Updates customer information.

### Business Rules

* Customer must exist
* Route must exist
* Route must be active
* Primary phone must remain unique

---

## Delete Customer

```
DELETE /customers/{customer_id}
```

### Purpose

Soft deletes a customer.

### Business Logic

Set

```
is_active = false
```

---

# 6. Route Module

Document every Route endpoint using the same format.

Examples

* Create Route
* Update Route
* Delete Route
* Get Route
* List Routes

---

# 7. Milk Type Module

Document:

* Create Milk Type
* Update Milk Type
* Delete Milk Type
* List Milk Types

---

# 8. Subscription Module

Document:

* Create Subscription
* Update Subscription
* Pause Subscription
* Resume Subscription
* Cancel Subscription

---

# 9. Delivery Exception Module

Document:

* Add Exception
* Update Exception
* Delete Exception
* Get Exception

---

# 10. Token Management Module

Document:

* Create Token Identity
* Issue Token Book
* Register Token
* Pending Token
* Advance Token
* Token Ledger
* Token History

---

# 11. Daily Delivery Module

Document:

* Generate Daily Route
* Get Today's Route
* Add Unplanned Delivery
* Register Delivery
* Register Cash Sale
* Register Returned Milk
* Reconciliation
* Close Route

---

# 12. Payment Module

Document:

* Record Payment
* Outstanding Payments
* Payment History
* Token Book Payment

---

# 13. Reports Module

Document:

* Daily Report
* Route Report
* Customer Report
* Token Report
* Outstanding Report
* Dashboard Report

---

# 14. Error Codes

Standard HTTP Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Created               |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 409  | Conflict              |
| 422  | Validation Error      |
| 500  | Internal Server Error |

---

# 15. API Security

Every protected endpoint validates:

* JWT Token
* User Status
* User Role

Unauthorized requests are rejected.

---

# 16. Conclusion

The API Specification provides a complete reference for all backend services in the Milk Distribution ERP. Each endpoint is documented with its purpose, request and response formats, business logic, validation rules, and possible exceptions. This documentation serves as the primary reference for frontend developers, backend developers, testers, and future system integrations.
