from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


# ─── Customer Payment Schemas ───


class CustomerPaymentBase(BaseModel):

    customer_id: int = Field(
        ...,
        gt=0
    )

    amount: Decimal = Field(
        ...,
        gt=0
    )

    payment_mode: str = Field(
        pattern="^(CASH|UPI|CARD|CHEQUE|BANK_TRANSFER)$"
    )

    payment_type: str = Field(
        pattern="^(ADVANCE|BILL_PAYMENT)$"
    )

    reference_number: str | None = Field(
        default=None,
        max_length=50
    )

    bill_id: int | None = Field(
        default=None,
        gt=0
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class CustomerPaymentCreate(CustomerPaymentBase):
    pass


class CustomerPaymentUpdate(BaseModel):

    amount: Decimal | None = Field(
        default=None,
        gt=0
    )

    payment_mode: str | None = Field(
        default=None,
        pattern="^(CASH|UPI|CARD|CHEQUE|BANK_TRANSFER)$"
    )

    reference_number: str | None = Field(
        default=None,
        max_length=50
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class CustomerPaymentResponse(CustomerPaymentBase):

    id: int

    payment_date: datetime

    collected_by: int | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerPaymentListResponse(BaseModel):

    id: int

    customer_id: int

    customer_code: str

    customer_name: str

    payment_date: datetime

    amount: Decimal

    payment_mode: str

    payment_type: str

    reference_number: str | None

    bill_id: int | None

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# ─── Customer Bill Schemas ───


class CustomerBillItemResponse(BaseModel):

    id: int

    milk_type_id: int

    milk_name: str

    quantity: int

    unit_price: Decimal

    amount: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerBillBase(BaseModel):

    customer_id: int = Field(
        ...,
        gt=0
    )

    bill_period_start: date

    bill_period_end: date

    due_date: date | None = None

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class BillGenerateRequest(BaseModel):

    customer_id: int = Field(
        ...,
        gt=0
    )

    bill_period_start: date

    bill_period_end: date

    due_date: date | None = None

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class CustomerBillResponse(BaseModel):

    id: int

    customer_id: int

    bill_date: date

    bill_period_start: date

    bill_period_end: date

    total_amount: Decimal

    paid_amount: Decimal

    balance_amount: Decimal

    status: str

    due_date: date | None

    remarks: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    items: list[CustomerBillItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerBillListResponse(BaseModel):

    id: int

    customer_id: int

    customer_code: str

    customer_name: str

    bill_date: date

    bill_period_start: date

    bill_period_end: date

    total_amount: Decimal

    paid_amount: Decimal

    balance_amount: Decimal

    status: str

    due_date: date | None

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class BillStatusUpdate(BaseModel):

    status: str = Field(
        pattern="^(PENDING|PARTIAL|PAID|OVERDUE|CANCELLED)$"
    )


# ─── Outstanding Balance Schema ───


class OutstandingBalanceResponse(BaseModel):

    customer_id: int

    customer_code: str

    customer_name: str

    total_billed: Decimal

    total_paid: Decimal

    balance: Decimal

    last_bill_date: date | None

    last_payment_date: datetime | None
