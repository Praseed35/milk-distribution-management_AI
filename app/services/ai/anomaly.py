from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_payment import CustomerPayment
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_exception import DeliveryException
from app.models.delivery_session import DeliverySession
from app.models.route import Route
from app.models.subscription import Subscription
from app.models.token_book_issue import TokenBookIssue
from app.models.token_book_payment import TokenBookPayment

SHORTFALL_RATIO = 0.75
OVERAGE_RATIO = 1.25
CONSUMPTION_DROP_RATIO = 0.75
CONSUMPTION_DEEP_DROP_RATIO = 0.5
PAYMENT_ZSCORE = 3.0
PAYMENT_MIN_SAMPLES = 5
PAYMENT_HISTORY_DAYS = 90
CONSUMPTION_RECENT_DAYS = 7
CONSUMPTION_PRIOR_DAYS = 21

_SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def get_anomalies(
    db: Session,
    route_id: int | None = None,
    days_back: int = 7,
) -> dict:
    today = date.today()
    date_from = today - timedelta(days=days_back - 1)

    items: list[dict] = []
    items.extend(_reconciliation_shortages(db, today, route_id))
    items.extend(_unclosed_sessions(db, today, route_id))
    items.extend(_delivery_shortfalls(db, route_id, date_from, today))
    items.extend(_consumption_drops(db, route_id, today))
    items.extend(_payment_spikes(db, route_id))
    items.extend(_unplanned_overages(db, route_id, date_from, today))

    items.sort(key=lambda i: (_SEVERITY_ORDER[i["severity"]], -i["occurred_on"].toordinal()))

    return {
        "generated_at": datetime.now(timezone.utc),
        "count": len(items),
        "items": items,
    }


def _route_names(db: Session) -> dict[int, str]:
    rows = db.query(Route.id, Route.route_name).filter(Route.is_active == True).all()
    return {r.id: r.route_name for r in rows}


def _customer_names(db: Session) -> dict[int, str]:
    rows = db.query(Customer.id, Customer.customer_name).filter(Customer.is_active == True).all()
    return {r.id: r.customer_name for r in rows}


def _session_delivered_totals(db: Session, session_ids: list[int]) -> dict[int, float]:
    if not session_ids:
        return {}
    rows = (
        db.query(
            DailyDelivery.session_id,
            sqlfunc.coalesce(sqlfunc.sum(DailyDelivery.delivered_quantity), 0),
        )
        .filter(
            DailyDelivery.session_id.in_(session_ids),
            DailyDelivery.is_active == True,
        )
        .group_by(DailyDelivery.session_id)
        .all()
    )
    return {r[0]: float(r[1]) for r in rows}


def _reconciliation_shortages(db: Session, today: date, route_id: int | None) -> list[dict]:
    query = (
        db.query(DeliverySession)
        .filter(
            DeliverySession.is_active == True,
            DeliverySession.delivery_date == today,
            DeliverySession.reconciliation_status == "UNBALANCED",
        )
    )
    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    sessions = query.all()
    if not sessions:
        return []

    names = _route_names(db)
    totals = _session_delivered_totals(db, [s.id for s in sessions])

    items = []
    for s in sessions:
        expected = float(s.total_milk_loaded or 0)
        actual = totals.get(s.id, 0.0) + float(s.total_returned_milk or 0)
        deviation = actual - expected
        if deviation >= -0.005:
            continue
        route_name = names.get(s.route_id, f"Route {s.route_id}")
        entity_name = f"{route_name} / {s.delivery_date} / {s.shift}"
        items.append({
            "type": "RECONCILIATION_SHORTAGE",
            "severity": "HIGH",
            "title": f"Reconciliation shortage on {route_name} session",
            "description": f"Loaded {expected:.2f}L but only {actual:.2f}L accounted for.",
            "entity_type": "session",
            "entity_id": s.id,
            "entity_name": entity_name,
            "metric": "loaded_vs_accounted",
            "expected": round(expected, 2),
            "actual": round(actual, 2),
            "deviation": round(deviation, 2),
            "occurred_on": s.delivery_date,
            "suggested_action": "Review token sheets and cash sale entries; reopen the session if needed.",
        })
    return items


