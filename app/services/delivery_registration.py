from datetime import date, datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession
from app.models.milk_type import MilkType
from app.models.token_book_issue import TokenBookIssue

from app.exceptions.delivery_edit import (
    CustomerNotFoundError,
    DeliveryNotFoundError,
    InvalidTokenSheetError,
    MilkTypeMismatchError,
    MilkTypeNotFoundError,
    SheetAlreadyUsedError,
    SheetOutOfRangeError,
    TokenBookNotActiveError,
)
from app.exceptions.delivery import SessionNotFoundError

from app.constants.statuses import BookIssueStatus, DeliveryStatus, DeliverySource


def validate_token_sheet(
    db: Session,
    customer_id: int,
    milk_type_id: int,
    sheet_number: int,
    token_book_issue_id: int | None = None,
) -> tuple[bool, list[dict], bool]:
    """
    Validate a token sheet before registration.

    Args:
        db: SQLAlchemy database session.
        customer_id: Customer ID.
        milk_type_id: Milk type ID.
        sheet_number: Sheet number to validate.
        token_book_issue_id: Optional specific book issue ID.

    Returns:
        Tuple of (is_valid, warnings, requires_acknowledgment).
    """
    warnings = []
    requires_acknowledgment = False

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise CustomerNotFoundError(customer_id)

    milk_type = db.query(MilkType).filter(MilkType.id == milk_type_id).first()
    if not milk_type:
        raise MilkTypeNotFoundError(milk_type_id)

    query = (
        db.query(TokenBookIssue)
        .filter(
            and_(
                TokenBookIssue.customer_id == customer_id,
                TokenBookIssue.milk_type_id == milk_type_id,
                TokenBookIssue.status == BookIssueStatus.ACTIVE,
                TokenBookIssue.is_active == True,
            )
        )
    )

    if token_book_issue_id:
        query = query.filter(TokenBookIssue.id == token_book_issue_id)

    book_issues = query.all()

    if not book_issues:
        raise InvalidTokenSheetError(
            f"No active token book found for customer {customer_id} "
            f"with milk type {milk_type_id}"
        )

    target_book = book_issues[0]

    if token_book_issue_id:
        target_book = next(
            (b for b in book_issues if b.id == token_book_issue_id),
            None,
        )
        if not target_book:
            raise InvalidTokenSheetError(
                f"Token book {token_book_issue_id} not found or not active"
            )

    if sheet_number > target_book.total_sheets:
        raise SheetOutOfRangeError(sheet_number, target_book.total_sheets)

    existing_usage = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.customer_id == customer_id,
                DailyDelivery.token_book_issue_id == target_book.id,
                DailyDelivery.token_sheet_number == sheet_number,
                DailyDelivery.delivery_status == DeliveryStatus.DELIVERED,
                DailyDelivery.is_active == True,
            )
        )
        .first()
    )
    if existing_usage:
        raise SheetAlreadyUsedError(sheet_number, target_book.id)

    current_sheet = target_book.current_sheet
    if sheet_number != current_sheet:
        if sheet_number > current_sheet:
            warnings.append(
                {
                    "code": "NON_SEQUENTIAL_SHEET",
                    "message": (
                        f"Sheet #{sheet_number} skips ahead. "
                        f"Sheet #{current_sheet} not yet used."
                    ),
                    "severity": "WARNING",
                    "expected_sheet": current_sheet,
                }
            )
        else:
            warnings.append(
                {
                    "code": "SHEET_OUT_OF_ORDER",
                    "message": (
                        f"Sheet #{sheet_number} is out of order. "
                        f"Current sheet is #{current_sheet}."
                    ),
                    "severity": "WARNING",
                    "expected_sheet": current_sheet,
                }
            )
        requires_acknowledgment = True

    if len(book_issues) > 1:
        old_books = [
            b for b in book_issues
            if b.id != target_book.id and b.current_sheet <= b.total_sheets
        ]
        if old_books:
            old_book = old_books[0]
            remaining = old_book.total_sheets - old_book.current_sheet + 1
            warnings.append(
                {
                    "code": "NEW_BOOK_BEFORE_OLD_FINISHED",
                    "message": (
                        f"Old book #{old_book.book_number} still has "
                        f"{remaining} sheets remaining."
                    ),
                    "severity": "WARNING",
                }
            )
            requires_acknowledgment = True

    is_valid = len(warnings) == 0 or requires_acknowledgment

    return is_valid, warnings, requires_acknowledgment


