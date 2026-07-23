# Authentication Flow

## Purpose

This document defines the authentication and authorization architecture of the Milk Distribution Management System.

Every AI assistant must follow these rules when implementing authentication, authorization, or protected endpoints.

Authentication must remain centralized, secure, and consistent across the application.

---

# Authentication Architecture

The project uses

- JWT Authentication
- FastAPI Dependency Injection
- Password Hashing
- Role-Based Authorization

Authentication flow

```
Client

↓

Login Request

↓

Router

↓

Auth Service

↓

Verify Credentials

↓

Generate JWT

↓

Return Token

↓

Client Stores Token

↓

Authenticated Requests

↓

JWT Validation

↓

Current User

↓

Protected Endpoint
```

---

# Components

Authentication is implemented using

```
app/core/auth.py

app/core/security.py

app/dependencies.py

app/routers/auth.py

app/services/auth_service.py
```

Each component has one responsibility.

---

# Responsibilities

## Router

Responsible for

- Login endpoint
- Refresh endpoint
- Logout endpoint (future)

Never

- Verify passwords
- Generate JWT
- Access database directly

---

## Auth Service

Responsible for

- User lookup
- Password verification
- Token generation
- Token refresh
- Business validation

Never

- Return HTTP responses
- Define routes

---

## Security Module

Responsible for

- Password hashing
- Password verification
- JWT encoding
- JWT decoding

Business logic should never exist here.

---

## Dependencies

Responsible for

- Extracting JWT
- Validating JWT
- Loading current user
- Role verification

Dependencies should be reusable.

---

# Login Flow

```
User

↓

Username & Password

↓

Router

↓

Auth Service

↓

Find User

↓

Verify Password

↓

Generate JWT

↓

Return Access Token
```

If authentication fails

↓

Return

401 Unauthorized

---

# Password Rules

Passwords must

- Never be stored in plain text.
- Always be hashed.
- Be verified using the security module.

Never compare passwords manually.

Always use the existing helper functions.

---

# JWT Rules

JWT should contain

- User ID
- Username
- Role
- Expiration

Never place

- Password
- Phone Number
- Personal Information

inside JWT payload.

---

# Protected Routes

Protected routes require authentication.

Example

```
Authorization

Bearer <access_token>
```

Request Flow

```
Request

↓

JWT Validation

↓

Current User

↓

Role Validation

↓

Router

↓

Service
```

---

# Current User

Every protected endpoint should receive

```
current_user
```

through dependency injection.

Never manually parse JWT inside routers.

---

# Authorization

The project uses Role-Based Access Control.

Current roles

- Owner
- Checker
- Delivery Partner

Future roles may be added without changing authentication architecture.

---

# Owner Permissions

Owner can

- Manage users
- Manage routes
- Manage customers
- Issue token books
- Record payments
- Manage employees
- Generate reports
- Configure system

---

# Checker Permissions

Checker can

- Verify collected tokens
- Verify deliveries
- Verify reconciliation
- View operational reports

Checker should not modify business history.

---

# Delivery Partner Permissions

Delivery Partner can

- View assigned routes
- Record deliveries
- Record cash sales
- Submit reconciliation
- View allocation

Delivery Partner should not access other routes.

---

# Authentication Failure

Possible failures

Invalid username

↓

401

Invalid password

↓

401

Expired token

↓

401

Invalid signature

↓

401

Inactive user

↓

403

Insufficient permissions

↓

403

---

# Token Refresh

Workflow

```
Expired Access Token

↓

Refresh Endpoint

↓

Validate Refresh Token

↓

Generate New Access Token

↓

Return Token
```

Refresh tokens should only be used to obtain new access tokens.

---

# Logout

Current implementation may be stateless.

Future implementation may

- blacklist tokens
- revoke refresh tokens

AI should preserve compatibility.

---

# Security Rules

Always

- Validate JWT
- Verify user status
- Check permissions
- Use HTTPS in production
- Use secure secrets

Never

- Hardcode secrets
- Disable authentication
- Skip role validation
- Trust client input

---

# Adding Protected Endpoints

Every protected endpoint should follow

```
Router

↓

Authentication Dependency

↓

Role Validation

↓

Service

↓

Business Logic

↓

Response
```

Never bypass authentication.

---

# Error Responses

Authentication errors

401 Unauthorized

Authorization errors

403 Forbidden

Never expose

- Stack traces
- Internal exception messages
- JWT secrets

---

# AI Instructions

Before creating authentication code

✔ Reuse existing security helpers

✔ Use dependency injection

✔ Validate JWT

✔ Verify user status

✔ Check roles

✔ Reuse auth service

Never

- Create a second authentication system.
- Store passwords in plain text.
- Parse JWT manually in routers.
- Duplicate security utilities.
- Bypass authorization checks.

---

# Golden Rule

Authentication verifies **who the user is**.

Authorization determines **what the user is allowed to do**.

Keep these responsibilities separate.

Always use the existing authentication flow instead of introducing new security patterns.