def _unclosed_sessions(db: Session, today: date, route_id: int | None) -> list[dict]:
    query = (
        db.query(DeliverySession)
        .filter(
            DeliverySession.is_active == True,
            DeliverySession.delivery_date < today,
            DeliverySession.status != "CLOSED",
        )
    )
    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    sessions = query.all()
    if not sessions:
        return []

    names = _route_names(db)
    totals = _session_delivered_totals(db, [s.id for s in sessions])

    items = []
    for s in sessions:
        expected = float(s.total_milk_loaded or 0)
        actual = totals.get(s.id, 0.0) + float(s.total_returned_milk or 0)
        route_name = names.get(s.route_id, f"Route {s.route_id}")
        entity_name = f"{route_name} / {s.delivery_date} / {s.shift}"
        items.append({
            "type": "UNCLOSED_SESSION",
            "severity": "MEDIUM",
            "title": f"Unclosed delivery session on {route_name}",
            "description": f"Session from {s.delivery_date} is still {s.status} and not closed.",
            "entity_type": "session",
            "entity_id": s.id,
            "entity_name": entity_name,
            "metric": "session_status",
            "expected": round(expected, 2),
            "actual": round(actual, 2),
            "deviation": round(actual - expected, 2),
            "occurred_on": s.delivery_date,
            "suggested_action": "Close the session and complete reconciliation for this date.",
        })
    return items


def _daterange(date_from: date, date_to: date):
    d = date_from
    while d <= date_to:
        yield d
        d += timedelta(days=1)


def _has_exception(exceptions: list[DeliveryException], day: date, shift: str) -> bool:
    day_start = day
    day_end = day
    for e in exceptions:
        if e.start_date.date() > day_end:
            continue
        if e.end_date is not None and e.end_date.date() < day_start:
            continue
        if e.shift is not None and e.shift != shift:
            continue
        return True
    return False


def _route_expected_volume(
    db: Session,
    route_id: int | None,
    date_from: date,
    date_to: date,
) -> dict[tuple[int, date], float]:
    query = (
        db.query(Subscription, Customer)
        .join(Customer, Subscription.customer_id == Customer.id)
        .filter(
            Customer.is_active == True,
            Subscription.is_active == True,
        )
    )
    if route_id:
        query = query.filter(Customer.route_id == route_id)
    pairs = query.all()

    sub_ids = [s.id for s, _ in pairs]
    exceptions: dict[int, list[DeliveryException]] = {}
    if sub_ids:
        exc_rows = (
            db.query(DeliveryException)
            .filter(
                DeliveryException.subscription_id.in_(sub_ids),
                DeliveryException.status == "ACTIVE",
                DeliveryException.is_active == True,
            )
            .all()
        )
        for e in exc_rows:
            exceptions.setdefault(e.subscription_id, []).append(e)

    result: dict[tuple[int, date], float] = {}
    for s, c in pairs:
        exs = exceptions.get(s.id, [])
        for d in _daterange(date_from, date_to):
            morning = 0 if _has_exception(exs, d, "MORNING") else (s.morning_quantity or 0)
            evening = 0 if _has_exception(exs, d, "EVENING") else (s.evening_quantity or 0)
            qty = morning + evening
            if qty <= 0:
                continue
            key = (c.route_id, d)
            result[key] = result.get(key, 0.0) + float(qty)
    return result


def _route_actual_volume(
    db: Session,
    route_id: int | None,
    date_from: date,
    date_to: date,
) -> dict[tuple[int, date], float]:
    query = (
        db.query(
            DeliverySession.route_id,
            DeliverySession.delivery_date,
            sqlfunc.coalesce(sqlfunc.sum(DailyDelivery.delivered_quantity), 0),
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .filter(
            DailyDelivery.is_active == True,
            DeliverySession.is_active == True,
            DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]),
            DeliverySession.delivery_date >= date_from,
            DeliverySession.delivery_date <= date_to,
        )
        .group_by(DeliverySession.route_id, DeliverySession.delivery_date)
    )
    if route_id:
        query = query.filter(DeliverySession.route_id == route_id)
    rows = query.all()
    return {(r[0], r[1]): float(r[2]) for r in rows}


