from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.schemas.token_identity import TokenIdentitySummaryResponse


class TokenBookIssueSummaryResponse(BaseModel):

    id: int

    token_identity: TokenIdentitySummaryResponse

    issue_number: int

    status: str

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookIssueBase(BaseModel):

    token_identity_id: int = Field(
        ...,
        gt=0
    )

    issue_number: int = Field(
        ...,
        gt=0
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class TokenBookIssueCreate(TokenBookIssueBase):

    pass


class TokenBookIssueUpdate(BaseModel):

    status: str | None = Field(
        default=None,
        max_length=20
    )

    current_sheet: int | None = Field(
        default=None,
        ge=0
    )

    completion_date: datetime | None = Field(
        default=None
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class TokenBookIssueResponse(TokenBookIssueBase):

    id: int

    issue_date: datetime

    completion_date: datetime | None

    current_sheet: int

    status: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookIssueListResponse(BaseModel):

    id: int

    token_identity_id: int

    customer_id: int

    customer_code: str

    customer_name: str

    milk_type_name: str

    token_number: int

    issue_number: int

    issue_date: datetime

    status: str

    current_sheet: int

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookIssueDetailResponse(BaseModel):

    id: int

    token_identity: TokenIdentitySummaryResponse

    issue_number: int

    issue_date: datetime

    completion_date: datetime | None

    current_sheet: int

    status: str

    remarks: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookPaymentBase(BaseModel):

    token_book_issue_id: int = Field(
        ...,
        gt=0
    )

    payment_mode: str = Field(
        ...,
        max_length=20
    )

    book_price: Decimal = Field(
        ...,
        gt=0
    )

    amount_paid: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class TokenBookPaymentCreate(TokenBookPaymentBase):

    pass


class TokenBookPaymentUpdate(BaseModel):

    payment_mode: str | None = Field(
        default=None,
        max_length=20
    )

    payment_status: str | None = Field(
        default=None,
        max_length=20
    )

    book_price: Decimal | None = Field(
        default=None,
        gt=0
    )

    amount_paid: Decimal | None = Field(
        default=None,
        ge=0
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class TokenBookPaymentResponse(TokenBookPaymentBase):

    id: int

    payment_status: str

    balance_amount: Decimal

    payment_date: datetime

    collected_by: int | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookPaymentListResponse(BaseModel):

    id: int

    token_book_issue_id: int

    customer_id: int

    customer_code: str

    customer_name: str

    payment_mode: str

    payment_status: str

    book_price: Decimal

    amount_paid: Decimal

    balance_amount: Decimal

    payment_date: datetime

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenBookPaymentDetailResponse(BaseModel):

    id: int

    token_book_issue: TokenBookIssueSummaryResponse

    payment_mode: str

    payment_status: str

    book_price: Decimal

    amount_paid: Decimal

    balance_amount: Decimal

    payment_date: datetime

    collected_by: int | None

    remarks: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )