from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_bill import CustomerBill
from app.models.customer_payment import CustomerPayment
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_exception import DeliveryException
from app.models.delivery_session import DeliverySession
from app.models.route import Route
from app.models.subscription import Subscription
from app.models.token_book_issue import TokenBookIssue
from app.models.token_book_payment import TokenBookPayment

WEIGHT_CONSUMPTION = 30
WEIGHT_EXCEPTIONS = 20
WEIGHT_MISSED = 20
WEIGHT_PAYMENT_RECENCY = 15
WEIGHT_BALANCE_AGING = 15

WINDOW_DAYS = 30
CONSUMPTION_RECENT_DAYS = 7
CONSUMPTION_PRIOR_DAYS = 21
MISSED_RATE_FULL = 0.5
EXCEPTION_COUNT_FULL = 5
PAYMENT_AGE_FULL_DAYS = 60
BILL_AGE_FULL_DAYS = 60

MISSED_STATUSES = ("NOT_DELIVERED", "CANCELLED")
TRACKED_DELIVERY_STATUSES = ("DELIVERED", "CASH_SALE", "NOT_DELIVERED", "CANCELLED")


def _risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def get_churn_risk(
    db: Session,
    route_id: int | None = None,
    limit: int = 20,
) -> dict:
    today = date.today()
    window_start = today - timedelta(days=WINDOW_DAYS)

    customers = _active_subscribers(db, route_id)
    if not customers:
        return {
            "generated_at": datetime.now(timezone.utc),
            "count": 0,
            "items": [],
        }

    cids = [c.id for c in customers]
    route_names = {r.id: r.route_name for r in db.query(Route.id, Route.route_name).all()}

    trends = _consumption_trends(db, cids, today)
    exception_counts = _exception_counts(db, cids, window_start, today)
    missed = _missed_delivery_rates(db, cids, window_start)
    last_payments = _last_payment_days(db, cids, today)
    bill_ages = _max_bill_overdue_days(db, cids, today)

    items = []
    for c in customers:
        recent_avg, prior_avg = trends.get(c.id, (None, None))
        if recent_avg is not None and prior_avg and recent_avg < prior_avg:
            consumption = round(WEIGHT_CONSUMPTION * (1 - recent_avg / prior_avg))
        else:
            consumption = 0
        exceptions = round(WEIGHT_EXCEPTIONS * min(exception_counts.get(c.id, 0) / EXCEPTION_COUNT_FULL, 1.0))
        missed_rate = missed.get(c.id, 0.0)
        missed_pts = round(WEIGHT_MISSED * min(missed_rate / MISSED_RATE_FULL, 1.0))
        payment_days = last_payments.get(c.id, None)
        if payment_days is None:
            payment_pts = WEIGHT_PAYMENT_RECENCY
        else:
            payment_pts = round(WEIGHT_PAYMENT_RECENCY * min(payment_days / PAYMENT_AGE_FULL_DAYS, 1.0))
        bill_days = bill_ages.get(c.id, 0)
        aging_pts = round(WEIGHT_BALANCE_AGING * min(bill_days / BILL_AGE_FULL_DAYS, 1.0))

        factors = []
        if consumption > 0:
            factors.append({"factor": "declining_consumption", "weight": WEIGHT_CONSUMPTION, "contribution": consumption})
        if exceptions > 0:
            factors.append({"factor": "delivery_exceptions", "weight": WEIGHT_EXCEPTIONS, "contribution": exceptions})
        if missed_pts > 0:
            factors.append({"factor": "missed_deliveries", "weight": WEIGHT_MISSED, "contribution": missed_pts})
        if payment_pts > 0:
            factors.append({"factor": "payment_recency", "weight": WEIGHT_PAYMENT_RECENCY, "contribution": payment_pts})
        if aging_pts > 0:
            factors.append({"factor": "outstanding_balance", "weight": WEIGHT_BALANCE_AGING, "contribution": aging_pts})

        score = min(100, consumption + exceptions + missed_pts + payment_pts + aging_pts)
        items.append({
            "customer_id": c.id,
            "customer_code": c.customer_code,
            "customer_name": c.customer_name,
            "route_name": route_names.get(c.route_id, f"Route {c.route_id}"),
            "risk_score": score,
            "risk_level": _risk_level(score),
            "factors": factors,
            "suggested_action": _suggested_action(factors),
        })

    items.sort(key=lambda i: i["risk_score"], reverse=True)
    items = items[:limit]

    return {
        "generated_at": datetime.now(timezone.utc),
        "count": len(items),
        "items": items,
    }


def _suggested_action(factors: list[dict]) -> str:
    if not factors:
        return "No action needed; the customer is currently at low risk."
    top = max(factors, key=lambda f: f["contribution"])
    action_map = {
        "declining_consumption": "Call the customer to understand the drop and offer a revised plan.",
        "delivery_exceptions": "Review the customer's delivery exceptions and address the underlying cause.",
        "missed_deliveries": "Confirm the delivery partner is completing the route and follow up on missed deliveries.",
        "payment_recency": "Reach out regarding the recent payment gap and confirm the customer's intent to continue.",
        "outstanding_balance": "Discuss the outstanding balance and set up a payment plan.",
    }
    return action_map.get(top["factor"], "Contact the customer to understand their situation.")


def _active_subscribers(db: Session, route_id: int | None) -> list[Customer]:
    query = (
        db.query(Customer)
        .join(Subscription, Subscription.customer_id == Customer.id)
        .filter(
            Customer.is_active == True,
            Subscription.is_active == True,
        )
        .distinct()
    )
    if route_id:
        query = query.filter(Customer.route_id == route_id)
    return query.all()


