from datetime import date, timedelta

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession
from app.models.milk_type import MilkType


def get_customer_consumption_report(
    db: Session,
    customer_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    group_by: str = "day",
) -> dict:
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.is_active == True)
        .first()
    )
    if not customer:
        return None

    from app.services.reports.common import resolve_date_range
    frm, to = resolve_date_range(preset=None, from_date=date_from, to_date=date_to)

    query = (
        db.query(
            DeliverySession.delivery_date,
            DailyDelivery.milk_type_id,
            MilkType.milk_name,
            DailyDelivery.delivered_quantity,
            DailyDelivery.delivery_status,
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .join(MilkType, DailyDelivery.milk_type_id == MilkType.id)
        .filter(DailyDelivery.customer_id == customer_id)
        .filter(DailyDelivery.is_active == True)
        .filter(DeliverySession.is_active == True)
        .filter(DeliverySession.delivery_date >= frm)
        .filter(DeliverySession.delivery_date <= to)
        .filter(DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]))
        .order_by(DeliverySession.delivery_date)
    )

    rows = query.all()

    daily_data: dict[date, dict] = {}
    for r in rows:
        d = r.delivery_date
        if d not in daily_data:
            daily_data[d] = {"total": 0.0, "by_milk_type": {}}
        qty = float(r.delivered_quantity or 0)
        daily_data[d]["total"] += qty
        mt = r.milk_name or "Unknown"
        daily_data[d]["by_milk_type"][mt] = daily_data[d]["by_milk_type"].get(mt, 0) + qty

    items = []
    for d in sorted(daily_data.keys()):
        dd = daily_data[d]
        items.append({
            "date": d,
            "total_quantity": dd["total"],
            "by_milk_type": [{"milk_type": k, "quantity": v} for k, v in dd["by_milk_type"].items()],
        })

    total_consumption = sum(i["total_quantity"] for i in items)
    days_with_data = len(items)
    avg_daily = round(total_consumption / days_with_data, 2) if days_with_data else 0

    trend = {"period": "insufficient_data", "recent_7day_avg": None, "preceding_21day_avg": None, "change_percentage": None}
    if days_with_data >= 14:
        cutoff = to - timedelta(days=7)
        recent = [i for i in items if i["date"] > cutoff]
        preceding = [i for i in items if i["date"] <= cutoff]
        if recent and preceding:
            recent_avg = sum(i["total_quantity"] for i in recent) / len(recent)
            preceding_avg = sum(i["total_quantity"] for i in preceding) / len(preceding)
            change = round((recent_avg - preceding_avg) / preceding_avg * 100, 2) if preceding_avg else 0
            if change > 10:
                period = "increasing"
            elif change < -10:
                period = "declining"
            else:
                period = "stable"
            trend = {
                "period": period,
                "recent_7day_avg": round(recent_avg, 2),
                "preceding_21day_avg": round(preceding_avg, 2),
                "change_percentage": change,
            }

    return {
        "customer_id": customer_id,
        "customer_name": customer.customer_name,
        "date_from": frm,
        "date_to": to,
        "group_by": group_by,
        "total_consumption": total_consumption,
        "average_daily": avg_daily,
        "days_with_data": days_with_data,
        "trend": trend,
        "items": items,
    }
