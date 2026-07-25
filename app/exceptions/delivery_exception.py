class DeliveryExceptionNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Delivery exception not found."
        )


class DeliveryExceptionOverlapError(Exception):

    def __init__(
        self,
        subscription_id: int,
        start_date: str,
        end_date: str
    ):
        super().__init__(
            f"Delivery exception overlaps with existing exception "
            f"for subscription {subscription_id} "
            f"between {start_date} and {end_date}."
        )


class InvalidDeliveryExceptionDateError(Exception):

    def __init__(self):
        super().__init__(
            "End date must be after start date."
        )


class InactiveSubscriptionError(Exception):

    def __init__(self):
        super().__init__(
            "Cannot create delivery exception for inactive subscription."
        )


class DeliveryExceptionAlreadyInactiveError(Exception):

    def __init__(self):
        super().__init__(
            "Delivery exception is already cancelled."
        )
