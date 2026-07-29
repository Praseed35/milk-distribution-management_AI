from datetime import date

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.payment import (
    BillGenerateRequest,
    BillStatusUpdate,
    CustomerBillListResponse,
    CustomerBillResponse,
    CustomerPaymentCreate,
    CustomerPaymentListResponse,
    CustomerPaymentResponse,
    CustomerPaymentUpdate,
    OutstandingBalanceResponse,
)

from app.services import payment_service

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.milk_type import MilkTypeError
from app.exceptions.payment import (
    BillAlreadyCancelledError,
    BillAlreadyPaidError,
    CustomerBillNotFoundError,
    CustomerPaymentNotFoundError,
    InvalidBillStatusError,
    InvalidPaymentModeError,
    InvalidPaymentTypeError,
    NoDeliveriesForBillError,
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# ─── Customer Payment Endpoints ───


@router.post(
    "/",
    response_model=CustomerPaymentResponse,
    status_code=201
)
def create_customer_payment(
    payment: CustomerPaymentCreate,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.create_payment(
            db,
            payment
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except (InvalidPaymentModeError, InvalidPaymentTypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except CustomerBillNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except (BillAlreadyPaidError, BillAlreadyCancelledError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[CustomerPaymentListResponse]
)
def get_all_customer_payments(
    customer_id: int | None = Query(default=None),
    payment_mode: str | None = Query(default=None),
    payment_type: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return payment_service.get_all_payments(
        db,
        customer_id=customer_id,
        payment_mode=payment_mode,
        payment_type=payment_type,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/{payment_id}",
    response_model=CustomerPaymentResponse
)
def get_customer_payment_by_id(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.get_payment_by_id(
            db,
            payment_id
        )
    except CustomerPaymentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/customer/{customer_id}",
    response_model=list[CustomerPaymentResponse]
)
def get_customer_payments_by_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.get_payments_by_customer(
            db,
            customer_id
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{payment_id}",
    response_model=CustomerPaymentResponse
)
def update_customer_payment(
    payment_id: int,
    payment: CustomerPaymentUpdate,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.update_payment(
            db,
            payment_id,
            payment
        )
    except CustomerPaymentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except InvalidPaymentModeError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{payment_id}",
    response_model=CustomerPaymentResponse
)
def deactivate_customer_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.deactivate_payment(
            db,
            payment_id
        )
    except CustomerPaymentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ─── Customer Bill Endpoints ───


@router.post(
    "/bills/generate",
    response_model=CustomerBillResponse,
    status_code=201
)
def generate_customer_bill(
    request: BillGenerateRequest,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.generate_bill(
            db,
            request
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except (MilkTypeError, NoDeliveriesForBillError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/bills/",
    response_model=list[CustomerBillListResponse]
)
def get_all_customer_bills(
    customer_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return payment_service.get_all_bills(
        db,
        customer_id=customer_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/bills/{bill_id}",
    response_model=CustomerBillResponse
)
def get_customer_bill_by_id(
    bill_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.get_bill_by_id(
            db,
            bill_id
        )
    except CustomerBillNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/bills/customer/{customer_id}",
    response_model=list[CustomerBillResponse]
)
def get_customer_bills_by_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.get_bills_by_customer(
            db,
            customer_id
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/bills/{bill_id}/status",
    response_model=CustomerBillResponse
)
def update_customer_bill_status(
    bill_id: int,
    status_update: BillStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.update_bill_status(
            db,
            bill_id,
            status_update
        )
    except CustomerBillNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except InvalidBillStatusError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ─── Outstanding Balance Endpoint ───


@router.get(
    "/outstanding/{customer_id}",
    response_model=OutstandingBalanceResponse
)
def get_customer_outstanding_balance(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        return payment_service.get_outstanding_balance(
            db,
            customer_id
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
