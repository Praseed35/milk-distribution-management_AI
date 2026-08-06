from app.exceptions.base import BusinessException


class AIUnavailableError(BusinessException):

    def __init__(self, detail: str = "AI service is currently unavailable. Please try again later."):
        super().__init__(detail)
        self.status_code = 503


class AIRateLimitError(BusinessException):

    def __init__(self, detail: str = "Too many requests. Please wait a minute and try again."):
        super().__init__(detail)
        self.status_code = 429


class AIInsufficientDataError(BusinessException):

    def __init__(self, detail: str = "Insufficient data for the requested operation."):
        super().__init__(detail)
        self.status_code = 422
