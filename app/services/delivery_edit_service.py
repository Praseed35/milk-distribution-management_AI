from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession
from app.models.session_edit import SessionEdit
from app.models.token_book_issue import TokenBookIssue

from app.exceptions.delivery import (
    InvalidSessionStatusError,
    SessionNotFoundError,
)
from app.exceptions.delivery_edit import (
    ConcurrentEditError,
    DeliveryNotFoundError,
    OwnerRequiredError,
    TokenSheetReturnError,
)

from app.constants.statuses import BookIssueStatus, DeliveryStatus, SessionStatus


def reopen_session(
    db: Session,
    session_id: int,
    user_id: int,
    reason: str,
) -> DeliverySession:
    """
    Reopen a closed delivery session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        user_id: User ID (must be Owner).
        reason: Reason for reopening.

    Returns:
        Updated DeliverySession.

    Raises:
        SessionNotFoundError: If session not found.
        InvalidSessionStatusError: If session not closed.
    """
    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        raise SessionNotFoundError(session_id)

    if session.status != SessionStatus.CLOSED:
        raise InvalidSessionStatusError(session.status, SessionStatus.CLOSED)

    old_status = session.status

    session.status = SessionStatus.COMPLETED
    session.reopened_by = user_id
    session.reopened_at = datetime.utcnow()
    session.reopen_count = session.reopen_count + 1

    edit = SessionEdit(
        session_id=session_id,
        edited_by=user_id,
        edit_type="SESSION_REOPEN",
        old_value={"status": old_status},
        new_value={"status": SessionStatus.COMPLETED},
        reason=reason,
    )
    db.add(edit)

    db.commit()
    db.refresh(session)

    return session


def edit_delivery(
    db: Session,
    delivery_id: int,
    user_id: int,
    delivery_status: str | None = None,
    return_token_sheet: bool = False,
    reason: str | None = None,
    version: int | None = None,
) -> dict:
    """
    Edit a delivery from a reopened session.

    Args:
        db: SQLAlchemy database session.
        delivery_id: Delivery ID.
        user_id: User ID (must be Owner).
        delivery_status: New delivery status.
        return_token_sheet: Whether to return token sheet.
        reason: Reason for edit.
        version: Expected version for optimistic locking.

    Returns:
        Edit result dict.

    Raises:
        DeliveryNotFoundError: If delivery not found.
        ConcurrentEditError: If version mismatch.
    """
    delivery = db.query(DailyDelivery).filter(DailyDelivery.id == delivery_id).first()
    if not delivery:
        raise DeliveryNotFoundError(delivery_id)

    if version is not None and delivery.version != version:
        raise ConcurrentEditError()

    session = db.query(DeliverySession).filter(DeliverySession.id == delivery.session_id).first()
    if not session:
        raise SessionNotFoundError(delivery.session_id)

    if session.status not in [SessionStatus.COMPLETED, SessionStatus.CLOSED]:
        raise InvalidSessionStatusError(session.status, SessionStatus.COMPLETED)

    old_status = delivery.delivery_status
    old_token_sheet = delivery.token_sheet_number

    if delivery_status:
        delivery.delivery_status = delivery_status

    delivery.is_edited = True
    delivery.last_edited_by = user_id
    delivery.last_edited_at = datetime.utcnow()
    delivery.version += 1

    token_returned = False
    new_current_sheet = None
    token_book_issue_id = None
    sheet_number = None

    if return_token_sheet and old_status == DeliveryStatus.DELIVERED and old_token_sheet:
        if delivery.token_book_issue_id:
            book_issue = (
                db.query(TokenBookIssue)
                .filter(TokenBookIssue.id == delivery.token_book_issue_id)
                .first()
            )
            if book_issue:
                book_issue.current_sheet = max(1, book_issue.current_sheet - 1)
                new_current_sheet = book_issue.current_sheet
                token_book_issue_id = book_issue.id
                sheet_number = old_token_sheet
                token_returned = True

        delivery.token_sheet_number = None
        delivery.token_book_issue_id = None

    edit = SessionEdit(
        session_id=delivery.session_id,
        delivery_id=delivery_id,
        edited_by=user_id,
        edit_type="STATUS_CHANGE",
        old_value={"status": old_status, "token_sheet": old_token_sheet},
        new_value={
            "status": delivery_status or old_status,
            "token_sheet": None if return_token_sheet else old_token_sheet,
        },
        reason=reason or "Edit delivery",
    )
    db.add(edit)

    db.commit()
    db.refresh(delivery)

    return {
        "delivery_id": delivery_id,
        "old_status": old_status,
        "new_status": delivery.delivery_status,
        "token_sheet_returned": token_returned,
        "token_book_issue_id": token_book_issue_id,
        "sheet_number": sheet_number,
        "new_current_sheet": new_current_sheet,
        "message": (
            f"Delivery corrected. Token sheet #{old_token_sheet} returned to customer."
            if token_returned
            else "Delivery updated successfully."
        ),
    }


def return_token_sheet(
    db: Session,
    delivery_id: int,
    user_id: int,
    reason: str,
) -> dict:
    """
    Return a token sheet for a delivery.

    Args:
        db: SQLAlchemy database session.
        delivery_id: Delivery ID.
        user_id: User ID (must be Owner).
        reason: Reason for return.

    Returns:
        Return result dict.

    Raises:
        DeliveryNotFoundError: If delivery not found.
        TokenSheetReturnError: If cannot return token.
    """
    delivery = db.query(DailyDelivery).filter(DailyDelivery.id == delivery_id).first()
    if not delivery:
        raise DeliveryNotFoundError(delivery_id)

    if delivery.delivery_status != DeliveryStatus.DELIVERED:
        raise TokenSheetReturnError(
            f"Cannot return token for delivery with status {delivery.delivery_status}"
        )

    if not delivery.token_sheet_number:
        raise TokenSheetReturnError("No token sheet registered for this delivery")

    return edit_delivery(
        db,
        delivery_id,
        user_id,
        delivery_status=DeliveryStatus.NOT_DELIVERED,
        return_token_sheet=True,
        reason=reason,
    )


def get_edit_history(
    db: Session,
    session_id: int,
) -> list[dict]:
    """
    Get edit history for a session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        List of edit dicts.
    """
    edits = (
        db.query(SessionEdit)
        .filter(SessionEdit.session_id == session_id)
        .order_by(SessionEdit.created_at.desc())
        .all()
    )

    result = []
    for edit in edits:
        customer_name = None
        if edit.delivery_id:
            delivery = db.query(DailyDelivery).filter(DailyDelivery.id == edit.delivery_id).first()
            if delivery and delivery.customer:
                customer_name = delivery.customer.customer_name

        edited_by_user = None
        if edit.edited_by_user:
            edited_by_user = edit.edited_by_user.username

        result.append(
            {
                "edit_id": edit.id,
                "delivery_id": edit.delivery_id,
                "customer_name": customer_name,
                "edit_type": edit.edit_type,
                "old_value": edit.old_value,
                "new_value": edit.new_value,
                "reason": edit.reason,
                "edited_by": edited_by_user,
                "edited_at": edit.created_at,
            }
        )

    return result
