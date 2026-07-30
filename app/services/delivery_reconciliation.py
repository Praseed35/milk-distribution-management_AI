from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession

from app.constants.statuses import DeliveryStatus


def calculate_reconciliation(
    db: Session,
    session_id: int,
) -> dict:
    """
    Calculate reconciliation for a delivery session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        Reconciliation dict with loaded, token, cash, returned, total, difference, is_balanced.
    """
    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        return {
            "loaded_milk": 0,
            "token_registered": 0,
            "cash_sales": 0,
            "returned_milk": 0,
            "total_accounted": 0,
            "difference": 0,
            "is_balanced": False,
            "status": "PENDING",
        }

    deliveries = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.session_id == session_id,
                DailyDelivery.is_active == True,
            )
        )
        .all()
    )

    token_registered = sum(
        float(d.delivered_quantity)
        for d in deliveries
        if d.delivery_status == DeliveryStatus.DELIVERED
    )

    cash_sales = sum(
        float(d.delivered_quantity)
        for d in deliveries
        if d.delivery_status == DeliveryStatus.CASH_SALE
    )

    returned_milk = float(session.total_returned_milk or 0)

    loaded_milk = float(session.total_milk_loaded or 0)

    total_accounted = token_registered + cash_sales + returned_milk

    difference = loaded_milk - total_accounted

    is_balanced = abs(difference) < 0.01

    status = "BALANCED" if is_balanced else "UNBALANCED"

    return {
        "loaded_milk": loaded_milk,
        "token_registered": token_registered,
        "cash_sales": cash_sales,
        "returned_milk": returned_milk,
        "total_accounted": total_accounted,
        "difference": difference,
        "is_balanced": is_balanced,
        "status": status,
    }


def submit_reconciliation(
    db: Session,
    session_id: int,
    total_cash_collected: float,
    cash_sales: list[dict],
    returned_milk: float,
    returned_reasons: list[dict] | None = None,
    token_sheets_collected: list[dict] | None = None,
    remarks: str | None = None,
) -> dict:
    """
    Submit reconciliation details for a session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        total_cash_collected: Total cash collected.
        cash_sales: List of cash sale dicts.
        returned_milk: Returned milk in liters.
        returned_reasons: List of return reason dicts.
        token_sheets_collected: List of token sheet collection dicts.
        remarks: Additional remarks.

    Returns:
        Updated reconciliation dict.
    """
    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}

    session.total_cash_sales = total_cash_collected
    session.total_returned_milk = returned_milk

    db.commit()

    return calculate_reconciliation(db, session_id)


def validate_reconciliation(
    db: Session,
    session_id: int,
) -> dict:
    """
    Validate if a session can be closed.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        Validation result dict.
    """
    reconciliation = calculate_reconciliation(db, session_id)

    issues = []

    if not reconciliation["is_balanced"]:
        issues.append(
            {
                "code": "RECONCILIATION_MISMATCH",
                "message": f"Reconciliation mismatch: {reconciliation['difference']:.2f} liters",
                "severity": "ERROR",
            }
        )

    deliveries = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.session_id == session_id,
                DailyDelivery.is_active == True,
            )
        )
        .all()
    )

    pending_tokens = [
        d for d in deliveries
        if d.delivery_status == DeliveryStatus.PENDING_TOKEN
    ]
    if pending_tokens:
        issues.append(
            {
                "code": "PENDING_TOKENS",
                "message": f"{len(pending_tokens)} customer(s) have pending token sheets",
                "severity": "WARNING",
            }
        )

    can_close = reconciliation["is_balanced"]

    return {
        "can_close": can_close,
        "is_balanced": reconciliation["is_balanced"],
        "issues": issues,
    }


