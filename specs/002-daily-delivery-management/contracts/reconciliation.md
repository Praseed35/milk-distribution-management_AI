# API Contracts: Reconciliation

**Date**: 2026-01-27
**Feature**: 002-daily-delivery-management

## Base URL
```
/api/v1/deliveries/sessions/{session_id}/reconciliation
```

---

## Endpoints

### POST /submit - Submit Reconciliation Details

**Description**: Checker submits final reconciliation details

**Auth**: CHECKER

**Request Body**:
```json
{
    "total_cash_collected": 150.00,
    "cash_sales": [
        {
            "customer_name": "Guest 1",
            "quantity": 0.5,
            "amount": 25.00
        }
    ],
    "returned_milk": 0.5,
    "returned_reasons": [
        {
            "customer_id": 10,
            "quantity": 0.5,
            "reason": "Customer on vacation"
        }
    ],
    "token_sheets_collected": [
        {
            "customer_id": 10,
            "milk_type_id": 1,
            "sheets": [1, 2, 3]
        }
    ],
    "remarks": "All accounted for"
}
```

**Response (200)**:
```json
{
    "session_id": 123,
    "reconciliation": {
        "loaded_milk": 5.0,
        "token_registered": 3.0,
        "cash_sales": 1.0,
        "returned_milk": 1.0,
        "total_accounted": 5.0,
        "difference": 0.0,
        "is_balanced": true,
        "status": "BALANCED"
    },
    "message": "Reconciliation submitted successfully"
}
```

**Errors**:
- 400: Reconciliation data invalid

---

### GET / - Get Current Reconciliation

**Description**: Get current reconciliation status

**Auth**: CHECKER

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
    "status": "BALANCED",
    "last_updated": "2026-01-27T10:30:00Z"
}
```

---

### GET /summary - Get Session Summary

**Description**: Get delivery summary for the session

**Auth**: CHECKER

**Response (200)**:
```json
{
    "session_id": 123,
    "route_name": "Route 1 - Downtown",
    "delivery_date": "2026-01-27",
    "shift": "MORNING",
    "delivery_partner": "Suresh Babu",
    "summary": {
        "total_customers": 10,
        "delivered_with_token": 8,
        "pending_token": 1,
        "cash_sales": 1,
        "not_delivered": 0,
        "unplanned_deliveries": 1
    },
    "milk_summary": {
        "loaded_liters": 5.0,
        "token_liters": 3.0,
        "cash_liters": 1.0,
        "returned_liters": 1.0,
        "total_liters_accounted": 5.0
    },
    "cash_summary": {
        "total_cash_collected": 150.00,
        "cash_sales_count": 1
    },
    "token_collection": {
        "sheets_collected": 3,
        "pending_sheets": 1
    }
}
```

---

### GET /customers - Get All Customer Status

**Description**: Get status of all customers in session

**Auth**: CHECKER

**Response (200)**:
```json
{
    "session_id": 123,
    "customers": [
        {
            "customer_id": 10,
            "customer_name": "Mrs. Sharma",
            "phone": "9876543210",
            "address": "123 Main St",
            "milk_type": "Full Cream 1L",
            "planned_quantity": 1,
            "status": "DELIVERED",
            "token_sheet": 3,
            "cash_paid": 0,
            "is_on_schedule": true
        },
        {
            "customer_id": 12,
            "customer_name": "Mr. Verma",
            "phone": "9876543211",
            "address": "456 Oak Ave",
            "milk_type": "Toned Milk 500ml",
            "planned_quantity": 1,
            "status": "CASH_SALE",
            "token_sheet": null,
            "cash_paid": 25.00,
            "is_on_schedule": true
        }
    ],
    "total": 10
}
```

---

### POST /validate - Validate Reconciliation

**Description**: Validate if reconciliation is possible

**Auth**: CHECKER

**Response (200)**:
```json
{
    "can_close": true,
    "is_balanced": true,
    "issues": []
}
```

**Response with issues (200)**:
```json
{
    "can_close": false,
    "is_balanced": false,
    "issues": [
        {
            "code": "MILK_SHORTAGE",
            "message": "Milk shortage: 0.2 liters",
            "severity": "ERROR"
        },
        {
            "code": "PENDING_TOKENS",
            "message": "1 customer has pending token sheet",
            "severity": "WARNING"
        }
    ]
}
```

---

### POST /cash-sales - Add Cash Sale

**Description**: Record a cash sale during reconciliation

**Auth**: CHECKER

**Request Body**:
```json
{
    "customer_name": "Guest 1",
    "customer_phone": null,
    "milk_type_id": 1,
    "quantity": 0.5,
    "amount": 25.00,
    "payment_method": "CASH"
}
```

**Response (201)**:
```json
{
    "id": 1,
    "session_id": 123,
    "customer_name": "Guest 1",
    "milk_type_name": "Full Cream 1L",
    "quantity": 0.5,
    "amount": 25.00,
    "payment_method": "CASH",
    "created_at": "2026-01-27T10:30:00Z"
}
```

---

### DELETE /cash-sales/{cash_sale_id} - Remove Cash Sale

**Description**: Remove a cash sale

**Auth**: CHECKER

**Response (200)**:
```json
{
    "message": "Cash sale removed successfully"
}
```

---

## Reconciliation Flow

### Step 1: Checker Enters Data
- Total cash collected
- List of cash sales with details
- Returned milk (undelivered)
- Reasons for returned milk
- Token sheets collected (automatic from token registration)

### Step 2: System Calculates
```
Total Accounted = Token Milk + Cash Milk + Returned Milk
Difference = Loaded Milk - Total Accounted
```

### Step 3: Validation
- If Difference = 0: BALANCED (can close)
- If Difference ≠ 0: UNBALANCED (shows shortage/overage)

### Step 4: Close Session
- Only allowed if BALANCED
- Creates immutable record

---

## Error Handling

| Error Code | Description | Severity |
|------------|-------------|----------|
| MILK_SHORTAGE | More milk loaded than accounted for | ERROR |
| MILK_OVERAGE | More milk accounted for than loaded | ERROR |
| PENDING_TOKENS | Some customers haven't returned tokens | WARNING |
| RECONCILIATION_MISMATCH | Reconciliation totals don't match | ERROR |
