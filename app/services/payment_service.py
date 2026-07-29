from datetime import date
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_bill import CustomerBill
from app.models.customer_bill import CustomerBillItem
from app.models.customer_payment import CustomerPayment
from app.models.daily_delivery import DailyDelivery
from app.models.milk_type import MilkType
from app.models.delivery_session import DeliverySession

from app.schemas.payment import (
    BillGenerateRequest,
    BillStatusUpdate,
    CustomerPaymentCreate,
    CustomerPaymentUpdate,
)

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.milk_type import MilkTypeError
from app.exceptions.payment import (
    BillAlreadyCancelledError,
    BillAlreadyPaidError,
    CustomerBillNotFoundError,
    CustomerPaymentNotFoundError,
    InvalidBillStatusError,
    InvalidPaymentModeError,
    InvalidPaymentTypeError,
    NoDeliveriesForBillError,
)

VALID_PAYMENT_MODES = {"CASH", "UPI", "CARD", "CHEQUE", "BANK_TRANSFER"}
VALID_PAYMENT_TYPES = {"ADVANCE", "BILL_PAYMENT"}
VALID_BILL_STATUSES = {"PENDING", "PARTIAL", "PAID", "OVERDUE", "CANCELLED"}


# ─── Customer Payment Service ───


def create_payment(
    db: Session,
    payment: CustomerPaymentCreate
) -> CustomerPayment:

    customer = db.query(Customer).filter(
        Customer.id == payment.customer_id,
        Customer.is_active == True
    ).first()
    if not customer:
        raise CustomerNotFoundError()

    if payment.payment_mode not in VALID_PAYMENT_MODES:
        raise InvalidPaymentModeError(payment.payment_mode)

    if payment.payment_type not in VALID_PAYMENT_TYPES:
        raise InvalidPaymentTypeError(payment.payment_type)

    if payment.payment_type == "BILL_PAYMENT":
        if not payment.bill_id:
            raise CustomerBillNotFoundError()
        bill = db.query(CustomerBill).filter(
            CustomerBill.id == payment.bill_id,
            CustomerBill.is_active == True
        ).first()
        if not bill:
            raise CustomerBillNotFoundError()
        if bill.status == "CANCELLED":
            raise BillAlreadyCancelledError(bill.id)
        if bill.status == "PAID":
            raise BillAlreadyPaidError(bill.id)

    new_payment = CustomerPayment(
        customer_id=payment.customer_id,
        amount=payment.amount,
        payment_mode=payment.payment_mode,
        payment_type=payment.payment_type,
        reference_number=payment.reference_number,
        bill_id=payment.bill_id if payment.payment_type == "BILL_PAYMENT" else None,
        remarks=payment.remarks,
    )

    db.add(new_payment)
    db.flush()

    if payment.payment_type == "BILL_PAYMENT" and payment.bill_id:
        _update_bill_paid_amount(db, payment.bill_id)

    db.commit()
    db.refresh(new_payment)

    return new_payment


def get_all_payments(
    db: Session,
    customer_id: int | None = None,
    payment_mode: str | None = None,
    payment_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:

    query = (
        db.query(
            CustomerPayment.id,
            CustomerPayment.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            CustomerPayment.payment_date,
            CustomerPayment.amount,
            CustomerPayment.payment_mode,
            CustomerPayment.payment_type,
            CustomerPayment.reference_number,
            CustomerPayment.bill_id,
            CustomerPayment.is_active,
        )
        .join(Customer, CustomerPayment.customer_id == Customer.id)
        .filter(CustomerPayment.is_active == True)
    )

    if customer_id:
        query = query.filter(CustomerPayment.customer_id == customer_id)
    if payment_mode:
        query = query.filter(CustomerPayment.payment_mode == payment_mode)
    if payment_type:
        query = query.filter(CustomerPayment.payment_type == payment_type)
    if from_date:
        query = query.filter(CustomerPayment.payment_date >= from_date)
    if to_date:
        query = query.filter(CustomerPayment.payment_date <= to_date)

    return query.order_by(CustomerPayment.payment_date.desc()).all()


def get_payment_by_id(
    db: Session,
    payment_id: int
) -> CustomerPayment:

    payment = db.query(CustomerPayment).filter(
        CustomerPayment.id == payment_id,
        CustomerPayment.is_active == True
    ).first()

    if not payment:
        raise CustomerPaymentNotFoundError()

    return payment


def get_payments_by_customer(
    db: Session,
    customer_id: int
) -> list[CustomerPayment]:

    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_active == True
    ).first()
    if not customer:
        raise CustomerNotFoundError()

    return db.query(CustomerPayment).filter(
        CustomerPayment.customer_id == customer_id,
        CustomerPayment.is_active == True
    ).order_by(CustomerPayment.payment_date.desc()).all()


