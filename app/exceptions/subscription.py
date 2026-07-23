class SubscriptionNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Subscription not found."
        )


class DuplicateSubscriptionError(Exception):

    def __init__(self, customer_id: int, milk_type_id: int):
        super().__init__(
            f"Subscription already exists for customer {customer_id} with milk type {milk_type_id}."
        )


class InactiveCustomerError(Exception):

    def __init__(self):
        super().__init__(
            "Cannot create subscription for inactive customer."
        )


class InactiveMilkTypeError(Exception):

    def __init__(self):
        super().__init__(
            "Cannot create subscription with inactive milk type."
        )


class InvalidSubscriptionQuantityError(Exception):

    def __init__(self):
        super().__init__(
            "At least one quantity (morning or evening) must be greater than 0."
        )


class SubscriptionAlreadyInactiveError(Exception):

    def __init__(self):
        super().__init__(
            "Subscription is already inactive."
        )
