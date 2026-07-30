from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class DeliverySessionCreate(BaseModel):

    route_id: int

    delivery_date: date

    shift: str = Field(
        pattern="^(MORNING|EVENING)$"
    )

    delivery_partner_id: int


class DeliverySessionUpdate(BaseModel):

    status: str | None = Field(
        default=None,
        pattern="^(PLANNED|STARTED|COMPLETED|CLOSED)$"
    )

    total_milk_loaded: Decimal | None = Field(
        default=None,
        ge=0
    )

    total_cash_sales: Decimal | None = Field(
        default=None,
        ge=0
    )

    total_returned_milk: Decimal | None = Field(
        default=None,
        ge=0
    )

    reconciliation_status: str | None = Field(
        default=None,
        pattern="^(BALANCED|UNBALANCED|PENDING)$"
    )


class DeliverySessionDispatch(BaseModel):

    total_milk_loaded: Decimal = Field(
        gt=0
    )


class DeliverySessionReopen(BaseModel):

    reason: str = Field(
        min_length=1,
        max_length=500
    )


class DailyDeliveryResponse(BaseModel):

    id: int

    customer_id: int

    customer_name: str | None = None

    milk_type_name: str | None = None

    planned_quantity: int

    delivered_quantity: int

    delivery_status: str

    delivery_source: str

    token_sheet_number: int | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliverySessionResponse(BaseModel):

    id: int

    route_id: int

    route_name: str | None = None

    delivery_date: date

    shift: str

    delivery_partner_id: int

    delivery_partner_name: str | None = None

    status: str

    total_milk_loaded: Decimal

    total_token_registered: Decimal

    total_cash_sales: Decimal

    total_returned_milk: Decimal

    reconciliation_status: str

    reopen_count: int

    version: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliverySessionDetailResponse(DeliverySessionResponse):

    deliveries: list[DailyDeliveryResponse] = []


class DeliverySessionListResponse(BaseModel):

    sessions: list[DeliverySessionResponse]

    total: int


class ChecklistCustomer(BaseModel):

    customer_id: int

    customer_name: str

    address: str | None = None

    phone: str | None = None

    milk_type: str

    quantity: int

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliveryChecklistResponse(BaseModel):

    session_id: int

    route_name: str | None = None

    delivery_date: date

    shift: str

    total_expected: int

    customers: list[ChecklistCustomer]


class ReconciliationResponse(BaseModel):

    session_id: int

    loaded_milk: Decimal

    token_registered: Decimal

    cash_sales: Decimal

    returned_milk: Decimal

    total_accounted: Decimal

    difference: Decimal

    is_balanced: bool

    status: str


class SessionReportSummary(BaseModel):

    total_customers: int

    delivered: int

    pending_token: int

    cash_sale: int

    not_delivered: int


class SessionReportMilkSummary(BaseModel):

    loaded: Decimal

    token_registered: Decimal

    cash_sales: Decimal

    returned: Decimal


class SessionReportResponse(BaseModel):

    session_id: int

    route_name: str | None = None

    delivery_date: date

    shift: str

    summary: SessionReportSummary

    milk_summary: SessionReportMilkSummary
