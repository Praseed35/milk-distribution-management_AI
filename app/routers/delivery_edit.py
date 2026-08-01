from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.core.roles import require_role
from app.models.user import User

from app.schemas.delivery_session import (
    DeliverySessionReopen,
    DeliverySessionResponse,
)
from app.schemas.daily_delivery import (
    DailyDeliveryEditRequest,
    DailyDeliveryEditResponse,
    DailyDeliveryResponse,
    DailyDeliveryUpdate,
    DeliveryWarningsResponse,
    TokenRegistrationRequest,
    TokenRegistrationResponse,
    TokenValidationRequest,
    TokenValidationResponse,
    UnplannedDeliveryCreate,
    CustomerTokenStatusResponse,
)

from app.services import delivery_service
from app.services import delivery_registration
from app.services import delivery_edit_service

from app.exceptions.delivery import (
    InvalidSessionStatusError,
    SessionNotFoundError,
)
from app.exceptions.delivery_edit import (
    ConcurrentEditError,
    CustomerNotFoundError,
    DeliveryNotFoundError,
    InvalidTokenSheetError,
    MilkTypeNotFoundError,
    OwnerRequiredError,
    SheetAlreadyUsedError,
    SheetOutOfRangeError,
    TokenBookNotActiveError,
    TokenSheetReturnError,
)


router = APIRouter(
    prefix="/deliveries",
    tags=["Deliveries"]
)


@router.put(
    "/{delivery_id}",
    response_model=DailyDeliveryResponse,
)
def update_delivery(
    delivery_id: int,
    delivery: DailyDeliveryUpdate,
    db: Session = Depends(get_db),
):
    try:
        return delivery_registration.update_delivery_status(
            db,
            delivery_id=delivery_id,
            delivery_status=delivery.delivery_status,
            delivered_quantity=delivery.delivered_quantity,
            token_sheet_number=delivery.token_sheet_number,
            cash_amount=float(delivery.cash_amount) if delivery.cash_amount else None,
            remarks=delivery.remarks,
            version=delivery.version,
        )
    except DeliveryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTokenSheetError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConcurrentEditError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post(
    "/unplanned",
    response_model=DailyDeliveryResponse,
    status_code=201,
)
def add_unplanned_delivery(
    delivery: UnplannedDeliveryCreate,
    db: Session = Depends(get_db),
):
    try:
        return delivery_registration.add_unplanned_delivery(
            db,
            session_id=delivery.session_id,
            customer_id=delivery.customer_id,
            milk_type_id=delivery.milk_type_id,
            delivered_quantity=delivery.delivered_quantity,
            delivery_status=delivery.delivery_status,
            registration_method=delivery.registration_method,
            token_sheet_number=delivery.token_sheet_number,
            reason=delivery.reason,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MilkTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTokenSheetError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SheetOutOfRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{delivery_id}/register-token",
    response_model=TokenRegistrationResponse,
)
def register_token(
    delivery_id: int,
    registration: TokenRegistrationRequest,
    db: Session = Depends(get_db),
):
    try:
        return delivery_registration.register_token(
            db,
            delivery_id=delivery_id,
            sheet_number=registration.token_sheet_number,
            acknowledged_warnings=registration.acknowledged_warnings,
            acknowledgment_reason=registration.acknowledgment_reason,
        )
    except DeliveryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTokenSheetError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SheetAlreadyUsedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SheetOutOfRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/validate-token",
    response_model=TokenValidationResponse,
)
def validate_token(
    validation: TokenValidationRequest,
    db: Session = Depends(get_db),
):
    try:
        is_valid, warnings, requires_acknowledgment = (
            delivery_registration.validate_token_sheet(
                db,
                validation.customer_id,
                validation.milk_type_id,
                validation.sheet_number,
                validation.token_book_issue_id,
            )
        )
        return TokenValidationResponse(
            is_valid=is_valid,
            warnings=warnings,
            can_proceed=is_valid,
            requires_acknowledgment=requires_acknowledgment,
        )
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MilkTypeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTokenSheetError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SheetAlreadyUsedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SheetOutOfRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/customer/{customer_id}/token-status",
    response_model=CustomerTokenStatusResponse,
)
def get_customer_token_status(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        return delivery_registration.get_customer_token_status(db, customer_id)
    except CustomerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{delivery_id}/edit",
    response_model=DailyDeliveryEditResponse,
)
def edit_delivery(
    delivery_id: int,
    edit_request: DailyDeliveryEditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER"])),
):
    try:
        return delivery_edit_service.edit_delivery(
            db,
            delivery_id=delivery_id,
            user_id=current_user.id,
            delivery_status=edit_request.delivery_status,
            return_token_sheet=edit_request.return_token_sheet,
            reason=edit_request.reason,
            version=edit_request.version,
        )
    except DeliveryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConcurrentEditError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidTokenSheetError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{delivery_id}/warnings",
    response_model=DeliveryWarningsResponse,
)
def get_delivery_warnings(
    delivery_id: int,
    db: Session = Depends(get_db),
):
    warnings = delivery_registration.get_delivery_warnings(db, delivery_id)
    return DeliveryWarningsResponse(
        delivery_id=delivery_id,
        warnings=warnings,
    )


@router.get(
    "/session/{session_id}",
    response_model=dict,
)
def get_session_deliveries(
    session_id: int,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    from sqlalchemy import and_
    from app.models.daily_delivery import DailyDelivery

    query = db.query(DailyDelivery).filter(
        and_(
            DailyDelivery.session_id == session_id,
            DailyDelivery.is_active == True,
        )
    )

    if status:
        query = query.filter(DailyDelivery.delivery_status == status)

    query = query.order_by(DailyDelivery.id)

    total = query.count()
    deliveries = query.offset(skip).limit(limit).all()

    return {
        "session_id": session_id,
        "deliveries": [DailyDeliveryResponse.model_validate(d) for d in deliveries],
        "total": total,
    }


@router.post(
    "/session/{session_id}/reopen",
    response_model=DeliverySessionResponse,
)
def reopen_session(
    session_id: int,
    reopen: DeliverySessionReopen,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["OWNER"])),
):
    try:
        return delivery_edit_service.reopen_session(
            db,
            session_id,
            user_id=current_user.id,
            reason=reopen.reason,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSessionStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/session/{session_id}/edit-history",
    response_model=list,
)
def get_edit_history(
    session_id: int,
    db: Session = Depends(get_db),
):
    return delivery_edit_service.get_edit_history(db, session_id)