def get_session_summary(
    db: Session,
    session_id: int,
) -> dict:
    """
    Get delivery summary for a session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        Session summary dict.
    """
    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}

    deliveries = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.session_id == session_id,
                DailyDelivery.is_active == True,
            )
        )
        .all()
    )

    total_customers = len(deliveries)
    delivered = len([d for d in deliveries if d.delivery_status == DeliveryStatus.DELIVERED])
    pending_token = len([d for d in deliveries if d.delivery_status == DeliveryStatus.PENDING_TOKEN])
    cash_sale = len([d for d in deliveries if d.delivery_status == DeliveryStatus.CASH_SALE])
    not_delivered = len([d for d in deliveries if d.delivery_status == DeliveryStatus.NOT_DELIVERED])

    return {
        "session_id": session_id,
        "route_name": session.route.route_name if session.route else None,
        "delivery_date": session.delivery_date,
        "shift": session.shift,
        "summary": {
            "total_customers": total_customers,
            "delivered": delivered,
            "pending_token": pending_token,
            "cash_sale": cash_sale,
            "not_delivered": not_delivered,
        },
        "milk_summary": {
            "loaded": float(session.total_milk_loaded or 0),
            "token_registered": float(session.total_token_registered or 0),
            "cash_sales": float(session.total_cash_sales or 0),
            "returned": float(session.total_returned_milk or 0),
        },
    }


def get_customer_delivery_status(
    db: Session,
    session_id: int,
) -> list[dict]:
    """
    Get status of all customers in a session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        List of customer delivery status dicts.
    """
    deliveries = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.session_id == session_id,
                DailyDelivery.is_active == True,
            )
        )
        .all()
    )

    result = []
    for delivery in deliveries:
        result.append(
            {
                "customer_id": delivery.customer_id,
                "customer_name": delivery.customer.customer_name if delivery.customer else None,
                "phone": delivery.customer.primary_phone if delivery.customer else None,
                "address": delivery.customer.address if delivery.customer else None,
                "milk_type": delivery.milk_type.milk_name if delivery.milk_type else None,
                "planned_quantity": delivery.planned_quantity,
                "status": delivery.delivery_status,
                "token_sheet": delivery.token_sheet_number,
                "cash_paid": float(delivery.cash_amount or 0),
                "is_on_schedule": delivery.delivery_source == "PLANNED",
            }
        )

    return result


def add_cash_sale(
    db: Session,
    session_id: int,
    customer_name: str,
    customer_phone: str | None,
    milk_type_id: int,
    quantity: float,
    amount: float,
    payment_method: str = "CASH",
) -> dict:
    """
    Add a cash sale during reconciliation.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        customer_name: Customer name.
        customer_phone: Customer phone.
        milk_type_id: Milk type ID.
        quantity: Quantity in liters.
        amount: Cash amount.
        payment_method: Payment method.

    Returns:
        Cash sale dict.
    """
    from app.models.milk_type import MilkType
    from app.models.customer import Customer

    session = db.query(DeliverySession).filter(DeliverySession.id == session_id).first()
    if not session:
        return {"error": "Session not found"}

    milk_type = db.query(MilkType).filter(MilkType.id == milk_type_id).first()

    cash_customer = (
        db.query(Customer)
        .filter(Customer.customer_code == "C_CASH")
        .first()
    )
    if not cash_customer:
        cash_customer = Customer(
            customer_code="C_CASH",
            customer_name="Cash Customer",
            primary_phone="0000000000",
            route_id=session.route_id,
            is_active=True,
        )
        db.add(cash_customer)
        db.flush()

    delivery = DailyDelivery(
        session_id=session_id,
        customer_id=cash_customer.id,
        milk_type_id=milk_type_id,
        planned_quantity=0,
        delivered_quantity=int(quantity),
        delivery_status=DeliveryStatus.CASH_SALE,
        delivery_source="UNPLANNED",
        cash_amount=amount,
        shift=session.shift,
        delivery_date=session.delivery_date,
        remarks=f"Cash sale: {customer_name}",
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return {
        "id": delivery.id,
        "session_id": session_id,
        "customer_name": customer_name,
        "milk_type_name": milk_type.milk_name if milk_type else None,
        "quantity": quantity,
        "amount": amount,
        "payment_method": payment_method,
        "created_at": delivery.created_at,
    }


def remove_cash_sale(
    db: Session,
    session_id: int,
    cash_sale_id: int,
) -> bool:
    """
    Remove a cash sale.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        cash_sale_id: Cash sale (delivery) ID.

    Returns:
        True if removed successfully.
    """
    delivery = (
        db.query(DailyDelivery)
        .filter(
            and_(
                DailyDelivery.id == cash_sale_id,
                DailyDelivery.session_id == session_id,
                DailyDelivery.delivery_status == DeliveryStatus.CASH_SALE,
            )
        )
        .first()
    )

    if not delivery:
        return False

    delivery.is_active = False
    db.commit()

    return True
