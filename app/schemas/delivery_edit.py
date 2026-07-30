from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SessionEditResponse(BaseModel):

    edit_id: int

    delivery_id: int | None = None

    customer_name: str | None = None

    edit_type: str

    old_value: dict

    new_value: dict

    reason: str

    edited_by: str

    edited_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SessionEditHistoryResponse(BaseModel):

    session_id: int

    edits: list[SessionEditResponse]

    total_edits: int


class CashSaleCreate(BaseModel):

    customer_name: str = Field(
        min_length=1,
        max_length=100
    )

    customer_phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    milk_type_id: int

    quantity: Decimal = Field(
        gt=0
    )

    amount: Decimal = Field(
        gt=0
    )

    payment_method: str = Field(
        pattern="^(CASH|UPI|CARD)$",
        default="CASH"
    )


class CashSaleResponse(BaseModel):

    id: int

    session_id: int

    customer_name: str

    milk_type_name: str | None = None

    quantity: Decimal

    amount: Decimal

    payment_method: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ReconciliationSubmitRequest(BaseModel):

    total_cash_collected: Decimal = Field(
        ge=0
    )

    cash_sales: list[CashSaleCreate] = []

    returned_milk: Decimal = Field(
        ge=0
    )

    returned_reasons: list[dict] = []

    token_sheets_collected: list[dict] = []

    remarks: str | None = Field(
        default=None,
        max_length=500
    )


class ReconciliationValidationIssue(BaseModel):

    code: str

    message: str

    severity: str


class ReconciliationValidationResponse(BaseModel):

    can_close: bool

    is_balanced: bool

    issues: list[ReconciliationValidationIssue]


class CustomerDeliveryStatus(BaseModel):

    customer_id: int

    customer_name: str

    phone: str | None = None

    address: str | None = None

    milk_type: str

    planned_quantity: int

    status: str

    token_sheet: int | None = None

    cash_paid: Decimal

    is_on_schedule: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class ReconciliationCustomerStatusResponse(BaseModel):

    session_id: int

    customers: list[CustomerDeliveryStatus]

    total: int


class TokenSheetWarningResponse(BaseModel):

    id: int

    warning_code: str

    warning_message: str

    sheet_number: int

    expected_sheet: int | None = None

    acknowledged_by: int | None = None

    acknowledged_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenSheetWarningCreate(BaseModel):

    delivery_id: int

    warning_code: str

    warning_message: str

    sheet_number: int

    expected_sheet: int | None = None

    book_issue_id: int | None = None

    metadata: dict | None = None


class TokenSheetWarningAcknowledge(BaseModel):

    acknowledged_by: int

    acknowledgment_reason: str | None = Field(
        default=None,
        max_length=500
    )
