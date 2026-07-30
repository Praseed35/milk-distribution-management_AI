# API Contracts: Reports and Analytics

**Date**: 2026-07-30 | **Phase**: Phase 1 (Design & Contracts)

**Base URL**: All endpoints are prefi xed with `/reports` and require authentication via `Authorization: Bearer <token>`.

**Content Types**:
- JSON: `Accept: application/json` (default)
- CSV: `Accept: text/csv` or `?format=csv`

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient role permissions
- `422 Unprocessable Entity`: Invalid parameter values

---

## Endpoint: Route Delivery Report

```
GET /reports/route-delivery
```

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_id` | int | null (all) | Filter by route |
| `preset` | string | null | Date preset override |
| `from_date` | date | null | Start date (ISO 8601) |
| `to_date` | date | null | End date (ISO 8601) |
| `shift` | string | null | MORNING or EVENING |
| `group_by` | string | "route" | route, day, week, month |
| `format` | string | "json" | json or csv |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page |

**Roles**: OWNER, ADMIN, CHECKER, DELIVERY_PARTNER (own route only)

**Response (JSON)**:
```json
{
  "data": [
    {
      "route_id": 1,
      "route_name": "Route A",
      "route_code": "R001",
      "session_count": 30,
      "delivery_count": 450,
      "total_loaded_quantity": 900.0,
      "total_delivered_quantity": 885.0,
      "total_cash_collected": 500.0,
      "total_token_registered": 800.0,
      "total_returned_quantity": 10.0,
      "shortage_surplus": 5.0,
      "is_balanced": false
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50,
  "generated_at": "2026-07-30T10:30:00"
}
```

**Response (CSV)**: Same field names as JSON, comma-separated, with header row.

---

## Endpoint: Revenue Report

```
GET /reports/revenue
```

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset` | string | null | Date preset override |
| `from_date` | date | null | Start date (ISO 8601) |
| `to_date` | date | null | End date (ISO 8601) |
| `route_id` | int | null | Filter by route |
| `milk_type_id` | int | null | Filter by milk type |
| `payment_mode` | string | null | CASH, UPI, CARD, CHEQUE, BANK_TRANSFER |
| `group_by` | string | "source" | source, payment_mode, route, milk_type |
| `format` | string | "json" | json or csv |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page |

**Roles**: OWNER only (revenue data is sensitive)

---

## Endpoint: Collection Efficiency

```
GET /reports/collection-efficiency
```

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset` | string | null | Date preset override |
| `from_date` | date | null | Start date |
| `to_date` | date | null | End date |
| `route_id` | int | null | Filter by route |
| `min_outstanding` | float | null | Min outstanding to filter (e.g., 1000) |
| `format` | string | "json" | json or csv |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page |

**Roles**: OWNER, ADMIN (operational data)

---

## Endpoint: Customer Consumption

```
GET /reports/customer/{customer_id}/consumption
```

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `customer_id` | int | Customer ID |

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset` | string | null | Date preset override |
| `from_date` | date | null | Start date |
| `to_date` | date | null | End date |
| `group_by` | string | "day" | day, week, month |
| `format` | string | "json" | json or csv |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page |

**Roles**: OWNER, ADMIN (customer data), CHECKER (read-only)

---

## Endpoint: Token Book Utilization

```
GET /reports/token-utilization
```

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `route_id` | int | null | Filter by route |
| `customer_id` | int | null | Filter by customer |
| `low_threshold` | int | 20 | % threshold for "needs replacement" |
| `format` | string | "json" | json or csv |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page |

**Roles**: OWNER, ADMIN

---

## Endpoint: Operational Dashboard

```
GET /reports/dashboard
```

**Query Parameters**: None (always shows today's data)

**Roles**: OWNER, ADMIN, CHECKER

---

## Endpoint: CSV Export (Generic)

All report endpoints support CSV export by passing `?format=csv` query parameter or `Accept: text/csv` header.

**Response Headers**:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="route-delivery-report-2026-07-30.csv"
```

**CSV Format Rules**:
- First row is header (field names matching JSON keys)
- Subsequent rows are data
- String values with commas are quoted
- Date/datetime values use ISO 8601 format
- Currency values use decimal format (no currency symbol)

---

## Endpoint: Force Cache Refresh

All report endpoints support cache bypass via `?refresh=true` query parameter.

```
GET /reports/route-delivery?refresh=true
```

When `refresh=true`, the system bypasses any cached data and recomputes from the database.