def update_payment(
    db: Session,
    payment_id: int,
    payment_update: CustomerPaymentUpdate
) -> CustomerPayment:

    existing = db.query(CustomerPayment).filter(
        CustomerPayment.id == payment_id,
        CustomerPayment.is_active == True
    ).first()

    if not existing:
        raise CustomerPaymentNotFoundError()

    if payment_update.amount is not None:
        existing.amount = payment_update.amount
    if payment_update.payment_mode is not None:
        if payment_update.payment_mode not in VALID_PAYMENT_MODES:
            raise InvalidPaymentModeError(payment_update.payment_mode)
        existing.payment_mode = payment_update.payment_mode
    if payment_update.reference_number is not None:
        existing.reference_number = payment_update.reference_number
    if payment_update.remarks is not None:
        existing.remarks = payment_update.remarks

    db.flush()

    if existing.bill_id:
        _update_bill_paid_amount(db, existing.bill_id)

    db.commit()
    db.refresh(existing)

    return existing


def deactivate_payment(
    db: Session,
    payment_id: int
) -> CustomerPayment:

    payment = db.query(CustomerPayment).filter(
        CustomerPayment.id == payment_id,
        CustomerPayment.is_active == True
    ).first()

    if not payment:
        raise CustomerPaymentNotFoundError()

    payment.is_active = False
    db.flush()

    if payment.bill_id:
        _update_bill_paid_amount(db, payment.bill_id)

    db.commit()
    db.refresh(payment)

    return payment


def _update_bill_paid_amount(
    db: Session,
    bill_id: int
) -> None:

    bill = db.query(CustomerBill).filter(
        CustomerBill.id == bill_id,
        CustomerBill.is_active == True
    ).first()

    if not bill:
        return

    total_paid = (
        db.query(sqlfunc.coalesce(sqlfunc.sum(CustomerPayment.amount), 0))
        .filter(
            CustomerPayment.bill_id == bill_id,
            CustomerPayment.is_active == True,
        )
        .scalar()
    )

    bill.paid_amount = total_paid
    bill.balance_amount = bill.total_amount - total_paid

    if bill.balance_amount <= 0:
        bill.status = "PAID"
    elif total_paid > 0:
        bill.status = "PARTIAL"
    else:
        bill.status = "PENDING"


# ─── Customer Bill Service ───


def generate_bill(
    db: Session,
    request: BillGenerateRequest
) -> CustomerBill:

    customer = db.query(Customer).filter(
        Customer.id == request.customer_id,
        Customer.is_active == True
    ).first()
    if not customer:
        raise CustomerNotFoundError()

    deliveries = (
        db.query(
            DailyDelivery.milk_type_id,
            sqlfunc.sum(DailyDelivery.delivered_quantity).label("total_quantity"),
        )
        .join(
            DeliverySession,
            DailyDelivery.session_id == DeliverySession.id,
        )
        .filter(
            DailyDelivery.customer_id == request.customer_id,
            DailyDelivery.delivery_status.in_(["DELIVERED", "CASH_SALE"]),
            DailyDelivery.is_active == True,
            DeliverySession.delivery_date >= request.bill_period_start,
            DeliverySession.delivery_date <= request.bill_period_end,
        )
        .group_by(DailyDelivery.milk_type_id)
        .all()
    )

    if not deliveries:
        raise NoDeliveriesForBillError()

    total_amount = Decimal(0)
    items = []

    for milk_type_id, total_qty in deliveries:
        milk_type = db.query(MilkType).filter(
            MilkType.id == milk_type_id,
            MilkType.is_active == True
        ).first()
        if not milk_type:
            raise MilkTypeError(f"Milk type {milk_type_id} not found.")

        unit_price = milk_type.unit_price
        amount = unit_price * total_qty
        total_amount += amount

        items.append(
            CustomerBillItem(
                milk_type_id=milk_type_id,
                quantity=total_qty,
                unit_price=unit_price,
                amount=amount,
            )
        )

    bill = CustomerBill(
        customer_id=request.customer_id,
        bill_period_start=request.bill_period_start,
        bill_period_end=request.bill_period_end,
        total_amount=total_amount,
        paid_amount=Decimal(0),
        balance_amount=total_amount,
        status="PENDING",
        due_date=request.due_date,
        remarks=request.remarks,
    )

    db.add(bill)
    db.flush()

    for item in items:
        item.bill_id = bill.id
        db.add(item)

    db.commit()
    db.refresh(bill)

    return bill


