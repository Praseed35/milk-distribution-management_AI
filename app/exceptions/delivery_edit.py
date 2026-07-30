from app.exceptions.base import BusinessException


class OwnerRequiredError(BusinessException):

    def __init__(self, action: str = "perform this action"):
        super().__init__(f"Only Owner can {action}")
        self.status_code = 403


class ConcurrentEditError(BusinessException):

    def __init__(self):
        super().__init__(
            "Session was modified by another user. Please reload and try again."
        )
        self.status_code = 409


class TokenSheetReturnError(BusinessException):

    def __init__(self, reason: str):
        super().__init__(f"Cannot return token sheet: {reason}")
        self.status_code = 400


class InvalidTokenSheetError(BusinessException):

    def __init__(self, reason: str):
        super().__init__(f"Invalid token sheet: {reason}")
        self.status_code = 400


class TokenBookNotActiveError(BusinessException):

    def __init__(self, book_id: int):
        super().__init__(f"Token book {book_id} is not active")
        self.status_code = 400


class SheetAlreadyUsedError(BusinessException):

    def __init__(self, sheet_number: int, book_id: int):
        super().__init__(
            f"Sheet {sheet_number} is already used in book {book_id}"
        )
        self.status_code = 400


class SheetOutOfRangeError(BusinessException):

    def __init__(self, sheet_number: int, max_sheets: int):
        super().__init__(
            f"Sheet {sheet_number} is out of range (max: {max_sheets})"
        )
        self.status_code = 400


class MilkTypeMismatchError(BusinessException):

    def __init__(self, expected: str, provided: str):
        super().__init__(
            f"Milk type mismatch: expected {expected}, got {provided}"
        )
        self.status_code = 400


class CustomerNotFoundError(BusinessException):

    def __init__(self, customer_id: int):
        super().__init__(f"Customer {customer_id} not found")
        self.status_code = 404


class MilkTypeNotFoundError(BusinessException):

    def __init__(self, milk_type_id: int):
        super().__init__(f"Milk type {milk_type_id} not found")
        self.status_code = 404


class DeliveryNotFoundError(BusinessException):

    def __init__(self, delivery_id: int):
        super().__init__(f"Delivery {delivery_id} not found")
        self.status_code = 404
