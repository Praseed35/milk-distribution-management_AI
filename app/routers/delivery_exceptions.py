from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.delivery_exception import (
    DeliveryExceptionCreate,
    DeliveryExceptionResponse,
    DeliveryExceptionUpdate,
    DeliveryExceptionListResponse,
    DeliveryExceptionDetailResponse
)

from app.services import delivery_exception_service

from app.exceptions.subscription import SubscriptionNotFoundError

from app.exceptions.delivery_exception import (
    DeliveryExceptionNotFoundError,
    DeliveryExceptionOverlapError,
    InvalidDeliveryExceptionDateError,
    InactiveSubscriptionError,
    DeliveryExceptionAlreadyInactiveError
)

router = APIRouter(
    prefix="/delivery-exceptions",
    tags=["Delivery Exceptions"]
)


@router.post(
    "/",
    response_model=DeliveryExceptionResponse,
    status_code=201
)
def create_delivery_exception(
    exception: DeliveryExceptionCreate,
    db: Session = Depends(get_db)
):

    try:

        return delivery_exception_service.create(
            db,
            exception
        )

    except SubscriptionNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InactiveSubscriptionError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except InvalidDeliveryExceptionDateError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DeliveryExceptionOverlapError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[DeliveryExceptionListResponse]
)
def get_all_delivery_exceptions(
    db: Session = Depends(get_db)
):
    return delivery_exception_service.get_all(
        db
    )


@router.get(
    "/{exception_id}",
    response_model=DeliveryExceptionDetailResponse
)
def get_delivery_exception_by_id(
    exception_id: int,
    db: Session = Depends(get_db)
):
    try:
        return delivery_exception_service.get_by_id(
            db,
            exception_id)
    except DeliveryExceptionNotFoundError as e:
         raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/subscription/{subscription_id}",
    response_model=list[DeliveryExceptionResponse]
)
def get_delivery_exceptions_by_subscription_id(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    try:
        return delivery_exception_service.get_by_subscription_id(
            db,
            subscription_id
        )
    except SubscriptionNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{exception_id}",
    response_model=DeliveryExceptionResponse
)
def update_delivery_exception_by_id(
    exception_id: int,
    exception: DeliveryExceptionUpdate,
    db: Session = Depends(get_db)
):
    try:
        return delivery_exception_service.update_by_id(
            db,
            exception_id,
            exception
        )

    except DeliveryExceptionNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InvalidDeliveryExceptionDateError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DeliveryExceptionOverlapError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{exception_id}",
    response_model=DeliveryExceptionResponse
)
def delete_delivery_exception_by_id(
    exception_id: int,
    db: Session = Depends(get_db)
):
    try:
        return delivery_exception_service.deactivate_by_id(
            db,
            exception_id
        )
    except DeliveryExceptionNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except DeliveryExceptionAlreadyInactiveError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
