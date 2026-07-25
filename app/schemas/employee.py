from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator


class EmployeeBase(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    role: str = Field(
        min_length=1,
        max_length=50
    )

    route_id: int | None = Field(
        default=None,
        gt=0
    )


class EmployeeCreate(EmployeeBase):

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )

    confirm_password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )

    @model_validator(mode="after")
    def validate_credentials(self):
        has_username = self.username is not None
        has_password = self.password is not None
        has_confirm = self.confirm_password is not None

        if has_username or has_password or has_confirm:
            if not (has_username and has_password and has_confirm):
                raise ValueError(
                    "username, password, and confirm_password "
                    "must all be provided together."
                )
            if self.password != self.confirm_password:
                raise ValueError(
                    "password and confirm_password do not match."
                )

        return self


class EmployeeCredentialsUpdate(BaseModel):

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )

    confirm_password: str | None = Field(
        default=None,
        min_length=6,
        max_length=128
    )

    @model_validator(mode="after")
    def validate_credentials(self):
        has_any = (
            self.username is not None
            or self.password is not None
            or self.confirm_password is not None
        )
        if not has_any:
            raise ValueError(
                "At least one of username or password "
                "must be provided."
            )

        has_password = self.password is not None
        has_confirm = self.confirm_password is not None

        if has_password or has_confirm:
            if not (has_password and has_confirm):
                raise ValueError(
                    "password and confirm_password "
                    "must be provided together."
                )
            if self.password != self.confirm_password:
                raise ValueError(
                    "password and confirm_password do not match."
                )

        return self


class EmployeeUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    role: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    route_id: int | None = Field(
        default=None,
        gt=0
    )


class EmployeeResponse(EmployeeBase):

    id: int

    employee_code: str

    is_active: bool

    username: str | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class EmployeeSummaryResponse(BaseModel):

    id: int

    employee_code: str

    name: str

    phone: str

    role: str

    model_config = ConfigDict(
        from_attributes=True
    )
