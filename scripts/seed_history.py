"""Seed ~30 days of operational history so the AI module and reports have
realistic data to inspect (forecast history, anomalies, churn factors,
bills/payments for revenue + collection efficiency).

Usage:
    python -m scripts.seed_history

Idempotent: re-running only fills gaps and never duplicates rows. Requires
master data (this script calls `python -m scripts.seed` first if needed).
"""

from datetime import date, datetime, time, timedelta

from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_bill import CustomerBill
from app.models.customer_payment import CustomerPayment
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_exception import DeliveryException
from app.models.delivery_session import DeliverySession
from app.models.employee import Employee
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.subscription import Subscription
from scripts.seed import seed

HISTORY_DAYS = 30

DEFAULT_MILK_PRICES = {
    "Full Cream Milk": 60,
    "Toned Milk": 45,
    "Double Toned Milk": 40,
    "Standard Milk": 50,
    "Small Pack Milk": 20,
    "Buffalo Milk": 70,
    "Organic Milk": 80,
}

# Deliberate patterns so anomalies / churn are visible when inspecting the AI page.
SHORTFALL_ROUTES = {"R002"}           # one day with ~50% delivered (DELIVERY_SHORTFALL)
SHORTFALL_OFFSET = 10
OVERAGE_ROUTES = {"R003"}             # one day with ~150% delivered (UNPLANNED_OVERAGE)
OVERAGE_OFFSET = 10
UNBALANCED_ROUTES = {"R005"}          # today's session is UNBALANCED (RECONCILIATION_SHORTAGE)
UNBALANCED_OFFSET = 0
UNCLOSED_ROUTES = {"R004"}            # a past session still IN_PROGRESS (UNCLOSED_SESSION)
UNCLOSED_OFFSET = 2

CONSUMPTION_DROP_CUSTOMER = "C00002"  # recent week delivered 0L -> consumption drop + churn HIGH
MISSED_CUSTOMER = "C00005"            # a few NOT_DELIVERED days -> churn missed-delivery factor
MISSED_OFFSETS = {3, 4, 5}
PAYMENT_SPIKE_CUSTOMER = "C00009"     # one unusually large payment -> PAYMENT_SPIKE
OVERDUE_CUSTOMERS = {"C00002", "C00007"}  # old unpaid bill -> aging + payment-recency factors


def _route_delivery_partner(db, route_id):
    emp = (
        db.query(Employee)
        .filter(Employee.route_id == route_id, Employee.role == "DELIVERY_PARTNER")
        .first()
    )
    if not emp:
        emp = db.query(Employee).filter(Employee.route_id == route_id).first()
    if not emp:
        emp = db.query(Employee).first()
    return emp


def _existing_session(db, route_id, delivery_date, shift):
    return (
        db.query(DeliverySession)
        .filter(
            DeliverySession.route_id == route_id,
            DeliverySession.delivery_date == delivery_date,
            DeliverySession.shift == shift,
        )
        .first()
    )


def _ensure_prices(db):
    updated = 0
    for milk in db.query(MilkType).all():
        if float(milk.unit_price or 0) <= 0:
            milk.unit_price = DEFAULT_MILK_PRICES.get(milk.milk_name, 50)
            updated += 1
    if updated:
        db.commit()
        print(f"Set default unit prices on {updated} milk types")
    else:
        print("Milk type prices already set")


