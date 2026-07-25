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