def register_token(
    db: Session,
    delivery_id: int,
    sheet_number: int,
    acknowledged_warnings: list[str] | None = None,
    acknowledgment_reason: str | None = None,
) -> dict:
    """
    Register a token sheet for a delivery.

    Args:
        db: SQLAlchemy database session.
        delivery_id: Delivery ID.
        sheet_number: Sheet number to register.
        acknowledged_warnings: List of warning codes acknowledged.
        acknowledgment_reason: Reason for acknowledging warnings.

    Returns:
        Registration result dict.

    Raises:
        DeliveryNotFoundError: If delivery not found.
        InvalidTokenSheetError: If token sheet invalid.
        SheetAlreadyUsedError: If sheet already used.
    """
    delivery = db.query(DailyDelivery).filter(DailyDelivery.id == delivery_id).first()
    if not delivery:
        raise DeliveryNotFoundError(delivery_id)

    is_valid, warnings, requires_acknowledgment = validate_token_sheet(
        db,
        delivery.customer_id,
        delivery.milk_type_id,
        sheet_number,
    )

    if requires_acknowledgment and not acknowledged_warnings:
        warning_codes = [w["code"] for w in warnings]
        raise InvalidTokenSheetError(
            f"Warnings require acknowledgment: {', '.join(warning_codes)}"
        )

    customer = db.query(Customer).filter(Customer.id == delivery.customer_id).first()
    book_issue = (
        db.query(TokenBookIssue)
        .filter(
            and_(
                TokenBookIssue.customer_id == delivery.customer_id,
                TokenBookIssue.milk_type_id == delivery.milk_type_id,
                TokenBookIssue.status == BookIssueStatus.ACTIVE,
                TokenBookIssue.is_active == True,
            )
        )
        .first()
    )

    delivery.token_sheet_number = sheet_number
    delivery.token_book_issue_id = book_issue.id if book_issue else None
    delivery.delivery_status = DeliveryStatus.DELIVERED
    delivery.delivered_quantity = delivery.planned_quantity

    if book_issue:
        book_issue.current_sheet = sheet_number + 1

    db.commit()
    db.refresh(delivery)

    new_current_sheet = book_issue.current_sheet if book_issue else None

    return {
        "delivery_id": delivery_id,
        "sheet_registered": True,
        "token_book_issue_id": book_issue.id if book_issue else None,
        "new_current_sheet": new_current_sheet,
        "warnings_logged": len(warnings),
        "message": f"Token Sheet #{sheet_number} registered successfully.",
    }


def update_delivery_status(
    db: Session,
    delivery_id: int,
    delivery_status: str | None = None,
    delivered_quantity: int | None = None,
    token_sheet_number: int | None = None,
    cash_amount: float | None = None,
    remarks: str | None = None,
    version: int | None = None,
) -> DailyDelivery:
    """
    Update a delivery's status or details.

    Args:
        db: SQLAlchemy database session.
        delivery_id: Delivery ID.
        delivery_status: New status.
        delivered_quantity: New quantity.
        token_sheet_number: New token sheet number.
        cash_amount: Cash amount.
        remarks: Remarks.
        version: Expected version for optimistic locking.

    Returns:
        Updated DailyDelivery.

    Raises:
        DeliveryNotFoundError: If delivery not found.
    """
    delivery = db.query(DailyDelivery).filter(DailyDelivery.id == delivery_id).first()
    if not delivery:
        raise DeliveryNotFoundError(delivery_id)

    if version is not None and delivery.version != version:
        from app.exceptions.delivery_edit import ConcurrentEditError
        raise ConcurrentEditError()

    if delivery_status:
        delivery.delivery_status = delivery_status
    if delivered_quantity is not None:
        delivery.delivered_quantity = delivered_quantity
    if token_sheet_number is not None:
        delivery.token_sheet_number = token_sheet_number
    if cash_amount is not None:
        delivery.cash_amount = cash_amount
    if remarks is not None:
        delivery.remarks = remarks

    delivery.version += 1

    db.commit()
    db.refresh(delivery)

    return delivery


