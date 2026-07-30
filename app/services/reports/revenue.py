from datetime import date

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer_payment import CustomerPayment
from app.models.token_book_payment import TokenBookPayment
from app.models.token_book_issue import TokenBookIssue
from app.models.token_identity import TokenIdentity
from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.route import Route


def get_revenue_report(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    route_id: int | None = None,
    milk_type_id: int | None = None,
    payment_mode: str | None = None,
    group_by: str = "source",
) -> dict:
    from app.services.reports.common import resolve_date_range
    frm, to = resolve_date_range(preset=None, from_date=date_from, to_date=date_to)

    token_payments = (
        db.query(
            TokenBookPayment.amount_paid,
            TokenBookPayment.payment_mode,
            TokenBookPayment.payment_date,
            TokenBookIssue.customer_id,
            TokenBookIssue.milk_type_id,
        )
        .join(TokenBookIssue, TokenBookPayment.token_book_issue_id == TokenBookIssue.id)
        .filter(TokenBookPayment.is_active == True)
        .filter(TokenBookIssue.is_active == True)
        .filter(sqlfunc.date(TokenBookPayment.payment_date) >= frm)
        .filter(sqlfunc.date(TokenBookPayment.payment_date) <= to)
    )

    customer_payments_q = (
        db.query(
            CustomerPayment.amount,
            CustomerPayment.payment_mode,
            CustomerPayment.payment_date,
            CustomerPayment.customer_id,
        )
        .filter(CustomerPayment.is_active == True)
        .filter(CustomerPayment.payment_type == "BILL_PAYMENT")
        .filter(sqlfunc.date(CustomerPayment.payment_date) >= frm)
        .filter(sqlfunc.date(CustomerPayment.payment_date) <= to)
    )

    token_rows = token_payments.all()
    customer_rows = customer_payments_q.all()

    token_revenue = sum(float(r.amount_paid or 0) for r in token_rows)
    customer_revenue = sum(float(r.amount or 0) for r in customer_rows)
    total_revenue = token_revenue + customer_revenue

    by_source = [
        {"source": "token_book_payments", "payment_mode": None, "route_name": None, "milk_type_name": None, "amount": token_revenue, "percentage": round((token_revenue / total_revenue * 100) if total_revenue else 0, 2)},
        {"source": "customer_bill_payments", "payment_mode": None, "route_name": None, "milk_type_name": None, "amount": customer_revenue, "percentage": round((customer_revenue / total_revenue * 100) if total_revenue else 0, 2)},
    ]

    result = {
        "date_from": frm,
        "date_to": to,
        "total_revenue": total_revenue,
        "token_book_revenue": token_revenue,
        "customer_bill_revenue": customer_revenue,
        "by_source": by_source,
        "by_payment_mode": [],
        "by_route": [],
        "by_milk_type": [],
    }

    return result
