# API Contracts: Delivery Sessions

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Base URL
```
/api/v1/deliveries/sessions
```

---

## Endpoints

### POST / - Create Delivery Session

**Description**: Generate delivery list for a route/shift/date combination

**Auth**: OWNER, CHECKER

**Request Body**:
```json
{
    "route_id": 1,
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "delivery_partner_id": 5
}
```

**Response (201)**:
```json
{
    "id": 123,
    "route_id": 1,
    "route_name": "Route 1 - Downtown",
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "delivery_partner_id": 5,
    "delivery_partner_name": "Suresh Babu",
    "status": "PLANNED",
    "total_milk_loaded": 0,
    "reconciliation_status": "PENDING",
    "created_at": "2026-01-27T04:00:00Z"
}
```

**Errors**:
- 400: Session already exists for this route/date/shift
- 404: Route or employee not found

---

### GET / - List Delivery Sessions

**Description**: List all delivery sessions with filters

**Auth**: OWNER, CHECKER

**Query Parameters**:
- `route_id` (optional): Filter by route
- `delivery_date` (optional): Filter by date
- `shift` (optional): Filter by shift
- `status` (optional): Filter by status
- `skip` (default: 0): Pagination offset
- `limit` (default: 100): Pagination limit

**Response (200)**:
```json
{
    "sessions": [
        {
            "id": 123,
            "route_id": 1,
            "route_name": "Route 1 - Downtown",
            "delivery_date": "2026-01-27",
            "shift": "MORNING",
            "delivery_partner_name": "Suresh Babu",
            "status": "COMPLETED",
            "total_milk_loaded": 5.0,
            "reconciliation_status": "BALANCED"
        }
    ],
    "total": 50
}
```

---

### GET /{session_id} - Get Session Detail

**Description**: Get session with all deliveries

**Auth**: OWNER, CHECKER

**Response (200)**:
```json
{
    "id": 123,
    "route_id": 1,
    "route_name": "Route 1 - Downtown",
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "delivery_partner_id": 5,
    "delivery_partner_name": "Suresh Babu",
    "status": "COMPLETED",
    "total_milk_loaded": 5.0,
    "reconciliation_status": "BALANCED",
    "reopen_count": 0,
    "deliveries": [
        {
            "id": 456,
            "customer_id": 10,
            "customer_name": "Mrs. Sharma",
            "milk_type_name": "Full Cream 1L",
            "planned_quantity": 1,
            "delivered_quantity": 1,
            "delivery_status": "DELIVERED",
            "token_sheet_number": 3
        }
    ],
    "created_at": "2026-01-27T04:00:00Z",
    "updated_at": "2026-01-27T10:00:00Z"
}
```

---

### POST /{session_id}/start - Start Session

**Description**: Record milk dispatch and start delivery

**Auth**: OWNER, CHECKER

**Request Body**:
```json
{
    "total_milk_loaded": 5.0
}
```

**Response (200)**:
```json
{
    "id": 123,
    "status": "STARTED",
    "total_milk_loaded": 5.0
}
```

**Errors**:
- 400: Session not in PLANNED status

---

### POST /{session_id}/dispatch - Record Dispatch

**Description**: Record milk dispatched (alternative to start)

**Auth**: OWNER, CHECKER

**Request Body**:
```json
{
    "total_milk_loaded": 5.0
}
```

**Response (200)**:
```json
{
    "id": 123,
    "status": "STARTED",
    "total_milk_loaded": 5.0
}
```

**Errors**:
- 400: Dispatch already recorded

---

### POST /{session_id}/close - Close Session

**Description**: Close session after reconciliation

**Auth**: OWNER, CHECKER

**Response (200)**:
```json
{
    "id": 123,
    "status": "CLOSED",
    "reconciliation_status": "BALANCED",
    "closed_at": "2026-01-27T10:30:00Z"
}
```

**Errors**:
- 400: Reconciliation not balanced
- 400: Not all customers processed

---

### POST /{session_id}/reopen - Reopen Session

**Description**: Reopen closed session for editing

**Auth**: OWNER only

**Request Body**:
```json
{
    "reason": "Customer complaint - token sheet return"
}
```

**Response (200)**:
```json
{
    "id": 123,
    "status": "COMPLETED",
    "reopened_by": 1,
    "reopened_at": "2026-01-28T10:00:00Z",
    "reopen_count": 1
}
```

**Errors**:
- 403: Only Owner can reopen
- 400: Session not in CLOSED status

---

### GET /{session_id}/checklist - Get Delivery Checklist

**Description**: Get checklist for delivery partner

**Auth**: OWNER, CHECKER, DELIVERY_PARTNER

**Response (200)**:
```json
{
    "session_id": 123,
    "route_name": "Route 1 - Downtown",
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "total_expected": 10,
    "customers": [
        {
            "customer_id": 10,
            "customer_name": "Mrs. Sharma",
            "address": "123 Main St",
            "phone": "9876543210",
            "milk_type": "Full Cream 1L",
            "quantity": 1
        }
    ]
}
```

---

### GET /{session_id}/reconciliation - Get Reconciliation

**Description**: Get reconciliation details

**Auth**: OWNER, CHECKER

**Response (200)**:
```json
{
    "session_id": 123,
    "loaded_milk": 5.0,
    "token_registered": 3.0,
    "cash_sales": 1.0,
    "returned_milk": 1.0,
    "total_accounted": 5.0,
    "difference": 0.0,
    "is_balanced": true,
    "status": "BALANCED"
}
```

---

### GET /{session_id}/report - Get Session Report

**Description**: Generate comprehensive session report

**Auth**: OWNER, CHECKER

**Response (200)**:
```json
{
    "session_id": 123,
    "route_name": "Route 1 - Downtown",
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "summary": {
        "total_customers": 10,
        "delivered": 8,
        "pending_token": 1,
        "cash_sale": 1,
        "not_delivered": 0
    },
    "milk_summary": {
        "loaded": 5.0,
        "token_registered": 3.0,
        "cash_sales": 1.0,
        "returned": 1.0
    },
    "token_collection": [...],
    "pending_tokens": [...],
    "cash_sales": [...],
    "edit_history": [...]
}
```

---

### GET /{session_id}/edit-history - Get Edit History

**Description**: Get all edits for a session

**Auth**: OWNER

**Response (200)**:
```json
{
    "session_id": 123,
    "edits": [
        {
            "edit_id": 1,
            "delivery_id": 456,
            "customer_name": "Mrs. Sharma",
            "edit_type": "TOKEN_RETURN",
            "old_value": {"status": "DELIVERED", "token_sheet": 3},
            "new_value": {"status": "NOT_DELIVERED", "token_sheet": null},
            "reason": "Customer said no milk",
            "edited_by": "Owner (Rajesh)",
            "edited_at": "2026-01-28T10:00:00Z"
        }
    ],
    "total_edits": 1
}
```