def _volume_diffs(
    db: Session,
    route_id: int | None,
    date_from: date,
    date_to: date,
) -> list[tuple[int, date, float, float]]:
    expected = _route_expected_volume(db, route_id, date_from, date_to)
    actual = _route_actual_volume(db, route_id, date_from, date_to)
    keys = sorted(set(expected.keys()) | set(actual.keys()))
    return [(rid, d, expected.get((rid, d), 0.0), actual.get((rid, d), 0.0)) for rid, d in keys]


def _delivery_shortfalls(
    db: Session, route_id: int | None, date_from: date, date_to: date
) -> list[dict]:
    names = _route_names(db)
    items = []
    for rid, d, exp, act in _volume_diffs(db, route_id, date_from, date_to):
        if exp <= 0:
            continue
        if act >= SHORTFALL_RATIO * exp:
            continue
        route_name = names.get(rid, f"Route {rid}")
        items.append({
            "type": "DELIVERY_SHORTFALL",
            "severity": "MEDIUM",
            "title": f"Deliveries below expectations on {route_name}",
            "description": (
                f"Expected {exp:.2f}L from subscriptions but only {act:.2f}L delivered "
                f"({round(act / exp * 100, 1)}% of expected)."
            ),
            "entity_type": "route",
            "entity_id": rid,
            "entity_name": route_name,
            "metric": "delivered_vs_expected",
            "expected": round(exp, 2),
            "actual": round(act, 2),
            "deviation": round(act - exp, 2),
            "occurred_on": d,
            "suggested_action": "Check for unrecorded deliveries or cash sales; confirm route coverage.",
        })
    return items


def _unplanned_overages(
    db: Session, route_id: int | None, date_from: date, date_to: date
) -> list[dict]:
    names = _route_names(db)
    items = []
    for rid, d, exp, act in _volume_diffs(db, route_id, date_from, date_to):
        if exp <= 0:
            continue
        if act <= OVERAGE_RATIO * exp:
            continue
        route_name = names.get(rid, f"Route {rid}")
        items.append({
            "type": "UNPLANNED_OVERAGE",
            "severity": "LOW",
            "title": f"Deliveries above expectations on {route_name}",
            "description": (
                f"Expected {exp:.2f}L from subscriptions but {act:.2f}L delivered "
                f"({round(act / exp * 100, 1)}% of expected)."
            ),
            "entity_type": "route",
            "entity_id": rid,
            "entity_name": route_name,
            "metric": "delivered_vs_expected",
            "expected": round(exp, 2),
            "actual": round(act, 2),
            "deviation": round(act - exp, 2),
            "occurred_on": d,
            "suggested_action": "Verify unplanned cash sales were recorded correctly.",
        })
    return items


def _consumption_drops(db: Session, route_id: int | None, today: date) -> list[dict]:
    names = _customer_names(db)
    recent_cutoff = today - timedelta(days=CONSUMPTION_RECENT_DAYS)
    prior_start = today - timedelta(days=CONSUMPTION_RECENT_DAYS + CONSUMPTION_PRIOR_DAYS)

    query = (
        db.query(
            DailyDelivery.customer_id,
            DeliverySession.delivery_date,
            sqlfunc.coalesce(sqlfunc.sum(DailyDelivery.delivered_quantity), 0),
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .join(Customer, DailyDelivery.customer_id == Customer.id)
        .filter(
            DailyDelivery.is_active == True,
            DeliverySession.is_active == True,
            Customer.is_active == True,
            DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]),
            DeliverySession.delivery_date > prior_start,
            DeliverySession.delivery_date <= today,
        )
        .group_by(DailyDelivery.customer_id, DeliverySession.delivery_date)
    )
    if route_id:
        query = query.filter(Customer.route_id == route_id)
    rows = query.all()

    per_customer: dict[int, list[tuple[date, float]]] = {}
    for r in rows:
        per_customer.setdefault(r[0], []).append((r[1], float(r[2])))

    items = []
    for cid, daily in per_customer.items():
        recent = [q for d, q in daily if d > recent_cutoff]
        prior = [q for d, q in daily if d <= recent_cutoff]
        if not recent or not prior:
            continue
        recent_avg = sum(recent) / len(recent)
        prior_avg = sum(prior) / len(prior)
        if prior_avg <= 0:
            continue
        if recent_avg >= CONSUMPTION_DROP_RATIO * prior_avg:
            continue
        drop_ratio = recent_avg / prior_avg
        severity = "MEDIUM" if drop_ratio < CONSUMPTION_DEEP_DROP_RATIO else "LOW"
        name = names.get(cid, f"Customer {cid}")
        items.append({
            "type": "CONSUMPTION_DROP",
            "severity": severity,
            "title": f"Consumption drop for {name}",
            "description": (
                f"Recent 7-day average {recent_avg:.2f}L is {round(drop_ratio * 100, 1)}% of the "
                f"prior 21-day average ({prior_avg:.2f}L)."
            ),
            "entity_type": "customer",
            "entity_id": cid,
            "entity_name": name,
            "metric": "consumption_trend",
            "expected": round(prior_avg, 2),
            "actual": round(recent_avg, 2),
            "deviation": round(recent_avg - prior_avg, 2),
            "occurred_on": today,
            "suggested_action": "Contact the customer to understand the reduction in consumption.",
        })
    return items


