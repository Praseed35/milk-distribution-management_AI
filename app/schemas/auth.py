from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePassword(BaseModel):

    current_password: str = Field(
        min_length=6,
        max_length=128
    )

    new_password: str = Field(
        min_length=6,
        max_length=128
    )

    confirm_password: str = Field(
        min_length=6,
        max_length=128
    )

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError(
                "new_password and confirm_password do not match."
            )
        if self.current_password == self.new_password:
            raise ValueError(
                "new_password must be different from current_password."
            )
        return self