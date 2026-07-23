from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
    SubscriptionListResponse,
    SubscriptionDetailResponse
)

from app.services import subscription_service

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.milk_type import MilkTypeError

from app.exceptions.subscription import (
    DuplicateSubscriptionError,
    InactiveCustomerError,
    InactiveMilkTypeError,
    InvalidSubscriptionQuantityError,
    SubscriptionNotFoundError,
    SubscriptionAlreadyInactiveError
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=201
)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):

    try:

        return subscription_service.create(
            db,
            subscription
        )

    except CustomerNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InactiveCustomerError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except MilkTypeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InactiveMilkTypeError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except InvalidSubscriptionQuantityError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DuplicateSubscriptionError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[SubscriptionListResponse]
)
def get_all_subscriptions(
    db: Session = Depends(get_db)
):
    return subscription_service.get_all(
        db
    )


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionDetailResponse
)
def get_subscription_by_id(
    subscription_id: int,
    db: Session = Depends(get_db)

):
    try:
        return subscription_service.get_by_id(
            db,
            subscription_id)
    except SubscriptionNotFoundError as e:
         raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/customer/{customer_id}",
    response_model=list[SubscriptionListResponse]
)
def get_subscriptions_by_customer_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        return subscription_service.get_by_customer_id(
            db,
            customer_id
        )
    except CustomerNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def update_subscription_by_id(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    try:
        return subscription_service.update_by_id(
            db,
            subscription_id,
            subscription
        )

    except SubscriptionNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except InvalidSubscriptionQuantityError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def delete_subscription_by_id(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    try:
        return subscription_service.deactivate_by_id(
            db,
            subscription_id
        )
    except SubscriptionNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except SubscriptionAlreadyInactiveError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
