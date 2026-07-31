from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.constants.shifts import Shift
from app.schemas.customer import CustomerSummaryResponse


class SubscriptionSummaryResponse(BaseModel):

    id: int

    customer: CustomerSummaryResponse

    morning_quantity: int

    evening_quantity: int

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliveryExceptionBase(BaseModel):

    subscription_id: int = Field(
        ...,
        gt=0
    )

    exception_type: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    shift: Shift | None = Field(
        default=None
    )

    start_date: datetime

    end_date: datetime | None = Field(
        default=None
    )

    reason: str | None = Field(
        default=None,
        max_length=255
    )


class DeliveryExceptionCreate(DeliveryExceptionBase):

    pass


class DeliveryExceptionUpdate(BaseModel):

    exception_type: str | None = Field(
        default=None,
        max_length=20
    )

    shift: Shift | None = Field(
        default=None
    )

    start_date: datetime | None = Field(
        default=None
    )

    end_date: datetime | None = Field(
        default=None
    )

    reason: str | None = Field(
        default=None,
        max_length=255
    )

    status: str | None = Field(
        default=None,
        max_length=20
    )


class DeliveryExceptionResponse(DeliveryExceptionBase):

    id: int

    status: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliveryExceptionListResponse(BaseModel):

    id: int

    subscription_id: int

    customer_id: int

    customer_code: str

    customer_name: str

    route_name: str

    exception_type: str

    shift: str | None

    start_date: datetime

    end_date: datetime | None

    status: str

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class DeliveryExceptionDetailResponse(BaseModel):

    id: int

    subscription: SubscriptionSummaryResponse

    exception_type: str

    shift: str | None

    start_date: datetime

    end_date: datetime | None

    reason: str | None

    status: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )