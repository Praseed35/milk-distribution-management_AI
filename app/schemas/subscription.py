from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.constants.shifts import Shift
from app.schemas.customer import CustomerSummaryResponse
from app.schemas.milk_type import MilkTypeSummaryResponse


class SubscriptionBase(BaseModel):

    customer_id: int = Field(
        ...,
        gt=0
    )

    milk_type_id: int = Field(
        ...,
        gt=0
    )

    morning_quantity: int = Field(
        default=0,
        ge=0
    )

    evening_quantity: int = Field(
        default=0,
        ge=0
    )

    status: str = Field(
        default="ACTIVE",
        max_length=20
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class SubscriptionCreate(SubscriptionBase):

    pass


class SubscriptionUpdate(BaseModel):

    morning_quantity: int | None = Field(
        default=None,
        ge=0
    )

    evening_quantity: int | None = Field(
        default=None,
        ge=0
    )

    status: str | None = Field(
        default=None,
        max_length=20
    )

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class SubscriptionResponse(SubscriptionBase):

    id: int

    start_date: datetime

    end_date: datetime | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SubscriptionListResponse(BaseModel):

    id: int

    customer_id: int

    customer_code: str

    customer_name: str

    route_name: str

    milk_type_name: str

    milk_type_volume: int

    morning_quantity: int

    evening_quantity: int

    status: str

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class SubscriptionDetailResponse(BaseModel):

    id: int

    customer: CustomerSummaryResponse

    milk_type: MilkTypeSummaryResponse

    morning_quantity: int

    evening_quantity: int

    status: str

    start_date: datetime

    end_date: datetime | None

    remarks: str | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
