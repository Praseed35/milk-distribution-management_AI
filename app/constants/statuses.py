from enum import Enum


class SessionStatus(str, Enum):

    PLANNED = "PLANNED"

    STARTED = "STARTED"

    COMPLETED = "COMPLETED"

    CLOSED = "CLOSED"

class PaymentStatus(str, Enum):

    PAID = "PAID"

    PENDING = "PENDING"

    PARTIAL = "PARTIAL"

class TokenStatus(str, Enum):

    COLLECTED = "COLLECTED"

    PENDING = "PENDING"

    CARRY_FORWARD = "CARRY_FORWARD"

class DeliveryStatus(str, Enum):

    DELIVERED = "DELIVERED"

    PENDING_TOKEN = "PENDING_TOKEN"

    CASH_SALE = "CASH_SALE"

    NOT_DELIVERED = "NOT_DELIVERED"

    SKIPPED = "SKIPPED"

    CANCELLED = "CANCELLED"


class ExceptionType(str, Enum):

    VACATION = "VACATION"

    NO_MILK = "NO_MILK"

    HOLIDAY = "HOLIDAY"


class ExceptionStatus(str, Enum):

    ACTIVE = "ACTIVE"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


class BookIssueStatus(str, Enum):

    WAITING = "WAITING"

    ACTIVE = "ACTIVE"

    COMPLETED = "COMPLETED"


class PaymentMode(str, Enum):

    PREPAID = "PREPAID"

    POSTPAID = "POSTPAID"

class CustomerPaymentMode(str, Enum):

    CASH = "CASH"

    UPI = "UPI"

    CARD = "CARD"

    CHEQUE = "CHEQUE"

    BANK_TRANSFER = "BANK_TRANSFER"

class CustomerPaymentType(str, Enum):

    ADVANCE = "ADVANCE"

    BILL_PAYMENT = "BILL_PAYMENT"

class BillStatus(str, Enum):

    PENDING = "PENDING"

    PARTIAL = "PARTIAL"

    PAID = "PAID"

    OVERDUE = "OVERDUE"

    CANCELLED = "CANCELLED"


class DeliverySource(str, Enum):

    PLANNED = "PLANNED"

    UNPLANNED = "UNPLANNED"


class WarningCode(str, Enum):

    NON_SEQUENTIAL_SHEET = "NON_SEQUENTIAL_SHEET"

    SHEET_OUT_OF_ORDER = "SHEET_OUT_OF_ORDER"

    GAP_DETECTED = "GAP_DETECTED"

    SHEET_ALREADY_USED = "SHEET_ALREADY_USED"

    NEW_BOOK_BEFORE_OLD_FINISHED = "NEW_BOOK_BEFORE_OLD_FINISHED"


class ReconciliationStatus(str, Enum):

    BALANCED = "BALANCED"

    UNBALANCED = "UNBALANCED"

    PENDING = "PENDING"