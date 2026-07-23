from app.exceptions.base import BusinessException


class DuplicateMilkNameError(BusinessException):
    """Raised when the milk name already exists."""

    def __init__(self, milk_name: str):

        super().__init__(
            f"Milk name '{milk_name}' already exists."
        )


class MilkTypeError(BusinessException):
    """Raised when a milk type cannot be found."""

    def __init__(self):

        super().__init__(
            "Milk type not found."
        )
