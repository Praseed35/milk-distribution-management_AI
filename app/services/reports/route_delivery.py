from datetime import date

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery
from app.models.route import Route
from app.models.customer import Customer


def get_route_delivery_report(
    db: Session,
    route_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    shift: str | None = None,
    restricted_route_id: int | None = None,
) -> list[dict]:
    if restricted_route_id == -1:
        return []

    query = (
        db.query(
            DeliverySession.route_id,
            Route.route_name,
            Route.route_code,
            DeliverySession.id.label("session_id"),
            DeliverySession.total_milk_loaded,
            DeliverySession.shift,
            DeliverySession.delivery_date,
        )
        .join(Route, DeliverySession.route_id == Route.id)
        .filter(Route.is_active == True)
        .filter(DeliverySession.is_active == True)
    )

    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    elif restricted_route_id is not None:
        query = query.filter(DeliverySession.route_id == restricted_route_id)

    if date_from:
        query = query.filter(DeliverySession.delivery_date >= date_from)
    if date_to:
        query = query.filter(DeliverySession.delivery_date <= date_to)
    if shift:
        query = query.filter(DeliverySession.shift == shift)

    sessions = query.all()

    route_map: dict[int, dict] = {}
    for s in sessions:
        if s.route_id not in route_map:
            route_map[s.route_id] = {
                "route_id": s.route_id,
                "route_name": s.route_name,
                "route_code": s.route_code,
                "session_count": 0,
                "delivery_count": 0,
                "total_loaded_quantity": 0.0,
                "total_delivered_quantity": 0.0,
                "total_cash_collected": 0.0,
                "total_token_registered": 0.0,
                "total_returned_quantity": 0.0,
                "shortage_surplus": 0.0,
                "is_balanced": False,
            }
        route_map[s.route_id]["session_count"] += 1
        route_map[s.route_id]["total_loaded_quantity"] += float(s.total_milk_loaded or 0)

    session_ids = [s.session_id for s in sessions]
    if session_ids:
        deliveries = (
            db.query(
                DailyDelivery.session_id,
                DailyDelivery.delivery_status,
                DailyDelivery.delivered_quantity,
                DailyDelivery.cash_amount,
                DailyDelivery.delivery_date,
                DailyDelivery.shift,
            )
            .filter(DailyDelivery.session_id.in_(session_ids))
            .filter(DailyDelivery.is_active == True)
            .all()
        )

        for d in deliveries:
            route_for_delivery = None
            for s in sessions:
                if s.session_id == d.session_id:
                    route_for_delivery = s.route_id
                    break
            if route_for_delivery is None:
                continue

            r = route_map[route_for_delivery]
            if d.delivery_status in ("DELIVERED", "CASH_SALE"):
                r["total_delivered_quantity"] += float(d.delivered_quantity or 0)
            if d.delivery_status == "CASH_SALE":
                r["total_cash_collected"] += float(d.cash_amount or 0)
            if d.delivery_status == "DELIVERED":
                r["total_token_registered"] += float(d.delivered_quantity or 0)
            r["delivery_count"] += 1

    result = []
    for r in route_map.values():
        r["total_returned_quantity"] = max(0.0, r["total_loaded_quantity"] - r["total_delivered_quantity"])
        r["shortage_surplus"] = r["total_loaded_quantity"] - r["total_returned_quantity"] - r["total_delivered_quantity"]
        r["is_balanced"] = abs(r["shortage_surplus"]) < 0.01
        result.append(r)

    return result
