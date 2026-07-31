from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.subscription import Subscription
from app.models.delivery_exception import DeliveryException

from app.schemas.delivery_exception import (
    DeliveryExceptionCreate,
    DeliveryExceptionUpdate
)

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.subscription import SubscriptionNotFoundError

from app.exceptions.delivery_exception import (
    DeliveryExceptionNotFoundError,
    DeliveryExceptionOverlapError,
    InvalidDeliveryExceptionDateError,
    InactiveSubscriptionError,
    DeliveryExceptionAlreadyInactiveError
)


def _check_overlap(
    db: Session,
    subscription_id: int,
    start_date: datetime,
    end_date: datetime | None,
    shift: str | None = None,
    exclude_id: int | None = None
):

    query = (
        db.query(DeliveryException)
        .filter(
            DeliveryException.subscription_id == subscription_id,
            DeliveryException.is_active == True,
            DeliveryException.start_date <= (end_date or start_date),
        )
    )

    if shift:
        query = query.filter(
            or_(
                DeliveryException.shift.is_(None),
                DeliveryException.shift == shift
            )
        )

    if end_date:
        query = query.filter(
            DeliveryException.end_date >= start_date
        )
    else:
        query = query.filter(
            DeliveryException.start_date == start_date
        )

    if exclude_id:
        query = query.filter(
            DeliveryException.id != exclude_id
        )

    return query.first()


def create(
    db: Session,
    exception: DeliveryExceptionCreate
) -> DeliveryException:

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == exception.subscription_id,
            Subscription.is_active == True
        )
        .first()
    )

    if not subscription:
        raise SubscriptionNotFoundError()

    if not subscription.is_active:
        raise InactiveSubscriptionError()

    if (exception.end_date and
            exception.end_date < exception.start_date):
        raise InvalidDeliveryExceptionDateError()

    existing = _check_overlap(
        db,
        exception.subscription_id,
        exception.start_date,
        exception.end_date,
        shift=exception.shift
    )

    if existing:
        raise DeliveryExceptionOverlapError(
            exception.subscription_id,
            str(exception.start_date.date()),
            str(exception.end_date.date()) if exception.end_date else str(exception.start_date.date())
        )

    new_exception = DeliveryException(
        subscription_id=exception.subscription_id,
        exception_type=exception.exception_type,
        shift=exception.shift,
        start_date=exception.start_date,
        end_date=exception.end_date,
        reason=exception.reason
    )

    db.add(new_exception)
    db.commit()
    db.refresh(new_exception)

    return new_exception


def get_all(
    db: Session
) -> list[dict]:

    results = (
        db.query(
            DeliveryException.id,
            DeliveryException.subscription_id,
            Customer.id.label('customer_id'),
            Customer.customer_code,
            Customer.customer_name,
            Route.route_name,
            DeliveryException.exception_type,
            DeliveryException.shift,
            DeliveryException.start_date,
            DeliveryException.end_date,
            DeliveryException.status,
            DeliveryException.is_active
        )
        .join(Subscription, DeliveryException.subscription_id == Subscription.id)
        .join(Customer, Subscription.customer_id == Customer.id)
        .join(Route, Customer.route_id == Route.id)
        .filter(DeliveryException.is_active == True)
        .all()
    )

    return results


def get_by_id(
    db: Session,
    exception_id: int
) -> dict:

    result = (
        db.query(
            DeliveryException.id,
            DeliveryException.subscription_id,
            Subscription.id.label('sub_id'),
            Customer.id.label('customer_id'),
            Customer.customer_code,
            Customer.customer_name,
            Customer.primary_phone,
            Subscription.morning_quantity,
            Subscription.evening_quantity,
            DeliveryException.exception_type,
            DeliveryException.shift,
            DeliveryException.start_date,
            DeliveryException.end_date,
            DeliveryException.reason,
            DeliveryException.status,
            DeliveryException.is_active,
            DeliveryException.created_at,
            DeliveryException.updated_at
        )
        .join(Subscription, DeliveryException.subscription_id == Subscription.id)
        .join(Customer, Subscription.customer_id == Customer.id)
        .filter(
            DeliveryException.id == exception_id,
            DeliveryException.is_active == True
        )
        .first()
    )

    if not result:
        raise DeliveryExceptionNotFoundError()

    return {
        'id': result.id,
        'subscription': {
            'id': result.sub_id,
            'customer': {
                'id': result.customer_id,
                'customer_code': result.customer_code,
                'customer_name': result.customer_name,
                'primary_phone': result.primary_phone
            },
            'morning_quantity': result.morning_quantity,
            'evening_quantity': result.evening_quantity
        },
        'exception_type': result.exception_type,
        'shift': result.shift,
        'start_date': result.start_date,
        'end_date': result.end_date,
        'reason': result.reason,
        'status': result.status,
        'is_active': result.is_active,
        'created_at': result.created_at,
        'updated_at': result.updated_at
    }


def get_by_subscription_id(
    db: Session,
    subscription_id: int
) -> list[DeliveryException]:

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id,
            Subscription.is_active == True
        )
        .first()
    )

    if not subscription:
        raise SubscriptionNotFoundError()

    results = (
        db.query(DeliveryException)
        .filter(
            DeliveryException.subscription_id == subscription_id,
            DeliveryException.is_active == True
        )
        .all()
    )

    return results


def update_by_id(
    db: Session,
    exception_id: int,
    exception: DeliveryExceptionUpdate
) -> DeliveryException:

    exception_to_update = (
        db.query(DeliveryException)
        .filter(
            DeliveryException.id == exception_id,
            DeliveryException.is_active == True
        )
        .first()
    )

    if not exception_to_update:
        raise DeliveryExceptionNotFoundError()

    if exception.exception_type is not None:
        exception_to_update.exception_type = exception.exception_type

    if "shift" in exception.model_fields_set:
        exception_to_update.shift = exception.shift

    if exception.start_date is not None:
        exception_to_update.start_date = exception.start_date

    if exception.end_date is not None:
        exception_to_update.end_date = exception.end_date

    if exception.reason is not None:
        exception_to_update.reason = exception.reason

    if exception.status is not None:
        exception_to_update.status = exception.status

    if (exception_to_update.end_date and
            exception_to_update.end_date < exception_to_update.start_date):
        raise InvalidDeliveryExceptionDateError()

    existing = _check_overlap(
        db,
        exception_to_update.subscription_id,
        exception_to_update.start_date,
        exception_to_update.end_date,
        shift=exception_to_update.shift,
        exclude_id=exception_id
    )

    if existing:
        raise DeliveryExceptionOverlapError(
            exception_to_update.subscription_id,
            str(exception_to_update.start_date.date()),
            str(exception_to_update.end_date.date()) if exception_to_update.end_date else str(exception_to_update.start_date.date())
        )

    db.commit()
    db.refresh(exception_to_update)

    return exception_to_update


def deactivate_by_id(
    db: Session,
    exception_id: int
) -> DeliveryException:

    exception = (
        db.query(DeliveryException)
        .filter(
            DeliveryException.id == exception_id,
            DeliveryException.is_active == True
        )
        .first()
    )

    if not exception:
        raise DeliveryExceptionNotFoundError()

    exception.is_active = False
    exception.status = "CANCELLED"

    db.commit()
    db.refresh(exception)

    return exception
