from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class MilkTypeBase(BaseModel):

    milk_name: str = Field(
        min_length=2,
        max_length=100
    )

    volume_ml: int = Field(
        gt=0
    )

    description: str | None = Field(
        default=None,
        max_length=255
    )


class MilkTypeCreate(MilkTypeBase):
    pass


class MilkTypeUpdate(MilkTypeBase):

    pass


class MilkTypeResponse(MilkTypeBase):

    id: int

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
