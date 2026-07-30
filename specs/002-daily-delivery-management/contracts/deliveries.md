# API Contracts: Daily Deliveries

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Base URL
```
/api/v1/deliveries
```

---

## Endpoints

### POST / - Record Delivery

**Description**: Record a delivery for a customer

**Auth**: CHECKER

**Request Body**:
```json
{
    "session_id": 123,
    "customer_id": 10,
    "milk_type_id": 1,
    "delivered_quantity": 1,
    "delivery_status": "DELIVERED",
    "token_sheet_number": 3,
    "remarks": ""
}
```

**Response (201)**:
```json
{
    "id": 789,
    "session_id": 123,
    "customer_id": 10,
    "customer_name": "Mrs. Sharma",
    "milk_type_id": 1,
    "milk_type_name": "Full Cream 1L",
    "planned_quantity": 1,
    "delivered_quantity": 1,
    "delivery_status": "DELIVERED",
    "delivery_source": "PLANNED",
    "token_sheet_number": 3,
    "token_book_issue_id": 456,
    "created_at": "2026-01-27T09:30:00Z"
}
```

**Errors**:
- 400: Invalid token sheet
- 404: Session, customer, or milk type not found

---

### PUT /{delivery_id} - Update Delivery

**Description**: Update delivery status or details

**Auth**: CHECKER

**Request Body**:
```json
{
    "delivery_status": "PENDING_TOKEN",
    "delivered_quantity": 1,
    "remarks": "Will provide token tomorrow"
}
```

**Response (200)**:
```json
{
    "id": 789,
    "delivery_status": "PENDING_TOKEN",
    "delivered_quantity": 1,
    "remarks": "Will provide token tomorrow",
    "updated_at": "2026-01-27T09:35:00Z"
}
```

**Errors**:
- 400: Session not in editable status

---

### POST /unplanned - Add Unplanned Delivery

**Description**: Add delivery for customer not on schedule

**Auth**: CHECKER

**Request Body**:
```json
{
    "session_id": 123,
    "customer_id": 15,
    "milk_type_id": 1,
    "delivered_quantity": 1,
    "delivery_status": "DELIVERED",
    "registration_method": "TOKEN_SHEET",
    "token_sheet_number": 5,
    "reason": "Customer changed mind, was on vacation"
}
```

**Response (201)**:
```json
{
    "id": 790,
    "session_id": 123,
    "customer_id": 15,
    "customer_name": "Mrs. Gupta",
    "milk_type_id": 1,
    "milk_type_name": "Full Cream 1L",
    "planned_quantity": 0,
    "delivered_quantity": 1,
    "delivery_status": "DELIVERED",
    "delivery_source": "UNPLANNED",
    "token_sheet_number": 5,
    "token_book_issue_id": 457,
    "added_by": 2,
    "added_reason": "Customer changed mind, was on vacation",
    "created_at": "2026-01-27T09:40:00Z"
}
```

**Errors**:
- 400: Invalid token sheet
- 404: Session or customer not found

---

### POST /{delivery_id}/register-token - Register Token Sheet

**Description**: Register token sheet for a delivery

**Auth**: CHECKER

**Request Body**:
```json
{
    "token_sheet_number": 3,
    "acknowledged_warnings": ["NON_SEQUENTIAL_SHEET"],
    "acknowledgment_reason": "Customer confirmed #4 is lost"
}
```

**Response (200)**:
```json
{
    "delivery_id": 789,
    "sheet_registered": true,
    "token_book_issue_id": 456,
    "new_current_sheet": 8,
    "warnings_logged": 1,
    "message": "Token Sheet #3 registered. Warning logged for non-sequential sheet."
}
```

**Errors**:
- 400: Invalid token sheet
- 400: Sheet already used
- 404: Delivery not found

---

### POST /validate-token - Validate Token Sheet

**Description**: Validate token sheet before registration

**Auth**: CHECKER

**Request Body**:
```json
{
    "customer_id": 10,
    "milk_type_id": 1,
    "sheet_number": 5,
    "token_book_issue_id": 456
}
```

**Response (200)**:
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

---

### GET /customer/{customer_id}/token-status - Get Customer Token Status

**Description**: Get customer's token book status

**Auth**: CHECKER

**Response (200)**:
```json
{
    "customer_id": 10,
    "customer_name": "Mrs. Sharma",
    "token_books": [
        {
            "book_issue_id": 456,
            "book_number": "#SM-001",
            "milk_type": "Full Cream 1L",
            "issue_date": "2026-01-01",
            "status": "ACTIVE",
            "sheets_used": 20,
            "sheets_remaining": 10,
            "is_old_book": true
        },
        {
            "book_issue_id": 457,
            "book_number": "#SM-002",
            "milk_type": "Full Cream 1L",
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

### PUT /{delivery_id}/edit - Edit Previous Delivery

**Description**: Edit delivery from a reopened session

**Auth**: OWNER only

**Request Body**:
```json
{
    "delivery_status": "NOT_DELIVERED",
    "return_token_sheet": true,
    "reason": "Customer said no milk, partner forgot and delivered"
}
```

**Response (200)**:
```json
{
    "delivery_id": 789,
    "old_status": "DELIVERED",
    "new_status": "NOT_DELIVERED",
    "token_sheet_returned": true,
    "token_book_issue_id": 456,
    "sheet_number": 3,
    "new_current_sheet": 7,
    "message": "Delivery corrected. Token sheet #3 returned to customer."
}
```

**Errors**:
- 403: Only Owner can edit
- 400: Session not in editable status
- 400: Cannot return token for non-delivered status

---

### GET /{delivery_id}/warnings - Get Delivery Warnings

**Description**: Get warnings for a delivery

**Auth**: CHECKER

**Response (200)**:
```json
{
    "delivery_id": 789,
    "warnings": [
        {
            "id": 1,
            "warning_code": "NON_SEQUENTIAL_SHEET",
            "warning_message": "Sheet #5 skips ahead. Sheet #4 not yet used.",
            "sheet_number": 5,
            "expected_sheet": 4,
            "acknowledged_by": 2,
            "acknowledged_at": "2026-01-27T09:30:00Z"
        }
    ]
}
```

---

### GET /session/{session_id} - Get Session Deliveries

**Description**: Get all deliveries for a session

**Auth**: CHECKER

**Query Parameters**:
- `status` (optional): Filter by delivery status
- `skip` (default: 0): Pagination offset
- `limit` (default: 100): Pagination limit

**Response (200)**:
```json
{
    "session_id": 123,
    "deliveries": [
        {
            "id": 789,
            "customer_id": 10,
            "customer_name": "Mrs. Sharma",
            "milk_type_name": "Full Cream 1L",
            "planned_quantity": 1,
            "delivered_quantity": 1,
            "delivery_status": "DELIVERED",
            "delivery_source": "PLANNED",
            "token_sheet_number": 3
        }
    ],
    "total": 10
}
```
