from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery

MIN_HISTORY_DAYS = 14
LOOKBACK_DAYS = 90
DEFAULT_HORIZON = 7
MAX_HORIZON = 30
WEEKDAY_OCCURRENCES = 4
MOVING_BLEND_WEIGHT = 0.3
TREND_CAP = 0.25
Z_SCORE = 1.28
RESIDUAL_WINDOW = 14

INSUFFICIENT_MESSAGE = (
    "Insufficient history for a full forecast (need at least 14 days); "
    "showing available historical average."
)


def forecast_demand(
    db: Session,
    route_id: int | None = None,
    milk_type_id: int | None = None,
    horizon_days: int = DEFAULT_HORIZON,
) -> dict:
    today = date.today()
    lookback_start = today - timedelta(days=LOOKBACK_DAYS)

    query = (
        db.query(
            DeliverySession.delivery_date,
            DailyDelivery.delivered_quantity,
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .filter(DailyDelivery.is_active == True)
        .filter(DeliverySession.is_active == True)
        .filter(DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]))
        .filter(DeliverySession.delivery_date >= lookback_start)
        .filter(DeliverySession.delivery_date <= today)
    )
    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    if milk_type_id:
        query = query.filter(DailyDelivery.milk_type_id == milk_type_id)

    rows = query.all()

    daily: dict[date, float] = {}
    for r in rows:
        daily[r.delivery_date] = daily.get(r.delivery_date, 0.0) + float(r.delivered_quantity or 0)

    history_dates = sorted(daily.keys())

    date_from = today + timedelta(days=1)
    date_to = today + timedelta(days=horizon_days)
    targets = [date_from + timedelta(days=i) for i in range(horizon_days)]

    if len(history_dates) < MIN_HISTORY_DAYS:
        return _insufficient(daily, history_dates, route_id, milk_type_id, horizon_days, date_from, date_to)

    items = []
    for target in targets:
        pred, low, high = _predict_day(daily, history_dates, target)
        items.append({
            "date": target,
            "predicted_quantity": round(pred, 2),
            "low": round(low, 2),
            "high": round(high, 2),
            "actual_quantity": None,
            "is_sufficient_history": True,
        })

    total = round(sum(i["predicted_quantity"] for i in items), 2)
    low_total = round(sum(i["low"] for i in items), 2)
    high_total = round(sum(i["high"] for i in items), 2)

    return {
        "route_id": route_id,
        "milk_type_id": milk_type_id,
        "horizon_days": horizon_days,
        "date_from": date_from,
        "date_to": date_to,
        "method": "weekday_seasonal_moving_average",
        "is_sufficient_history": True,
        "message": None,
        "total_expected": total,
        "low_range": low_total,
        "high_range": high_total,
        "items": items,
    }


def _insufficient(daily, history_dates, route_id, milk_type_id, horizon_days, date_from, date_to) -> dict:
    items = []
    for target in [date_from + timedelta(days=i) for i in range(horizon_days)]:
        avg = _available_average(daily, history_dates, target)
        if avg is None:
            items.append({
                "date": target,
                "predicted_quantity": 0.0,
                "low": 0.0,
                "high": 0.0,
                "actual_quantity": None,
                "is_sufficient_history": False,
            })
        else:
            items.append({
                "date": target,
                "predicted_quantity": round(avg, 2),
                "low": round(avg, 2),
                "high": round(avg, 2),
                "actual_quantity": None,
                "is_sufficient_history": False,
            })

    total = round(sum(i["predicted_quantity"] for i in items), 2)
    return {
        "route_id": route_id,
        "milk_type_id": milk_type_id,
        "horizon_days": horizon_days,
        "date_from": date_from,
        "date_to": date_to,
        "method": "weekday_seasonal_moving_average",
        "is_sufficient_history": False,
        "message": INSUFFICIENT_MESSAGE,
        "total_expected": total,
        "low_range": total,
        "high_range": total,
        "items": items,
    }


def _available_average(daily, history_dates, target: date) -> float | None:
    weekday = _same_weekday_avg(daily, history_dates, target, WEEKDAY_OCCURRENCES)
    if weekday is not None:
        return weekday
    window = [x for x in history_dates if x < target and x >= target - timedelta(days=RESIDUAL_WINDOW)]
    if window:
        return sum(daily[x] for x in window) / len(window)
    if history_dates:
        return sum(daily[x] for x in history_dates) / len(history_dates)
    return None


def _same_weekday_avg(daily, history_dates, target: date, k: int) -> float | None:
    values = [daily[x] for x in history_dates if x < target and x.weekday() == target.weekday()]
    values = values[-k:]
    if not values:
        return None
    return sum(values) / len(values)


def _trailing_avg(daily, history_dates, target: date, n: int = RESIDUAL_WINDOW) -> float | None:
    cutoff = target - timedelta(days=n)
    window = [x for x in history_dates if cutoff <= x < target]
    if not window:
        return None
    return sum(daily[x] for x in window) / len(window)


def _linear_trend(daily, history_dates, target: date, n: int = RESIDUAL_WINDOW) -> float:
    window = [x for x in history_dates if x < target and x >= target - timedelta(days=n)]
    if len(window) < 2:
        return 0.0
    ys = [daily[x] for x in window]
    xs = list(range(len(window)))
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((xi - mean_x) * (y - mean_y) for xi, y in zip(xs, ys))
    den = sum((xi - mean_x) ** 2 for xi in xs)
    if den == 0:
        return 0.0
    slope = num / den
    return slope


def _residual_sigma(daily, history_dates) -> float:
    residuals = []
    for d in history_dates:
        if len([x for x in history_dates if x < d]) < MIN_HISTORY_DAYS:
            continue
        pred = _predict_point(daily, history_dates, d)
        residuals.append(daily[d] - pred)
    if len(residuals) < 2:
        return 0.0
    mean_r = sum(residuals) / len(residuals)
    var = sum((r - mean_r) ** 2 for r in residuals) / (len(residuals) - 1)
    return var ** 0.5


def _predict_point(daily, history_dates, target: date) -> float:
    weekday = _same_weekday_avg(daily, history_dates, target, WEEKDAY_OCCURRENCES)
    trailing = _trailing_avg(daily, history_dates, target)
    if weekday is None:
        baseline = trailing if trailing is not None else _available_average(daily, history_dates, target)
    elif trailing is None:
        baseline = weekday
    else:
        baseline = (1 - MOVING_BLEND_WEIGHT) * weekday + MOVING_BLEND_WEIGHT * trailing

    trend = _linear_trend(daily, history_dates, target)
    max_trend = baseline * TREND_CAP
    trend = max(-max_trend, min(max_trend, trend))
    return baseline + trend


def _predict_day(daily, history_dates, target: date) -> tuple[float, float, float]:
    pred = _predict_point(daily, history_dates, target)
    sigma = _residual_sigma(daily, history_dates)
    return pred, pred - Z_SCORE * sigma, pred + Z_SCORE * sigma
