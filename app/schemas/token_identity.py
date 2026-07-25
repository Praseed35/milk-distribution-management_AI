from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from app.schemas.customer import CustomerSummaryResponse
from app.schemas.milk_type import MilkTypeSummaryResponse


class TokenIdentityBase(BaseModel):

    customer_id: int = Field(
        ...,
        gt=0
    )

    milk_type_id: int = Field(
        ...,
        gt=0
    )

    token_number: int = Field(
        ...,
        gt=0
    )


class TokenIdentityCreate(TokenIdentityBase):

    pass


class TokenIdentityUpdate(BaseModel):

    token_number: int | None = Field(
        default=None,
        gt=0
    )


class TokenIdentityResponse(TokenIdentityBase):

    id: int

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenIdentityListResponse(BaseModel):

    id: int

    customer_id: int

    customer_code: str

    customer_name: str

    milk_type_id: int

    milk_type_name: str

    milk_type_volume: int

    token_number: int

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenIdentityDetailResponse(BaseModel):

    id: int

    customer: CustomerSummaryResponse

    milk_type: MilkTypeSummaryResponse

    token_number: int

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenIdentitySummaryResponse(BaseModel):

    id: int

    customer: CustomerSummaryResponse

    milk_type: MilkTypeSummaryResponse

    token_number: int

    model_config = ConfigDict(
        from_attributes=True
    )