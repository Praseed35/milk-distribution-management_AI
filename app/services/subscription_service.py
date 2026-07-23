from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.subscription import Subscription

from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate

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


def create(
        db: Session,
        subscription: SubscriptionCreate
) -> Subscription:

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == subscription.customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise CustomerNotFoundError()

    if not customer.is_active:
        raise InactiveCustomerError()

    milk_type = (
        db.query(MilkType)
        .filter(
            MilkType.id == subscription.milk_type_id,
            MilkType.is_active == True
        )
        .first()
    )

    if not milk_type:
        raise MilkTypeError()

    if not milk_type.is_active:
        raise InactiveMilkTypeError()

    if subscription.morning_quantity == 0 and subscription.evening_quantity == 0:
        raise InvalidSubscriptionQuantityError()

    existing_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.customer_id == subscription.customer_id,
            Subscription.milk_type_id == subscription.milk_type_id,
            Subscription.is_active == True
        )
        .first()
    )

    if existing_subscription:
        raise DuplicateSubscriptionError(
            subscription.customer_id,
            subscription.milk_type_id
        )

    new_subscription = Subscription(
        customer_id=subscription.customer_id,
        milk_type_id=subscription.milk_type_id,
        morning_quantity=subscription.morning_quantity,
        evening_quantity=subscription.evening_quantity,
        status=subscription.status,
        remarks=subscription.remarks
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription


def get_all(
    db: Session
) -> list[dict]:

    results = (
        db.query(
            Subscription.id,
            Subscription.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Route.route_name,
            MilkType.milk_name.label('milk_type_name'),
            MilkType.volume_ml.label('milk_type_volume'),
            Subscription.morning_quantity,
            Subscription.evening_quantity,
            Subscription.status,
            Subscription.is_active
        )
        .join(Customer, Subscription.customer_id == Customer.id)
        .join(Route, Customer.route_id == Route.id)
        .join(MilkType, Subscription.milk_type_id == MilkType.id)
        .filter(Subscription.is_active == True)
        .all()
    )

    return results


def get_by_id(
        db: Session,
        subscription_id: int
) -> dict:

    result = (
        db.query(
            Subscription.id,
            Subscription.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Customer.primary_phone,
            MilkType.id.label('milk_type_id'),
            MilkType.milk_name,
            MilkType.volume_ml,
            Subscription.morning_quantity,
            Subscription.evening_quantity,
            Subscription.status,
            Subscription.start_date,
            Subscription.end_date,
            Subscription.remarks,
            Subscription.is_active,
            Subscription.created_at,
            Subscription.updated_at
        )
        .join(Customer, Subscription.customer_id == Customer.id)
        .join(MilkType, Subscription.milk_type_id == MilkType.id)
        .filter(
            Subscription.id == subscription_id,
            Subscription.is_active == True
        )
        .first()
    )

    if not result:
        raise SubscriptionNotFoundError()

    return {
        'id': result.id,
        'customer': {
            'id': result.customer_id,
            'customer_code': result.customer_code,
            'customer_name': result.customer_name,
            'primary_phone': result.primary_phone
        },
        'milk_type': {
            'id': result.milk_type_id,
            'milk_name': result.milk_name,
            'volume_ml': result.volume_ml
        },
        'morning_quantity': result.morning_quantity,
        'evening_quantity': result.evening_quantity,
        'status': result.status,
        'start_date': result.start_date,
        'end_date': result.end_date,
        'remarks': result.remarks,
        'is_active': result.is_active,
        'created_at': result.created_at,
        'updated_at': result.updated_at
    }


def get_by_customer_id(
        db: Session,
        customer_id: int
) -> list[dict]:

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise CustomerNotFoundError()

    results = (
        db.query(
            Subscription.id,
            Subscription.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Route.route_name,
            MilkType.milk_name.label('milk_type_name'),
            MilkType.volume_ml.label('milk_type_volume'),
            Subscription.morning_quantity,
            Subscription.evening_quantity,
            Subscription.status,
            Subscription.is_active
        )
        .join(Customer, Subscription.customer_id == Customer.id)
        .join(Route, Customer.route_id == Route.id)
        .join(MilkType, Subscription.milk_type_id == MilkType.id)
        .filter(
            Subscription.customer_id == customer_id,
            Subscription.is_active == True
        )
        .all()
    )

    return results


def update_by_id(
        db: Session,
        subscription_id: int,
        subscription: SubscriptionUpdate
) -> Subscription:

    subscription_to_update = (
        db.query(Subscription)
        .filter(
            Subscription.id == subscription_id,
            Subscription.is_active == True
        )
        .first()
    )

    if not subscription_to_update:
        raise SubscriptionNotFoundError()

    if subscription.morning_quantity is not None:
        subscription_to_update.morning_quantity = subscription.morning_quantity

    if subscription.evening_quantity is not None:
        subscription_to_update.evening_quantity = subscription.evening_quantity

    if subscription.status is not None:
        subscription_to_update.status = subscription.status

    if subscription.remarks is not None:
        subscription_to_update.remarks = subscription.remarks

    if (subscription_to_update.morning_quantity == 0 and
            subscription_to_update.evening_quantity == 0):
        raise InvalidSubscriptionQuantityError()

    db.commit()
    db.refresh(subscription_to_update)

    return subscription_to_update


def deactivate_by_id(
    db: Session,
    subscription_id: int
) -> Subscription:

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

    subscription.is_active = False
    subscription.status = "INACTIVE"

    db.commit()
    db.refresh(subscription)

    return subscription
