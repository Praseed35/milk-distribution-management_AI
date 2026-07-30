from datetime import date

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.delivery_exception import DeliveryException
from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery
from app.models.employee import Employee
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.subscription import Subscription

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

from app.constants.statuses import SessionStatus


VALID_SESSION_TRANSITIONS = {
    SessionStatus.PLANNED: [SessionStatus.STARTED],
    SessionStatus.STARTED: [SessionStatus.COMPLETED],
    SessionStatus.COMPLETED: [SessionStatus.CLOSED],
    SessionStatus.CLOSED: [SessionStatus.COMPLETED],
}


def create_session(
    db: Session,
    route_id: int,
    delivery_date: date,
    shift: str,
    delivery_partner_id: int,
) -> DeliverySession:
    """
    Create a new delivery session.

    Args:
        db: SQLAlchemy database session.
        route_id: Route ID.
        delivery_date: Delivery date.
        shift: MORNING or EVENING.
        delivery_partner_id: Employee ID for delivery partner.

    Returns:
        Newly created DeliverySession.

    Raises:
        RouteNotFoundError: If route not found.
        EmployeeNotFoundError: If employee not found.
        SessionAlreadyExistsError: If session exists for route/date/shift.
    """
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise RouteNotFoundError(route_id)

    employee = db.query(Employee).filter(Employee.id == delivery_partner_id).first()
    if not employee:
        raise EmployeeNotFoundError(delivery_partner_id)

    existing_session = (
        db.query(DeliverySession)
        .filter(
            and_(
                DeliverySession.route_id == route_id,
                DeliverySession.delivery_date == delivery_date,
                DeliverySession.shift == shift,
                DeliverySession.is_active == True,
            )
        )
        .first()
    )
    if existing_session:
        raise SessionAlreadyExistsError(route_id, str(delivery_date), shift)

    session = DeliverySession(
        route_id=route_id,
        delivery_date=delivery_date,
        shift=shift,
        delivery_partner_id=delivery_partner_id,
        status=SessionStatus.PLANNED,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(db: Session, session_id: int) -> DeliverySession:
    """
    Get a delivery session by ID.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        DeliverySession.

    Raises:
        SessionNotFoundError: If session not found.
    """
    session = (
        db.query(DeliverySession)
        .filter(
            and_(
                DeliverySession.id == session_id,
                DeliverySession.is_active == True,
            )
        )
        .first()
    )
    if not session:
        raise SessionNotFoundError(session_id)
    return session


def list_sessions(
    db: Session,
    route_id: int | None = None,
    delivery_date: date | None = None,
    shift: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[DeliverySession], int]:
    """
    List delivery sessions with filters.

    Args:
        db: SQLAlchemy database session.
        route_id: Optional route filter.
        delivery_date: Optional date filter.
        shift: Optional shift filter.
        status: Optional status filter.
        skip: Pagination offset.
        limit: Pagination limit.

    Returns:
        Tuple of (sessions, total count).
    """
    query = db.query(DeliverySession).filter(DeliverySession.is_active == True)

    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    if delivery_date:
        query = query.filter(DeliverySession.delivery_date == delivery_date)
    if shift:
        query = query.filter(DeliverySession.shift == shift)
    if status:
        query = query.filter(DeliverySession.status == status)

    total = query.count()
    sessions = query.offset(skip).limit(limit).all()

    return sessions, total


def record_dispatch(
    db: Session,
    session_id: int,
    total_milk_loaded: float,
) -> DeliverySession:
    """
    Record milk dispatch for a session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        total_milk_loaded: Total milk loaded in liters.

    Returns:
        Updated DeliverySession.

    Raises:
        SessionNotFoundError: If session not found.
        InvalidSessionStatusError: If session not in PLANNED status.
        DispatchAlreadyRecordedError: If dispatch already recorded.
    """
    session = get_session(db, session_id)

    if session.status != SessionStatus.PLANNED:
        raise InvalidSessionStatusError(session.status, SessionStatus.PLANNED)

    if session.total_milk_loaded > 0:
        raise DispatchAlreadyRecordedError(session_id)

    session.total_milk_loaded = total_milk_loaded
    session.status = SessionStatus.STARTED

    db.commit()
    db.refresh(session)

    return session


def start_session(
    db: Session,
    session_id: int,
    total_milk_loaded: float,
) -> DeliverySession:
    """
    Start a delivery session (record dispatch and start).

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        total_milk_loaded: Total milk loaded in liters.

    Returns:
        Updated DeliverySession.

    Raises:
        SessionNotFoundError: If session not found.
        InvalidSessionStatusError: If session not in PLANNED status.
        DispatchAlreadyRecordedError: If dispatch already recorded.
    """
    return record_dispatch(db, session_id, total_milk_loaded)


def close_session(
    db: Session,
    session_id: int,
    is_balanced: bool,
) -> DeliverySession:
    """
    Close a delivery session.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.
        is_balanced: Whether reconciliation is balanced.

    Returns:
        Updated DeliverySession.

    Raises:
        SessionNotFoundError: If session not found.
        InvalidSessionStatusError: If session not in COMPLETED status.
        SessionAlreadyClosedError: If session already closed.
        SessionNotBalancedError: If reconciliation not balanced.
    """
    session = get_session(db, session_id)

    if session.status == SessionStatus.CLOSED:
        raise SessionAlreadyClosedError(session_id)

    if session.status != SessionStatus.COMPLETED:
        raise InvalidSessionStatusError(session.status, SessionStatus.COMPLETED)

    if not is_balanced:
        from app.services.delivery_reconciliation import calculate_reconciliation

        reconciliation = calculate_reconciliation(db, session_id)
        raise SessionNotBalancedError(session_id, float(reconciliation["difference"]))

    session.status = SessionStatus.CLOSED
    session.reconciliation_status = "BALANCED"

    db.commit()
    db.refresh(session)

    return session


def generate_delivery_list(
    db: Session,
    session_id: int,
) -> list[DailyDelivery]:
    """
    Generate delivery list for a session based on subscriptions and exceptions.

    Args:
        db: SQLAlchemy database session.
        session_id: Session ID.

    Returns:
        List of DailyDelivery records created.
    """
    session = get_session(db, session_id)

    subscriptions = (
        db.query(Subscription)
        .join(Customer, Subscription.customer_id == Customer.id)
        .filter(
            and_(
                Customer.route_id == session.route_id,
                Customer.is_active == True,
                Subscription.is_active == True,
            )
        )
        .all()
    )

    today = session.delivery_date
    exceptions = (
        db.query(DeliveryException)
        .filter(
            and_(
                DeliveryException.exception_date == today,
                DeliveryException.is_active == True,
            )
        )
        .all()
    )

    exception_customer_ids = {exc.customer_id for exc in exceptions}

    deliveries = []
    for sub in subscriptions:
        if sub.customer_id in exception_customer_ids:
            continue

        customer = db.query(Customer).filter(Customer.id == sub.customer_id).first()
        if not customer or not customer.is_active:
            continue

        milk_type = db.query(MilkType).filter(MilkType.id == sub.milk_type_id).first()
        if not milk_type or not milk_type.is_active:
            continue

        delivery = DailyDelivery(
            session_id=session_id,
            customer_id=sub.customer_id,
            milk_type_id=sub.milk_type_id,
            planned_quantity=sub.quantity,
            delivered_quantity=0,
            delivery_status="PLANNED",
            delivery_source="PLANNED",
            shift=session.shift,
            delivery_date=session.delivery_date,
        )

        db.add(delivery)
        deliveries.append(delivery)

    db.commit()

    for delivery in deliveries:
        db.refresh(delivery)

    return deliveries