def _payment_spikes(db: Session, route_id: int | None) -> list[dict]:
    names = _customer_names(db)
    cutoff = date.today() - timedelta(days=PAYMENT_HISTORY_DAYS)

    cp_query = (
        db.query(
            CustomerPayment.id,
            CustomerPayment.customer_id,
            CustomerPayment.amount,
            CustomerPayment.payment_date,
            Customer.route_id,
        )
        .join(Customer, CustomerPayment.customer_id == Customer.id)
        .filter(
            CustomerPayment.is_active == True,
            Customer.is_active == True,
            CustomerPayment.payment_date >= cutoff,
        )
    )
    if route_id:
        cp_query = cp_query.filter(Customer.route_id == route_id)

    tbp_query = (
        db.query(
            TokenBookPayment.id,
            TokenBookIssue.customer_id,
            TokenBookPayment.amount_paid,
            TokenBookPayment.payment_date,
            Customer.route_id,
        )
        .join(TokenBookIssue, TokenBookPayment.token_book_issue_id == TokenBookIssue.id)
        .join(Customer, TokenBookIssue.customer_id == Customer.id)
        .filter(
            TokenBookPayment.is_active == True,
            Customer.is_active == True,
            TokenBookPayment.payment_date >= cutoff,
        )
    )
    if route_id:
        tbp_query = tbp_query.filter(Customer.route_id == route_id)

    candidates: list[tuple[int, int, float, datetime]] = []  # (payment_id, customer_id, amount, when)
    for r in cp_query.all():
        candidates.append((r[0], r[1], float(r[2] or 0), r[3]))
    for r in tbp_query.all():
        candidates.append((r[0], r[1], float(r[2] or 0), r[3]))

    per_customer: dict[int, list[tuple[int, float, datetime]]] = {}
    for pid, cid, amt, when in candidates:
        per_customer.setdefault(cid, []).append((pid, amt, when))

    items = []
    for cid, entries in per_customer.items():
        if len(entries) < PAYMENT_MIN_SAMPLES:
            continue
        amounts = [e[1] for e in entries]
        mean = sum(amounts) / len(amounts)
        var = sum((a - mean) ** 2 for a in amounts) / len(amounts)
        std = var ** 0.5
        name = names.get(cid, f"Customer {cid}")
        for pid, amt, when in entries:
            if std > 0:
                z = (amt - mean) / std
                if z <= PAYMENT_ZSCORE:
                    continue
            else:
                if amt <= mean + PAYMENT_ZSCORE * max(mean, 1.0):
                    continue
            items.append({
                "type": "PAYMENT_SPIKE",
                "severity": "LOW",
                "title": f"Unusually large payment by {name}",
                "description": (
                    f"Payment of {amt:.2f} is well above this customer's usual "
                    f"average of {mean:.2f}."
                ),
                "entity_type": "payment",
                "entity_id": pid,
                "entity_name": name,
                "metric": "payment_amount_zscore",
                "expected": round(mean, 2),
                "actual": round(amt, 2),
                "deviation": round(amt - mean, 2),
                "occurred_on": when.date() if hasattr(when, "date") else when,
                "suggested_action": "Verify the unusually large payment was intentional and recorded correctly.",
            })
    return items