def get_all_bills(
    db: Session,
    customer_id: int | None = None,
    status: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:

    query = (
        db.query(
            CustomerBill.id,
            CustomerBill.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            CustomerBill.bill_date,
            CustomerBill.bill_period_start,
            CustomerBill.bill_period_end,
            CustomerBill.total_amount,
            CustomerBill.paid_amount,
            CustomerBill.balance_amount,
            CustomerBill.status,
            CustomerBill.due_date,
            CustomerBill.is_active,
        )
        .join(Customer, CustomerBill.customer_id == Customer.id)
        .filter(CustomerBill.is_active == True)
    )

    if customer_id:
        query = query.filter(CustomerBill.customer_id == customer_id)
    if status:
        query = query.filter(CustomerBill.status == status)
    if from_date:
        query = query.filter(CustomerBill.bill_date >= from_date)
    if to_date:
        query = query.filter(CustomerBill.bill_date <= to_date)

    return query.order_by(CustomerBill.bill_date.desc()).all()


def get_bill_by_id(
    db: Session,
    bill_id: int
) -> CustomerBill:

    bill = db.query(CustomerBill).filter(
        CustomerBill.id == bill_id,
        CustomerBill.is_active == True
    ).first()

    if not bill:
        raise CustomerBillNotFoundError()

    return bill


def get_bills_by_customer(
    db: Session,
    customer_id: int
) -> list[CustomerBill]:

    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_active == True
    ).first()
    if not customer:
        raise CustomerNotFoundError()

    return db.query(CustomerBill).filter(
        CustomerBill.customer_id == customer_id,
        CustomerBill.is_active == True
    ).order_by(CustomerBill.bill_date.desc()).all()


def update_bill_status(
    db: Session,
    bill_id: int,
    status_update: BillStatusUpdate
) -> CustomerBill:

    bill = db.query(CustomerBill).filter(
        CustomerBill.id == bill_id,
        CustomerBill.is_active == True
    ).first()

    if not bill:
        raise CustomerBillNotFoundError()

    if status_update.status not in VALID_BILL_STATUSES:
        raise InvalidBillStatusError(status_update.status)

    bill.status = status_update.status
    db.commit()
    db.refresh(bill)

    return bill


# ─── Outstanding Balance ───


def get_outstanding_balance(
    db: Session,
    customer_id: int
) -> dict:

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise CustomerNotFoundError()

    total_billed = (
        db.query(sqlfunc.coalesce(sqlfunc.sum(CustomerBill.total_amount), 0))
        .filter(
            CustomerBill.customer_id == customer_id,
            CustomerBill.is_active == True,
            CustomerBill.status.in_(["PENDING", "PARTIAL", "OVERDUE"]),
        )
        .scalar()
    )

    total_paid = (
        db.query(sqlfunc.coalesce(sqlfunc.sum(CustomerPayment.amount), 0))
        .filter(
            CustomerPayment.customer_id == customer_id,
            CustomerPayment.is_active == True,
        )
        .scalar()
    )

    last_bill = (
        db.query(CustomerBill.bill_date)
        .filter(
            CustomerBill.customer_id == customer_id,
            CustomerBill.is_active == True,
        )
        .order_by(CustomerBill.bill_date.desc())
        .first()
    )

    last_payment = (
        db.query(CustomerPayment.payment_date)
        .filter(
            CustomerPayment.customer_id == customer_id,
            CustomerPayment.is_active == True,
        )
        .order_by(CustomerPayment.payment_date.desc())
        .first()
    )

    return {
        "customer_id": customer.id,
        "customer_code": customer.customer_code,
        "customer_name": customer.customer_name,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "balance": total_billed - total_paid,
        "last_bill_date": last_bill[0] if last_bill else None,
        "last_payment_date": last_payment[0] if last_payment else None,
    }
