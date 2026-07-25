class EmployeeNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Employee not found."
        )


class DuplicateEmployeeCodeError(Exception):

    def __init__(self, employee_code: str):
        super().__init__(
            f"Employee code '{employee_code}' already exists."
        )


class DuplicateEmployeePhoneError(Exception):

    def __init__(self, phone: str):
        super().__init__(
            f"Employee phone '{phone}' already exists."
        )


class EmployeeRouteNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Route not found."
        )


class InactiveRouteError(Exception):

    def __init__(self):
        super().__init__(
            "Cannot assign an inactive route to an employee."
        )


class EmployeeUserNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "User not found."
        )


class InactiveUserError(Exception):

    def __init__(self):
        super().__init__(
            "Cannot assign an inactive user to an employee."
        )


class DuplicateUsernameError(Exception):

    def __init__(self, username: str):
        super().__init__(
            f"Username '{username}' already exists."
        )


class EmployeeNoLinkedUserError(Exception):

    def __init__(self):
        super().__init__(
            "Employee has no linked user account. "
            "Use employee creation with credentials first."
        )
