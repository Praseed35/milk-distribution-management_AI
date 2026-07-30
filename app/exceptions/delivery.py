from app.exceptions.base import BusinessException


class SessionNotFoundError(BusinessException):

    def __init__(self, session_id: int | None = None):
        message = "Delivery session not found"
        if session_id:
            message = f"Delivery session {session_id} not found"
        super().__init__(message)
        self.status_code = 404


class SessionAlreadyClosedError(BusinessException):

    def __init__(self, session_id: int):
        super().__init__(f"Delivery session {session_id} is already closed")
        self.status_code = 400


class SessionNotBalancedError(BusinessException):

    def __init__(self, session_id: int, difference: float):
        super().__init__(
            f"Cannot close session {session_id}: reconciliation not balanced. "
            f"Difference: {difference} liters"
        )
        self.status_code = 400


class DispatchAlreadyRecordedError(BusinessException):

    def __init__(self, session_id: int):
        super().__init__(f"Dispatch already recorded for session {session_id}")
        self.status_code = 400


class InvalidSessionStatusError(BusinessException):

    def __init__(self, current_status: str, required_status: str):
        super().__init__(
            f"Invalid session status: {current_status}. Required: {required_status}"
        )
        self.status_code = 400


class SessionAlreadyExistsError(BusinessException):

    def __init__(self, route_id: int, delivery_date: str, shift: str):
        super().__init__(
            f"Session already exists for route {route_id} on {delivery_date} ({shift})"
        )
        self.status_code = 400


class RouteNotFoundError(BusinessException):

    def __init__(self, route_id: int):
        super().__init__(f"Route {route_id} not found")
        self.status_code = 404


class EmployeeNotFoundError(BusinessException):

    def __init__(self, employee_id: int):
        super().__init__(f"Employee {employee_id} not found")
        self.status_code = 404