def _consumption_trends(
    db: Session, customer_ids: list[int], today: date
) -> dict[int, tuple[float | None, float | None]]:
    recent_cutoff = today - timedelta(days=CONSUMPTION_RECENT_DAYS)
    prior_start = today - timedelta(days=CONSUMPTION_RECENT_DAYS + CONSUMPTION_PRIOR_DAYS)

    rows = (
        db.query(
            DailyDelivery.customer_id,
            DeliverySession.delivery_date,
            sqlfunc.coalesce(sqlfunc.sum(DailyDelivery.delivered_quantity), 0),
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .filter(
            DailyDelivery.customer_id.in_(customer_ids),
            DailyDelivery.is_active == True,
            DeliverySession.is_active == True,
            DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]),
            DeliverySession.delivery_date > prior_start,
            DeliverySession.delivery_date <= today,
        )
        .group_by(DailyDelivery.customer_id, DeliverySession.delivery_date)
        .all()
    )

    per_customer: dict[int, list[tuple[date, float]]] = {}
    for r in rows:
        per_customer.setdefault(r[0], []).append((r[1], float(r[2])))

    result: dict[int, tuple[float | None, float | None]] = {}
    for cid, daily in per_customer.items():
        recent = [q for d, q in daily if d > recent_cutoff]
        prior = [q for d, q in daily if d <= recent_cutoff]
        if not recent or not prior:
            result[cid] = (None, None)
            continue
        result[cid] = (sum(recent) / len(recent), sum(prior) / len(prior))
    return result


def _exception_counts(
    db: Session, customer_ids: list[int], window_start: date, today: date
) -> dict[int, int]:
    rows = (
        db.query(
            Subscription.customer_id,
            sqlfunc.count(DeliveryException.id),
        )
        .join(DeliveryException, DeliveryException.subscription_id == Subscription.id)
        .filter(
            Subscription.customer_id.in_(customer_ids),
            Subscription.is_active == True,
            DeliveryException.status == "ACTIVE",
            DeliveryException.is_active == True,
            DeliveryException.start_date <= today + timedelta(days=1),
        )
        .group_by(Subscription.customer_id)
        .all()
    )
    result: dict[int, int] = {}
    for cid, cnt in rows:
        result[cid] = int(cnt)
    return result


def _missed_delivery_rates(db: Session, customer_ids: list[int], window_start: date) -> dict[int, float]:
    rows = (
        db.query(
            DailyDelivery.customer_id,
            DailyDelivery.delivery_status,
            sqlfunc.count(DailyDelivery.id),
        )
        .select_from(DailyDelivery)
        .join(DeliverySession, DailyDelivery.session_id == DeliverySession.id)
        .filter(
            DailyDelivery.customer_id.in_(customer_ids),
            DailyDelivery.is_active == True,
            DeliverySession.is_active == True,
            DailyDelivery.delivery_status.in_(TRACKED_DELIVERY_STATUSES),
            DeliverySession.delivery_date >= window_start,
        )
        .group_by(DailyDelivery.customer_id, DailyDelivery.delivery_status)
        .all()
    )

    totals: dict[int, int] = {}
    missed_counts: dict[int, int] = {}
    for cid, status, cnt in rows:
        totals[cid] = totals.get(cid, 0) + int(cnt)
        if status in MISSED_STATUSES:
            missed_counts[cid] = missed_counts.get(cid, 0) + int(cnt)

    result: dict[int, float] = {}
    for cid, total in totals.items():
        if total > 0:
            result[cid] = missed_counts.get(cid, 0) / total
    return result


def _last_payment_days(db: Session, customer_ids: list[int], today: date) -> dict[int, int]:
    cp_rows = (
        db.query(CustomerPayment.customer_id, sqlfunc.max(CustomerPayment.payment_date))
        .filter(
            CustomerPayment.customer_id.in_(customer_ids),
            CustomerPayment.is_active == True,
        )
        .group_by(CustomerPayment.customer_id)
        .all()
    )
    tbp_rows = (
        db.query(
            TokenBookIssue.customer_id,
            sqlfunc.max(TokenBookPayment.payment_date),
        )
        .join(TokenBookPayment, TokenBookPayment.token_book_issue_id == TokenBookIssue.id)
        .filter(
            TokenBookIssue.customer_id.in_(customer_ids),
            TokenBookPayment.is_active == True,
        )
        .group_by(TokenBookIssue.customer_id)
        .all()
    )

    latest: dict[int, date] = {}
    for cid, when in cp_rows + tbp_rows:
        if when is None:
            continue
        d = when.date() if hasattr(when, "date") else when
        if cid not in latest or d > latest[cid]:
            latest[cid] = d

    return {cid: (today - d).days for cid, d in latest.items()}


def _max_bill_overdue_days(db: Session, customer_ids: list[int], today: date) -> dict[int, int]:
    rows = (
        db.query(CustomerBill)
        .filter(
            CustomerBill.customer_id.in_(customer_ids),
            CustomerBill.is_active == True,
            CustomerBill.balance_amount > 0,
        )
        .all()
    )

    result: dict[int, int] = {}
    for bill in rows:
        anchor = bill.due_date or bill.bill_period_end
        if anchor is None:
            continue
        age = (today - anchor).days
        if age < 0:
            age = 0
        if bill.customer_id not in result or age > result[bill.customer_id]:
            result[bill.customer_id] = age
    return result
