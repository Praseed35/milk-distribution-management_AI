class CustomerPaymentNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Customer payment not found."
        )


class CustomerBillNotFoundError(Exception):

    def __init__(self):
        super().__init__(
            "Customer bill not found."
        )


class InvalidPaymentModeError(Exception):

    def __init__(self, mode: str):
        super().__init__(
            f"Invalid payment mode: {mode}. "
            f"Allowed modes: CASH, UPI, CARD, CHEQUE, BANK_TRANSFER."
        )


class InvalidPaymentTypeError(Exception):

    def __init__(self, payment_type: str):
        super().__init__(
            f"Invalid payment type: {payment_type}. "
            f"Allowed types: ADVANCE, BILL_PAYMENT."
        )


class InvalidBillStatusError(Exception):

    def __init__(self, status: str):
        super().__init__(
            f"Invalid bill status: {status}. "
            f"Allowed statuses: PENDING, PARTIAL, PAID, OVERDUE, CANCELLED."
        )


class BillAlreadyPaidError(Exception):

    def __init__(self, bill_id: int):
        super().__init__(
            f"Bill {bill_id} is already fully paid."
        )


class BillAlreadyCancelledError(Exception):

    def __init__(self, bill_id: int):
        super().__init__(
            f"Bill {bill_id} is already cancelled."
        )


class NoDeliveriesForBillError(Exception):

    def __init__(self):
        super().__init__(
            "No deliveries found for the given period."
        )
