from datetime import date

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery


def get_operational_dashboard(
    db: Session,
    restricted_route_id: int | None = None,
) -> dict:
    today = date.today()

    session_query = db.query(DeliverySession).filter(
        DeliverySession.delivery_date == today,
        DeliverySession.is_active == True,
    )
    if restricted_route_id and restricted_route_id > 0:
        session_query = session_query.filter(DeliverySession.route_id == restricted_route_id)
    elif restricted_route_id == -1:
        return _empty_dashboard(today)

    sessions = session_query.all()

    total_sessions = len(sessions)
    total_milk_loaded = sum(float(s.total_milk_loaded or 0) for s in sessions)

    session_ids = [s.id for s in sessions]

    deliveries_by_status = {
        "DELIVERED": 0, "PENDING_TOKEN": 0, "CASH_SALE": 0,
        "NOT_DELIVERED": 0, "CANCELLED": 0,
    }
    total_milk_delivered = 0.0
    total_cash_collected = 0.0
    pending_token_count = 0

    if session_ids:
        deliveries = (
            db.query(
                DailyDelivery.delivery_status,
                DailyDelivery.delivered_quantity,
                DailyDelivery.cash_amount,
            )
            .filter(DailyDelivery.session_id.in_(session_ids))
            .filter(DailyDelivery.is_active == True)
            .all()
        )

        for d in deliveries:
            status = d.delivery_status
            if status in deliveries_by_status:
                deliveries_by_status[status] += 1
            if status in ("DELIVERED", "CASH_SALE"):
                total_milk_delivered += float(d.delivered_quantity or 0)
            if status == "CASH_SALE":
                total_cash_collected += float(d.cash_amount or 0)
            if status == "PENDING_TOKEN":
                pending_token_count += 1

    unclosed_query = db.query(DeliverySession).filter(
        DeliverySession.delivery_date < today,
        DeliverySession.status != "CLOSED",
        DeliverySession.is_active == True,
    )
    if restricted_route_id and restricted_route_id > 0:
        unclosed_query = unclosed_query.filter(DeliverySession.route_id == restricted_route_id)
    unclosed_sessions = unclosed_query.count()

    unbalanced_query = db.query(DeliverySession).filter(
        DeliverySession.delivery_date == today,
        DeliverySession.reconciliation_status == "UNBALANCED",
        DeliverySession.is_active == True,
    )
    if restricted_route_id and restricted_route_id > 0:
        unbalanced_query = unbalanced_query.filter(DeliverySession.route_id == restricted_route_id)
    unbalanced_sessions = unbalanced_query.count()

    completed_not_closed_q = db.query(DeliverySession).filter(
        DeliverySession.delivery_date == today,
        DeliverySession.status == "COMPLETED",
        DeliverySession.is_active == True,
    )
    if restricted_route_id and restricted_route_id > 0:
        completed_not_closed_q = completed_not_closed_q.filter(DeliverySession.route_id == restricted_route_id)
    completed_not_closed = completed_not_closed_q.count()

    return {
        "report_date": today,
        "total_sessions": total_sessions,
        "total_milk_loaded": total_milk_loaded,
        "total_milk_delivered": total_milk_delivered,
        "total_cash_collected": total_cash_collected,
        "deliveries_by_status": deliveries_by_status,
        "pending_token_count": pending_token_count,
        "unclosed_sessions": unclosed_sessions,
        "unbalanced_sessions": unbalanced_sessions,
        "completed_not_closed": completed_not_closed,
    }


def _empty_dashboard(today: date) -> dict:
    return {
        "report_date": today,
        "total_sessions": 0,
        "total_milk_loaded": 0.0,
        "total_milk_delivered": 0.0,
        "total_cash_collected": 0.0,
        "deliveries_by_status": {"DELIVERED": 0, "PENDING_TOKEN": 0, "CASH_SALE": 0, "NOT_DELIVERED": 0, "CANCELLED": 0},
        "pending_token_count": 0,
        "unclosed_sessions": 0,
        "unbalanced_sessions": 0,
        "completed_not_closed": 0,
    }