def _seed_sessions_and_deliveries(db):
    today = date.today()
    routes = db.query(Route).filter(Route.is_active == True).all()
    route_by_code = {r.route_code: r for r in routes}

    pairs = (
        db.query(Subscription, Customer)
        .join(Customer, Subscription.customer_id == Customer.id)
        .filter(Subscription.is_active == True, Customer.is_active == True)
        .all()
    )
    subs_by_route: dict[int, list] = {}
    for sub, cust in pairs:
        subs_by_route.setdefault(cust.route_id, []).append((sub, cust))

    created_sessions = 0
    created_deliveries = 0

    for offset in range(HISTORY_DAYS):
        day = today - timedelta(days=offset)
        for route in routes:
            route_subs = subs_by_route.get(route.id, [])
            morning_total = sum(s.morning_quantity or 0 for s, _ in route_subs)
            evening_total = sum(s.evening_quantity or 0 for s, _ in route_subs)

            for shift, total in (("MORNING", morning_total), ("EVENING", evening_total)):
                if total <= 0:
                    continue
                if _existing_session(db, route.id, day, shift):
                    continue

                emp = _route_delivery_partner(db, route.id)
                if not emp:
                    continue

                code = route.route_code
                status, rec, loaded = "CLOSED", "BALANCED", float(total)
                if code in UNCLOSED_ROUTES and (offset, shift) == (UNCLOSED_OFFSET, "MORNING"):
                    status, rec = "IN_PROGRESS", "PENDING"
                elif code in UNBALANCED_ROUTES and (offset, shift) == (UNBALANCED_OFFSET, "MORNING"):
                    rec, loaded = "UNBALANCED", float(total + 5)

                session = DeliverySession(
                    route_id=route.id,
                    delivery_date=day,
                    shift=shift,
                    delivery_partner_id=emp.id,
                    status=status,
                    total_milk_loaded=loaded,
                    total_token_registered=0,
                    total_cash_sales=0,
                    total_returned_milk=0,
                    reconciliation_status=rec,
                    is_active=True,
                )
                db.add(session)
                db.flush()
                created_sessions += 1

                for sub, cust in route_subs:
                    planned = sub.morning_quantity if shift == "MORNING" else sub.evening_quantity
                    if not planned:
                        continue
                    delivered, d_status = _delivered_for(cust.customer_code, code, offset, planned)
                    db.add(DailyDelivery(
                        session_id=session.id,
                        customer_id=cust.id,
                        milk_type_id=sub.milk_type_id,
                        planned_quantity=planned,
                        delivered_quantity=delivered,
                        delivery_status=d_status,
                        delivery_source="PLANNED",
                        shift=shift,
                        delivery_date=day,
                        is_active=True,
                    ))
                    created_deliveries += 1

    if created_sessions or created_deliveries:
        db.commit()
        print(f"Seeded {created_sessions} delivery sessions and {created_deliveries} deliveries over {HISTORY_DAYS} days")
    else:
        print("Delivery history already present, skipping")


def _delivered_for(customer_code, route_code, offset, planned):
    """Return (delivered_quantity, delivery_status) for a given day/subscription."""
    if customer_code == CONSUMPTION_DROP_CUSTOMER and 1 <= offset <= 7:
        return 0, "DELIVERED"
    if customer_code == MISSED_CUSTOMER and offset in MISSED_OFFSETS:
        return 0, "NOT_DELIVERED"
    if route_code in SHORTFALL_ROUTES and offset == SHORTFALL_OFFSET:
        return max(1, int(planned * 0.5)), "DELIVERED"
    if route_code in OVERAGE_ROUTES and offset == OVERAGE_OFFSET:
        return int(planned * 1.5) + 1, "DELIVERED"
    return planned, "DELIVERED"


def _seed_churn_exceptions(db):
    customer = db.query(Customer).filter(Customer.customer_code == CONSUMPTION_DROP_CUSTOMER).first()
    if not customer:
        return 0
    sub = (
        db.query(Subscription)
        .filter(Subscription.customer_id == customer.id, Subscription.is_active == True)
        .first()
    )
    if not sub:
        return 0

    created = 0
    today = date.today()
    for i in range(5):
        start = today - timedelta(days=20 + i)
        exists = (
            db.query(DeliveryException)
            .filter(
                DeliveryException.subscription_id == sub.id,
                DeliveryException.exception_type == "VACATION",
                DeliveryException.start_date == start,
            )
            .first()
        )
        if exists:
            continue
        db.add(DeliveryException(
            subscription_id=sub.id,
            exception_type="VACATION",
            start_date=start,
            end_date=start + timedelta(days=2),
            reason="Past vacation (churn demo)",
            status="ACTIVE",
            is_active=True,
        ))
        created += 1
    if created:
        db.commit()
        print(f"Seeded {created} churn-demo delivery exceptions for {CONSUMPTION_DROP_CUSTOMER}")
    return created


def _monthly_amount(db, milk_prices, customer_id):
    total = 0.0
    subs = (
        db.query(Subscription)
        .filter(Subscription.customer_id == customer_id, Subscription.is_active == True)
        .all()
    )
    for s in subs:
        price = milk_prices.get(s.milk_type_id, 0.0)
        total += (s.morning_quantity + s.evening_quantity) * HISTORY_DAYS * price
    return round(total, 2)


def _existing_bill(db, customer_id, period_start):
    return (
        db.query(CustomerBill)
        .filter(
            CustomerBill.customer_id == customer_id,
            CustomerBill.bill_period_start == period_start,
        )
        .first()
    )


def _existing_payment(db, customer_id, amount, when, payment_type):
    return (
        db.query(CustomerPayment)
        .filter(
            CustomerPayment.customer_id == customer_id,
            CustomerPayment.amount == amount,
            CustomerPayment.payment_type == payment_type,
            CustomerPayment.payment_date == when,
        )
        .first()
    )