def add_unplanned_delivery(
    db: Session,
    session_id: int,
    customer_id: int,
    milk_type_id: int,
    delivered_quantity: int,
    delivery_status: str,
    registration_method: str,
    token_sheet_number: int | None = None,
    reason: str | None = None,
    added_by: int | None = None,
) -> DailyDelivery:
    """
    Add an unplanned delivery.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        customer_id: Customer ID.
        milk_type_id: Milk type ID.
        delivered_quantity: Quantity delivered.
        delivery_status: Delivery status.
        registration_method: TOKEN_SHEET, CASH, or PENDING.
        token_sheet_number: Token sheet number if applicable.
        reason: Reason for unplanned delivery.
        added_by: User ID who added the delivery.

    Returns:
        Newly created DailyDelivery.

    Raises:
        SessionNotFoundError: If session not found.
        CustomerNotFoundError: If customer not found.
        MilkTypeNotFoundError: If milk type not found.
    """
    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        raise SessionNotFoundError(session_id)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise CustomerNotFoundError(customer_id)

    milk_type = db.query(MilkType).filter(MilkType.id == milk_type_id).first()
    if not milk_type:
        raise MilkTypeNotFoundError(milk_type_id)

    token_book_issue_id = None
    if registration_method == "TOKEN_SHEET" and token_sheet_number:
        is_valid, warnings, _ = validate_token_sheet(
            db, customer_id, milk_type_id, token_sheet_number
        )
        if not is_valid:
            raise InvalidTokenSheetError("Token sheet validation failed")

        book_issue = (
            db.query(TokenBookIssue)
            .filter(
                and_(
                    TokenBookIssue.customer_id == customer_id,
                    TokenBookIssue.milk_type_id == milk_type_id,
                    TokenBookIssue.status == BookIssueStatus.ACTIVE,
                    TokenBookIssue.is_active == True,
                )
            )
            .first()
        )
        token_book_issue_id = book_issue.id if book_issue else None

    delivery = DailyDelivery(
        session_id=session_id,
        customer_id=customer_id,
        milk_type_id=milk_type_id,
        planned_quantity=0,
        delivered_quantity=delivered_quantity,
        delivery_status=delivery_status,
        delivery_source=DeliverySource.UNPLANNED,
        token_sheet_number=token_sheet_number,
        token_book_issue_id=token_book_issue_id,
        added_by=added_by,
        added_reason=reason,
        shift=session.shift,
        delivery_date=session.delivery_date,
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return delivery


def get_customer_token_status(
    db: Session,
    customer_id: int,
) -> dict:
    """
    Get customer's token book status.

    Args:
        db: SQLAlchemy database session.
        customer_id: Customer ID.

    Returns:
        Customer token status dict.

    Raises:
        CustomerNotFoundError: If customer not found.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise CustomerNotFoundError(customer_id)

    book_issues = (
        db.query(TokenBookIssue)
        .filter(
            and_(
                TokenBookIssue.customer_id == customer_id,
                TokenBookIssue.is_active == True,
            )
        )
        .all()
    )

    token_books = []
    has_old_book_with_remaining = False
    old_book_remaining = 0

    for book in book_issues:
        sheets_used = book.current_sheet - 1 if book.current_sheet > 0 else 0
        sheets_remaining = book.total_sheets - sheets_used

        issue_date = book.issue_date
        if isinstance(issue_date, datetime):
            issue_date = issue_date.date()

        token_books.append(
            {
                "book_issue_id": book.id,
                "book_number": book.book_number,
                "milk_type": book.milk_type.milk_name if book.milk_type else "Unknown",
                "issue_date": issue_date,
                "status": book.status,
                "sheets_used": sheets_used,
                "sheets_remaining": sheets_remaining,
                "is_old_book": False,
            }
        )

    if len(book_issues) > 1:
        sorted_books = sorted(book_issues, key=lambda x: x.issue_date)
        for i, book in enumerate(sorted_books):
            if i < len(sorted_books) - 1:
                sheets_used = book.current_sheet - 1 if book.current_sheet > 0 else 0
                sheets_remaining = book.total_sheets - sheets_used
                if sheets_remaining > 0:
                    has_old_book_with_remaining = True
                    old_book_remaining = sheets_remaining
                    token_books[i]["is_old_book"] = True

    return {
        "customer_id": customer_id,
        "customer_name": customer.customer_name,
        "token_books": token_books,
        "has_old_book_with_remaining": has_old_book_with_remaining,
        "old_book_remaining": old_book_remaining,
    }


def get_delivery_warnings(
    db: Session,
    delivery_id: int,
) -> list:
    """
    Get warnings for a delivery.

    Args:
        db: SQLAlchemy database session.
        delivery_id: Delivery ID.

    Returns:
        List of warning dicts.
    """
    from app.models.token_sheet_warning import TokenSheetWarning

    warnings = (
        db.query(TokenSheetWarning)
        .filter(TokenSheetWarning.delivery_id == delivery_id)
        .all()
    )

    return [
        {
            "id": w.id,
            "warning_code": w.warning_code,
            "warning_message": w.warning_message,
            "sheet_number": w.sheet_number,
            "expected_sheet": w.expected_sheet,
            "acknowledged_by": w.acknowledged_by,
            "acknowledged_at": w.acknowledged_at,
        }
        for w in warnings
    ]
