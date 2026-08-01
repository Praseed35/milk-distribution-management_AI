from datetime import date

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.delivery_session import (
    ChecklistCustomer,
    DailyDeliveryResponse,
    DeliveryChecklistResponse,
    DeliverySessionCreate,
    DeliverySessionDetailResponse,
    DeliverySessionDispatch,
    DeliverySessionListResponse,
    DeliverySessionReopen,
    DeliverySessionResponse,
    ReconciliationResponse,
    SessionReportMilkSummary,
    SessionReportResponse,
    SessionReportSummary,
)

from app.services import delivery_service
from app.services import delivery_reconciliation

from app.exceptions.delivery import (
    DispatchAlreadyRecordedError,
    EmployeeNotFoundError,
    InvalidSessionStatusError,
    RouteNotFoundError,
    SessionAlreadyClosedError,
    SessionAlreadyExistsError,
    SessionNotBalancedError,
    SessionNotFoundError,
)


router = APIRouter(
    prefix="/deliveries/sessions",
    tags=["Delivery Sessions"]
)


@router.post(
    "/",
    response_model=DeliverySessionResponse,
    status_code=201,
)
def create_session(
    session: DeliverySessionCreate,
    db: Session = Depends(get_db),
):
    try:
        return delivery_service.create_session(
            db,
            session.route_id,
            session.delivery_date,
            session.shift,
            session.delivery_partner_id,
        )
    except RouteNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SessionAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=DeliverySessionListResponse,
)
def list_sessions(
    route_id: int | None = None,
    delivery_date: date | None = None,
    shift: str | None = None,
    status: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    sessions, total = delivery_service.list_sessions(
        db,
        route_id=route_id,
        delivery_date=delivery_date,
        shift=shift,
        status=status,
        skip=skip,
        limit=limit,
    )
    return DeliverySessionListResponse(sessions=sessions, total=total)


@router.get(
    "/{session_id}",
    response_model=DeliverySessionDetailResponse,
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        session = delivery_service.get_session(db, session_id)
        deliveries = (
            db.query(delivery_service.DailyDelivery)
            .filter(delivery_service.DailyDelivery.session_id == session_id)
            .all()
        )
        return DeliverySessionDetailResponse(
            **session.__dict__,
            deliveries=[DailyDeliveryResponse.model_validate(d) for d in deliveries],
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{session_id}/start",
    response_model=DeliverySessionResponse,
)
def start_session(
    session_id: int,
    dispatch: DeliverySessionDispatch,
    db: Session = Depends(get_db),
):
    try:
        return delivery_service.start_session(
            db,
            session_id,
            float(dispatch.total_milk_loaded),
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSessionStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DispatchAlreadyRecordedError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{session_id}/dispatch",
    response_model=DeliverySessionResponse,
)
def record_dispatch(
    session_id: int,
    dispatch: DeliverySessionDispatch,
    db: Session = Depends(get_db),
):
    try:
        return delivery_service.record_dispatch(
            db,
            session_id,
            float(dispatch.total_milk_loaded),
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSessionStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DispatchAlreadyRecordedError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{session_id}/complete",
    response_model=DeliverySessionResponse,
)
def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        return delivery_service.complete_session(
            db,
            session_id,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSessionStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{session_id}/close",
    response_model=DeliverySessionResponse,
)
def close_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        reconciliation = delivery_reconciliation.calculate_reconciliation(db, session_id)
        return delivery_service.close_session(
            db,
            session_id,
            reconciliation["is_balanced"],
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSessionStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SessionAlreadyClosedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SessionNotBalancedError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{session_id}/checklist",
    response_model=DeliveryChecklistResponse,
)
def get_checklist(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        session = delivery_service.get_session(db, session_id)
        deliveries = (
            db.query(delivery_service.DailyDelivery)
            .filter(delivery_service.DailyDelivery.session_id == session_id)
            .all()
        )

        customers = []
        for d in deliveries:
            if d.customer:
                customers.append(
                    ChecklistCustomer(
                        customer_id=d.customer_id,
                        customer_name=d.customer.customer_name,
                        address=d.customer.address,
                        phone=d.customer.primary_phone,
                        milk_type=d.milk_type.milk_name if d.milk_type else "Unknown",
                        quantity=d.planned_quantity,
                    )
                )

        return DeliveryChecklistResponse(
            session_id=session_id,
            route_name=session.route.route_name if session.route else None,
            delivery_date=session.delivery_date,
            shift=session.shift,
            total_expected=len(deliveries),
            customers=customers,
        )
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{session_id}/reconciliation",
    response_model=ReconciliationResponse,
)
def get_reconciliation(
    session_id: int,
    db: Session = Depends(get_db),
):
    reconciliation = delivery_reconciliation.calculate_reconciliation(db, session_id)
    return ReconciliationResponse(
        session_id=session_id,
        **reconciliation,
    )


@router.get(
    "/{session_id}/reconciliation/summary",
    response_model=dict,
)
def get_reconciliation_summary(
    session_id: int,
    db: Session = Depends(get_db),
):
    return delivery_reconciliation.get_session_summary(db, session_id)


@router.get(
    "/{session_id}/reconciliation/customers",
    response_model=dict,
)
def get_customer_status(
    session_id: int,
    db: Session = Depends(get_db),
):
    customers = delivery_reconciliation.get_customer_delivery_status(db, session_id)
    return {
        "session_id": session_id,
        "customers": customers,
        "total": len(customers),
    }


@router.post(
    "/{session_id}/reconciliation/validate",
    response_model=dict,
)
def validate_reconciliation(
    session_id: int,
    db: Session = Depends(get_db),
):
    return delivery_reconciliation.validate_reconciliation(db, session_id)


@router.post(
    "/{session_id}/reconciliation/submit",
    response_model=ReconciliationResponse,
)
def submit_reconciliation(
    session_id: int,
    total_cash_collected: float,
    cash_sales: list[dict] = [],
    returned_milk: float = 0,
    returned_reasons: list[dict] | None = None,
    token_sheets_collected: list[dict] | None = None,
    remarks: str | None = None,
    db: Session = Depends(get_db),
):
    if total_cash_collected < 0:
        raise HTTPException(
            status_code=400,
            detail="Total cash collected cannot be negative",
        )
    if returned_milk < 0:
        raise HTTPException(
            status_code=400,
            detail="Returned milk cannot be negative",
        )

    reconciliation = delivery_reconciliation.submit_reconciliation(
        db,
        session_id,
        total_cash_collected,
        cash_sales,
        returned_milk,
        returned_reasons,
        token_sheets_collected,
        remarks,
    )
    return ReconciliationResponse(
        session_id=session_id,
        loaded_milk=reconciliation["loaded_milk"],
        token_registered=reconciliation["token_registered"],
        cash_sales=reconciliation["cash_sales"],
        returned_milk=reconciliation["returned_milk"],
        total_accounted=reconciliation["total_accounted"],
        difference=reconciliation["difference"],
        is_balanced=reconciliation["is_balanced"],
        status=reconciliation["status"],
    )


@router.post(
    "/{session_id}/reconciliation/cash-sales",
    response_model=dict,
    status_code=201,
)
def add_cash_sale(
    session_id: int,
    customer_name: str,
    customer_phone: str | None,
    milk_type_id: int,
    quantity: float,
    amount: float,
    payment_method: str = "CASH",
    db: Session = Depends(get_db),
):
    return delivery_reconciliation.add_cash_sale(
        db,
        session_id,
        customer_name,
        customer_phone,
        milk_type_id,
        quantity,
        amount,
        payment_method,
    )


@router.delete(
    "/{session_id}/reconciliation/cash-sales/{cash_sale_id}",
    response_model=dict,
)
def remove_cash_sale(
    session_id: int,
    cash_sale_id: int,
    db: Session = Depends(get_db),
):
    success = delivery_reconciliation.remove_cash_sale(db, session_id, cash_sale_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cash sale not found")
    return {"message": "Cash sale removed successfully"}


@router.get(
    "/{session_id}/report",
    response_model=SessionReportResponse,
)
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
):
    summary = delivery_reconciliation.get_session_summary(db, session_id)
    return SessionReportResponse(
        session_id=session_id,
        route_name=summary.get("route_name"),
        delivery_date=summary.get("delivery_date"),
        shift=summary.get("shift"),
        summary=SessionReportSummary(**summary.get("summary", {})),
        milk_summary=SessionReportMilkSummary(**summary.get("milk_summary", {})),
    )
