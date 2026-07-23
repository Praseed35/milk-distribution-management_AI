from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SubscriptionBase(BaseModel):

    customer_id: int

    milk_type_id: int

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
