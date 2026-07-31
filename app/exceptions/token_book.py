class TokenIdentityNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Token identity not found."
        )


class DuplicateTokenIdentityError(Exception):

    def __init__(
        self,
        customer_id: int,
        milk_type_id: int,
        token_number: int
    ):
        super().__init__(
            f"Token number {token_number} is already in use: either for "
            f"customer {customer_id} with milk type {milk_type_id}, "
            f"or by another active customer."
        )


class TokenBookIssueNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Token book issue not found."
        )


class ActiveBookExistsError(Exception):

    def __init__(self, token_identity_id: int):
        super().__init__(
            f"An active book already exists for token identity {token_identity_id}. "
            f"Complete or deactivate it before issuing a new one."
        )


class DuplicateIssueNumberError(Exception):

    def __init__(
        self,
        token_identity_id: int,
        issue_number: int
    ):
        super().__init__(
            f"Issue number {issue_number} already exists for token identity {token_identity_id}."
        )


class TokenBookPaymentNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Token book payment not found."
        )


class InvalidPaymentAmountError(Exception):

    def __init__(self):
        super().__init__(
            "Amount paid cannot exceed book price."
        )