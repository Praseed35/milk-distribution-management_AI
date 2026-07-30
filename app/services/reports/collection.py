from datetime import date, datetime

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_bill import CustomerBill
from app.models.customer_payment import CustomerPayment
from app.models.route import Route


def get_collection_efficiency_report(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    route_id: int | None = None,
    min_outstanding: float | None = None,
    restricted_route_id: int | None = None,
) -> list[dict]:
    if restricted_route_id == -1:
        return []

    today = date.today()

    query = (
        db.query(
            Customer.id.label("customer_id"),
            Customer.customer_code,
            Customer.customer_name,
            Route.route_name,
            Customer.route_id,
        )
        .join(Route, Customer.route_id == Route.id)
        .filter(Customer.is_active == True)
        .filter(Route.is_active == True)
    )

    if route_id:
        query = query.filter(Customer.route_id == route_id)
    elif restricted_route_id is not None:
        query = query.filter(Customer.route_id == restricted_route_id)

    customers = query.all()

    result = []
    for c in customers:
        bill_query = (
            db.query(sqlfunc.sum(CustomerBill.total_amount))
            .filter(CustomerBill.customer_id == c.customer_id)
            .filter(CustomerBill.is_active == True)
        )
        if date_from:
            bill_query = bill_query.filter(CustomerBill.bill_period_start >= date_from)
        if date_to:
            bill_query = bill_query.filter(CustomerBill.bill_period_end <= date_to)

        total_billed = float(bill_query.scalar() or 0)

        payment_query = (
            db.query(sqlfunc.sum(CustomerPayment.amount))
            .filter(CustomerPayment.customer_id == c.customer_id)
            .filter(CustomerPayment.is_active == True)
            .filter(CustomerPayment.payment_type != "ADVANCE")
        )
        if date_from:
            payment_query = payment_query.filter(sqlfunc.date(CustomerPayment.payment_date) >= date_from)
        if date_to:
            payment_query = payment_query.filter(sqlfunc.date(CustomerPayment.payment_date) <= date_to)

        total_paid = float(payment_query.scalar() or 0)

        last_bill = (
            db.query(CustomerBill.bill_date)
            .filter(CustomerBill.customer_id == c.customer_id)
            .filter(CustomerBill.is_active == True)
            .order_by(CustomerBill.bill_date.desc())
            .first()
        )
        last_payment = (
            db.query(CustomerPayment.payment_date)
            .filter(CustomerPayment.customer_id == c.customer_id)
            .filter(CustomerPayment.is_active == True)
            .order_by(CustomerPayment.payment_date.desc())
            .first()
        )

        balance = total_billed - total_paid
        collection_pct = round((total_paid / total_billed * 100) if total_billed else 0, 2)

        overdue_bills = (
            db.query(CustomerBill.balance_amount, CustomerBill.due_date)
            .filter(CustomerBill.customer_id == c.customer_id)
            .filter(CustomerBill.is_active == True)
            .filter(CustomerBill.due_date.isnot(None))
            .all()
        )
        aging_current = 0.0
        aging_31_60 = 0.0
        aging_61_90 = 0.0
        aging_90_plus = 0.0
        for b in overdue_bills:
            days_overdue = (today - b.due_date).days if b.due_date else 0
            bal = float(b.balance_amount or 0)
            if days_overdue <= 0:
                aging_current += bal
            elif days_overdue <= 30:
                aging_current += bal
            elif days_overdue <= 60:
                aging_31_60 += bal
            elif days_overdue <= 90:
                aging_61_90 += bal
            else:
                aging_90_plus += bal

        item = {
            "customer_id": c.customer_id,
            "customer_code": c.customer_code,
            "customer_name": c.customer_name,
            "route_name": c.route_name,
            "total_billed": total_billed,
            "total_paid": total_paid,
            "balance": balance,
            "collection_percentage": collection_pct,
            "last_bill_date": last_bill[0] if last_bill and last_bill[0] else None,
            "last_payment_date": last_payment[0].date() if last_payment and last_payment[0] else None,
            "aging_current": aging_current,
            "aging_31_60": aging_31_60,
            "aging_61_90": aging_61_90,
            "aging_90_plus": aging_90_plus,
        }

        if min_outstanding is not None and item["balance"] < min_outstanding:
            continue

        result.append(item)

    return result