def _seed_bills_and_payments(db):
    today = date.today()
    customers = db.query(Customer).filter(Customer.is_active == True).all()
    milk_prices = {m.id: float(m.unit_price or 0) for m in db.query(MilkType).all()}

    created_bills = 0
    created_payments = 0

    for cust in customers:
        code = cust.customer_code
        amount = _monthly_amount(db, milk_prices, cust.id)
        if amount <= 0:
            continue

        # Current-month bill.
        period_start = today - timedelta(days=HISTORY_DAYS - 1)
        bill = _existing_bill(db, cust.id, period_start)
        if bill is None:
            bill = CustomerBill(
                customer_id=cust.id,
                bill_date=today,
                bill_period_start=period_start,
                bill_period_end=today,
                total_amount=amount,
                paid_amount=0,
                balance_amount=amount,
                status="PENDING",
                due_date=today + timedelta(days=7),
                is_active=True,
            )
            db.add(bill)
            db.flush()
            created_bills += 1

        if code not in OVERDUE_CUSTOMERS:
            # Pay the bill in full with a BILL_PAYMENT entry.
            when = datetime.combine(today - timedelta(days=2), time(10, 30))
            if not _existing_payment(db, cust.id, amount, when, "BILL_PAYMENT"):
                db.add(CustomerPayment(
                    customer_id=cust.id,
                    payment_date=when,
                    amount=amount,
                    payment_mode="CASH",
                    payment_type="BILL_PAYMENT",
                    bill_id=bill.id,
                    is_active=True,
                ))
                created_payments += 1
            bill.paid_amount = amount
            bill.balance_amount = 0
            bill.status = "PAID"

        # Regular advance payments for healthy customers.
        if code not in OVERDUE_CUSTOMERS and code != PAYMENT_SPIKE_CUSTOMER:
            for offset, amt in ((25, 200), (15, 300), (5, 250)):
                when = datetime.combine(today - timedelta(days=offset), time(9, 0))
                if not _existing_payment(db, cust.id, amt, when, "REGULAR"):
                    db.add(CustomerPayment(
                        customer_id=cust.id,
                        payment_date=when,
                        amount=amt,
                        payment_mode="UPI",
                        payment_type="REGULAR",
                        is_active=True,
                    ))
                    created_payments += 1

        if code == PAYMENT_SPIKE_CUSTOMER:
            for offset, amt in ((25, 150), (20, 200), (15, 180), (10, 250), (5, 220)):
                when = datetime.combine(today - timedelta(days=offset), time(9, 0))
                if not _existing_payment(db, cust.id, amt, when, "REGULAR"):
                    db.add(CustomerPayment(
                        customer_id=cust.id,
                        payment_date=when,
                        amount=amt,
                        payment_mode="CASH",
                        payment_type="REGULAR",
                        is_active=True,
                    ))
                    created_payments += 1
            spike = datetime.combine(today - timedelta(days=3), time(11, 0))
            if not _existing_payment(db, cust.id, 25000, spike, "REGULAR"):
                db.add(CustomerPayment(
                    customer_id=cust.id,
                    payment_date=spike,
                    amount=25000,
                    payment_mode="BANK_TRANSFER",
                    payment_type="REGULAR",
                    is_active=True,
                ))
                created_payments += 1

        if code in OVERDUE_CUSTOMERS:
            # Old unpaid bill so aging + payment-recency churn factors show up.
            old_start = today - timedelta(days=120)
            old_end = today - timedelta(days=90)
            if _existing_bill(db, cust.id, old_start) is None:
                db.add(CustomerBill(
                    customer_id=cust.id,
                    bill_date=old_end,
                    bill_period_start=old_start,
                    bill_period_end=old_end,
                    total_amount=amount,
                    paid_amount=0,
                    balance_amount=amount,
                    status="PENDING",
                    due_date=old_end + timedelta(days=7),
                    is_active=True,
                ))
                created_bills += 1

    if created_bills or created_payments:
        db.commit()
        print(f"Seeded {created_bills} bills and {created_payments} payments")
    else:
        print("Bills/payments already present, skipping")


def seed_history():
    seed()
    db = SessionLocal()
    try:
        _ensure_prices(db)
        _seed_sessions_and_deliveries(db)
        _seed_churn_exceptions(db)
        _seed_bills_and_payments(db)
        print("\nHistory seed completed!")
        print("  - 30 days of closed delivery sessions per route/shift")
        print("  - Anomalies: reconciliation shortage (R005 today), unclosed session (R004),")
        print("               shortfall (R002), overage (R003), consumption drop (C00002), payment spike (C00009)")
        print("  - Churn demo: C00002 declining + exceptions, C00007 overdue balance")
        print("  - Bills + payments so revenue / collection efficiency reports have data")
    except Exception as e:
        db.rollback()
        print(f"Error seeding history: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_history()
