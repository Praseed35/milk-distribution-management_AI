from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class DailyDeliveryCreate(BaseModel):

    session_id: int

    customer_id: int

    milk_type_id: int

    delivered_quantity: int = Field(
        ge=0
    )

    delivery_status: str = Field(
        pattern="^(DELIVERED|PENDING_TOKEN|CASH_SALE|NOT_DELIVERED|CANCELLED)$"
    )

    token_sheet_number: int | None = None

    cash_amount: Decimal | None = None

    remarks: str | None = Field(
        default=None,
        max_length=500
    )


class DailyDeliveryUpdate(BaseModel):

    delivery_status: str | None = Field(
        default=None,
        pattern="^(DELIVERED|PENDING_TOKEN|CASH_SALE|NOT_DELIVERED|CANCELLED)$"
    )

    delivered_quantity: int | None = Field(
        default=None,
        ge=0
    )

    token_sheet_number: int | None = None

    cash_amount: Decimal | None = None

    remarks: str | None = Field(
        default=None,
        max_length=500
    )

    version: int | None = None


class UnplannedDeliveryCreate(BaseModel):

    session_id: int

    customer_id: int

    milk_type_id: int

    delivered_quantity: int = Field(
        ge=0
    )

    delivery_status: str = Field(
        pattern="^(DELIVERED|PENDING_TOKEN|CASH_SALE)$"
    )

    registration_method: str = Field(
        pattern="^(TOKEN_SHEET|CASH|PENDING)$"
    )

    token_sheet_number: int | None = None

    reason: str = Field(
        min_length=1,
        max_length=500
    )


class TokenRegistrationRequest(BaseModel):

    token_sheet_number: int = Field(
        gt=0
    )

    acknowledged_warnings: list[str] = []

    acknowledgment_reason: str | None = Field(
        default=None,
        max_length=500
    )


class TokenValidationRequest(BaseModel):

    customer_id: int

    milk_type_id: int

    sheet_number: int = Field(
        gt=0
    )

    token_book_issue_id: int | None = None


class TokenValidationWarning(BaseModel):

    code: str

    message: str

    severity: str = "WARNING"

    expected_sheet: int | None = None


class TokenValidationResponse(BaseModel):

    is_valid: bool

    warnings: list[TokenValidationWarning]

    can_proceed: bool

    requires_acknowledgment: bool


class TokenRegistrationResponse(BaseModel):

    delivery_id: int

    sheet_registered: bool

    token_book_issue_id: int | None = None

    new_current_sheet: int | None = None

    warnings_logged: int

    message: str


class TokenBookStatus(BaseModel):

    book_issue_id: int

    book_number: str

    milk_type: str

    issue_date: date

    status: str

    sheets_used: int

    sheets_remaining: int

    is_old_book: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerTokenStatusResponse(BaseModel):

    customer_id: int

    customer_name: str | None = None

    token_books: list[TokenBookStatus]

    has_old_book_with_remaining: bool

    old_book_remaining: int


class DailyDeliveryResponse(BaseModel):

    id: int

    session_id: int

    customer_id: int

    customer_name: str | None = None

    milk_type_id: int

    milk_type_name: str | None = None

    planned_quantity: int

    delivered_quantity: int

    delivery_status: str

    delivery_source: str

    token_sheet_number: int | None = None

    token_book_issue_id: int | None = None

    cash_amount: Decimal | None = None

    version: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DailyDeliveryEditRequest(BaseModel):

    delivery_status: str | None = Field(
        default=None,
        pattern="^(DELIVERED|PENDING_TOKEN|CASH_SALE|NOT_DELIVERED|CANCELLED)$"
    )

    return_token_sheet: bool = False

    reason: str = Field(
        min_length=1,
        max_length=500
    )

    version: int | None = None


class DailyDeliveryEditResponse(BaseModel):

    delivery_id: int

    old_status: str

    new_status: str

    token_sheet_returned: bool

    token_book_issue_id: int | None = None

    sheet_number: int | None = None

    new_current_sheet: int | None = None

    message: str


class DailyDeliveryListResponse(BaseModel):

    session_id: int

    deliveries: list[DailyDeliveryResponse]

    total: int


class DeliveryWarning(BaseModel):

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


class DeliveryWarningsResponse(BaseModel):

    delivery_id: int

    warnings: list[DeliveryWarning]
