from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class CustomerBase(BaseModel):

    customer_name: str = Field(
        min_length=2,
        max_length=100
    )

    primary_phone: str = Field(
        min_length=10,
        max_length=10
    )

    alternate_phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    route_id: int

    remarks: str | None = Field(
        default=None,
        max_length=255
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):

    pass

class CustomerResponse(CustomerBase):

    id: int

    customer_code: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class CustomerSummaryResponse(BaseModel):

    id: int

    customer_code: str

    customer_name: str

    primary_phone: str

    model_config = ConfigDict(
        from_attributes=True
    )