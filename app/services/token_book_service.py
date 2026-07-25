from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.token_identity import TokenIdentity
from app.models.token_book_issue import TokenBookIssue
from app.models.token_book_payment import TokenBookPayment

from app.schemas.token_identity import TokenIdentityCreate, TokenIdentityUpdate
from app.schemas.token_book import (
    TokenBookIssueCreate,
    TokenBookIssueUpdate,
    TokenBookPaymentCreate,
    TokenBookPaymentUpdate
)

from app.exceptions.customer import CustomerNotFoundError
from app.exceptions.milk_type import MilkTypeError

from app.exceptions.token_book import (
    TokenIdentityNotFoundError,
    DuplicateTokenIdentityError,
    TokenBookIssueNotFoundError,
    ActiveBookExistsError,
    DuplicateIssueNumberError,
    TokenBookPaymentNotFoundError,
    InvalidPaymentAmountError
)


# ─── Token Identity ───


def create_identity(
    db: Session,
    identity: TokenIdentityCreate
) -> TokenIdentity:

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == identity.customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise CustomerNotFoundError()

    milk_type = (
        db.query(MilkType)
        .filter(
            MilkType.id == identity.milk_type_id,
            MilkType.is_active == True
        )
        .first()
    )

    if not milk_type:
        raise MilkTypeError()

    existing = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.customer_id == identity.customer_id,
            TokenIdentity.milk_type_id == identity.milk_type_id,
            TokenIdentity.token_number == identity.token_number,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if existing:
        raise DuplicateTokenIdentityError(
            identity.customer_id,
            identity.milk_type_id,
            identity.token_number
        )

    new_identity = TokenIdentity(
        customer_id=identity.customer_id,
        milk_type_id=identity.milk_type_id,
        token_number=identity.token_number
    )

    db.add(new_identity)
    db.commit()
    db.refresh(new_identity)

    return new_identity


def get_all_identities(
    db: Session
) -> list[dict]:

    results = (
        db.query(
            TokenIdentity.id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            TokenIdentity.milk_type_id,
            MilkType.milk_name.label('milk_type_name'),
            MilkType.volume_ml.label('milk_type_volume'),
            TokenIdentity.token_number,
            TokenIdentity.is_active
        )
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(TokenIdentity.is_active == True)
        .all()
    )

    return results


def get_identity_by_id(
    db: Session,
    identity_id: int
) -> dict:

    result = (
        db.query(
            TokenIdentity.id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Customer.primary_phone,
            TokenIdentity.milk_type_id,
            MilkType.milk_name,
            MilkType.volume_ml,
            TokenIdentity.token_number,
            TokenIdentity.is_active,
            TokenIdentity.created_at,
            TokenIdentity.updated_at
        )
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(
            TokenIdentity.id == identity_id,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if not result:
        raise TokenIdentityNotFoundError()

    return {
        'id': result.id,
        'customer': {
            'id': result.customer_id,
            'customer_code': result.customer_code,
            'customer_name': result.customer_name,
            'primary_phone': result.primary_phone
        },
        'milk_type': {
            'id': result.milk_type_id,
            'milk_name': result.milk_name,
            'volume_ml': result.volume_ml
        },
        'token_number': result.token_number,
        'is_active': result.is_active,
        'created_at': result.created_at,
        'updated_at': result.updated_at
    }


def get_identities_by_customer_id(
    db: Session,
    customer_id: int
) -> list[TokenIdentity]:

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise CustomerNotFoundError()

    results = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.customer_id == customer_id,
            TokenIdentity.is_active == True
        )
        .all()
    )

    return results


def update_identity(
    db: Session,
    identity_id: int,
    identity: TokenIdentityUpdate
) -> TokenIdentity:

    identity_to_update = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.id == identity_id,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if not identity_to_update:
        raise TokenIdentityNotFoundError()

    if identity.token_number is not None:
        existing = (
            db.query(TokenIdentity)
            .filter(
                TokenIdentity.customer_id == identity_to_update.customer_id,
                TokenIdentity.milk_type_id == identity_to_update.milk_type_id,
                TokenIdentity.token_number == identity.token_number,
                TokenIdentity.is_active == True,
                TokenIdentity.id != identity_id
            )
            .first()
        )

        if existing:
            raise DuplicateTokenIdentityError(
                identity_to_update.customer_id,
                identity_to_update.milk_type_id,
                identity.token_number
            )

        identity_to_update.token_number = identity.token_number

    db.commit()
    db.refresh(identity_to_update)

    return identity_to_update


def deactivate_identity(
    db: Session,
    identity_id: int
) -> TokenIdentity:

    identity = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.id == identity_id,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if not identity:
        raise TokenIdentityNotFoundError()

    identity.is_active = False

    db.commit()
    db.refresh(identity)

    return identity


# ─── Token Book Issue ───


def create_book_issue(
    db: Session,
    issue: TokenBookIssueCreate
) -> TokenBookIssue:

    identity = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.id == issue.token_identity_id,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if not identity:
        raise TokenIdentityNotFoundError()

    active_book = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.token_identity_id == issue.token_identity_id,
            TokenBookIssue.status == "ACTIVE",
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if active_book:
        raise ActiveBookExistsError(issue.token_identity_id)

    existing_issue = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.token_identity_id == issue.token_identity_id,
            TokenBookIssue.issue_number == issue.issue_number,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if existing_issue:
        raise DuplicateIssueNumberError(
            issue.token_identity_id,
            issue.issue_number
        )

    new_issue = TokenBookIssue(
        token_identity_id=issue.token_identity_id,
        issue_number=issue.issue_number,
        remarks=issue.remarks
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


def get_all_book_issues(
    db: Session
) -> list[dict]:

    results = (
        db.query(
            TokenBookIssue.id,
            TokenBookIssue.token_identity_id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            MilkType.milk_name.label('milk_type_name'),
            TokenIdentity.token_number,
            TokenBookIssue.issue_number,
            TokenBookIssue.issue_date,
            TokenBookIssue.status,
            TokenBookIssue.current_sheet,
            TokenBookIssue.is_active
        )
        .join(TokenIdentity, TokenBookIssue.token_identity_id == TokenIdentity.id)
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(TokenBookIssue.is_active == True)
        .all()
    )

    return results


def get_book_issue_by_id(
    db: Session,
    issue_id: int
) -> dict:

    result = (
        db.query(
            TokenBookIssue.id,
            TokenBookIssue.token_identity_id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Customer.primary_phone,
            TokenIdentity.milk_type_id,
            MilkType.milk_name,
            MilkType.volume_ml,
            TokenIdentity.token_number,
            TokenBookIssue.issue_number,
            TokenBookIssue.issue_date,
            TokenBookIssue.completion_date,
            TokenBookIssue.current_sheet,
            TokenBookIssue.status,
            TokenBookIssue.remarks,
            TokenBookIssue.is_active,
            TokenBookIssue.created_at,
            TokenBookIssue.updated_at
        )
        .join(TokenIdentity, TokenBookIssue.token_identity_id == TokenIdentity.id)
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(
            TokenBookIssue.id == issue_id,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if not result:
        raise TokenBookIssueNotFoundError()

    return {
        'id': result.id,
        'token_identity': {
            'id': result.token_identity_id,
            'customer': {
                'id': result.customer_id,
                'customer_code': result.customer_code,
                'customer_name': result.customer_name,
                'primary_phone': result.primary_phone
            },
            'milk_type': {
                'id': result.milk_type_id,
                'milk_name': result.milk_name,
                'volume_ml': result.volume_ml
            },
            'token_number': result.token_number
        },
        'issue_number': result.issue_number,
        'issue_date': result.issue_date,
        'completion_date': result.completion_date,
        'current_sheet': result.current_sheet,
        'status': result.status,
        'remarks': result.remarks,
        'is_active': result.is_active,
        'created_at': result.created_at,
        'updated_at': result.updated_at
    }


def get_book_issues_by_identity_id(
    db: Session,
    identity_id: int
) -> list[TokenBookIssue]:

    identity = (
        db.query(TokenIdentity)
        .filter(
            TokenIdentity.id == identity_id,
            TokenIdentity.is_active == True
        )
        .first()
    )

    if not identity:
        raise TokenIdentityNotFoundError()

    results = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.token_identity_id == identity_id,
            TokenBookIssue.is_active == True
        )
        .all()
    )

    return results


def update_book_issue(
    db: Session,
    issue_id: int,
    issue: TokenBookIssueUpdate
) -> TokenBookIssue:

    issue_to_update = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.id == issue_id,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if not issue_to_update:
        raise TokenBookIssueNotFoundError()

    if issue.status is not None:
        issue_to_update.status = issue.status

    if issue.current_sheet is not None:
        issue_to_update.current_sheet = issue.current_sheet

    if issue.completion_date is not None:
        issue_to_update.completion_date = issue.completion_date

    if issue.remarks is not None:
        issue_to_update.remarks = issue.remarks

    db.commit()
    db.refresh(issue_to_update)

    return issue_to_update


def deactivate_book_issue(
    db: Session,
    issue_id: int
) -> TokenBookIssue:

    issue = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.id == issue_id,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if not issue:
        raise TokenBookIssueNotFoundError()

    issue.is_active = False

    db.commit()
    db.refresh(issue)

    return issue


# ─── Token Book Payment ───


def create_payment(
    db: Session,
    payment: TokenBookPaymentCreate
) -> TokenBookPayment:

    issue = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.id == payment.token_book_issue_id,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if not issue:
        raise TokenBookIssueNotFoundError()

    if payment.amount_paid > payment.book_price:
        raise InvalidPaymentAmountError()

    balance = payment.book_price - payment.amount_paid

    if balance <= 0:
        payment_status = "PAID"
    elif payment.amount_paid > 0:
        payment_status = "PARTIAL"
    else:
        payment_status = "PENDING"

    new_payment = TokenBookPayment(
        token_book_issue_id=payment.token_book_issue_id,
        payment_mode=payment.payment_mode,
        payment_status=payment_status,
        book_price=payment.book_price,
        amount_paid=payment.amount_paid,
        balance_amount=balance,
        remarks=payment.remarks
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


def get_all_payments(
    db: Session
) -> list[dict]:

    results = (
        db.query(
            TokenBookPayment.id,
            TokenBookPayment.token_book_issue_id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            TokenBookPayment.payment_mode,
            TokenBookPayment.payment_status,
            TokenBookPayment.book_price,
            TokenBookPayment.amount_paid,
            TokenBookPayment.balance_amount,
            TokenBookPayment.payment_date,
            TokenBookPayment.is_active
        )
        .join(TokenBookIssue, TokenBookPayment.token_book_issue_id == TokenBookIssue.id)
        .join(TokenIdentity, TokenBookIssue.token_identity_id == TokenIdentity.id)
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .filter(TokenBookPayment.is_active == True)
        .all()
    )

    return results


def get_payment_by_id(
    db: Session,
    payment_id: int
) -> dict:

    result = (
        db.query(
            TokenBookPayment.id,
            TokenBookPayment.token_book_issue_id,
            TokenBookIssue.token_identity_id,
            TokenIdentity.customer_id,
            Customer.customer_code,
            Customer.customer_name,
            Customer.primary_phone,
            TokenIdentity.milk_type_id,
            MilkType.milk_name,
            MilkType.volume_ml,
            TokenIdentity.token_number,
            TokenBookIssue.issue_number,
            TokenBookPayment.payment_mode,
            TokenBookPayment.payment_status,
            TokenBookPayment.book_price,
            TokenBookPayment.amount_paid,
            TokenBookPayment.balance_amount,
            TokenBookPayment.payment_date,
            TokenBookPayment.collected_by,
            TokenBookPayment.remarks,
            TokenBookPayment.is_active,
            TokenBookPayment.created_at,
            TokenBookPayment.updated_at
        )
        .join(TokenBookIssue, TokenBookPayment.token_book_issue_id == TokenBookIssue.id)
        .join(TokenIdentity, TokenBookIssue.token_identity_id == TokenIdentity.id)
        .join(Customer, TokenIdentity.customer_id == Customer.id)
        .join(MilkType, TokenIdentity.milk_type_id == MilkType.id)
        .filter(
            TokenBookPayment.id == payment_id,
            TokenBookPayment.is_active == True
        )
        .first()
    )

    if not result:
        raise TokenBookPaymentNotFoundError()

    return {
        'id': result.id,
        'token_book_issue': {
            'id': result.token_book_issue_id,
            'token_identity': {
                'id': result.token_identity_id,
                'customer': {
                    'id': result.customer_id,
                    'customer_code': result.customer_code,
                    'customer_name': result.customer_name,
                    'primary_phone': result.primary_phone
                },
                'milk_type': {
                    'id': result.milk_type_id,
                    'milk_name': result.milk_name,
                    'volume_ml': result.volume_ml
                },
                'token_number': result.token_number
            },
            'issue_number': result.issue_number,
            'status': 'ACTIVE'
        },
        'payment_mode': result.payment_mode,
        'payment_status': result.payment_status,
        'book_price': result.book_price,
        'amount_paid': result.amount_paid,
        'balance_amount': result.balance_amount,
        'payment_date': result.payment_date,
        'collected_by': result.collected_by,
        'remarks': result.remarks,
        'is_active': result.is_active,
        'created_at': result.created_at,
        'updated_at': result.updated_at
    }


def get_payments_by_issue_id(
    db: Session,
    issue_id: int
) -> list[TokenBookPayment]:

    issue = (
        db.query(TokenBookIssue)
        .filter(
            TokenBookIssue.id == issue_id,
            TokenBookIssue.is_active == True
        )
        .first()
    )

    if not issue:
        raise TokenBookIssueNotFoundError()

    results = (
        db.query(TokenBookPayment)
        .filter(
            TokenBookPayment.token_book_issue_id == issue_id,
            TokenBookPayment.is_active == True
        )
        .all()
    )

    return results


def update_payment(
    db: Session,
    payment_id: int,
    payment: TokenBookPaymentUpdate
) -> TokenBookPayment:

    payment_to_update = (
        db.query(TokenBookPayment)
        .filter(
            TokenBookPayment.id == payment_id,
            TokenBookPayment.is_active == True
        )
        .first()
    )

    if not payment_to_update:
        raise TokenBookPaymentNotFoundError()

    if payment.payment_mode is not None:
        payment_to_update.payment_mode = payment.payment_mode

    if payment.payment_status is not None:
        payment_to_update.payment_status = payment.payment_status

    if payment.book_price is not None:
        payment_to_update.book_price = payment.book_price

    if payment.amount_paid is not None:
        payment_to_update.amount_paid = payment.amount_paid

    if payment.remarks is not None:
        payment_to_update.remarks = payment.remarks

    payment_to_update.balance_amount = (
        payment_to_update.book_price - payment_to_update.amount_paid
    )

    if payment_to_update.balance_amount <= 0:
        payment_to_update.payment_status = "PAID"
    elif payment_to_update.amount_paid > 0:
        payment_to_update.payment_status = "PARTIAL"
    else:
        payment_to_update.payment_status = "PENDING"

    db.commit()
    db.refresh(payment_to_update)

    return payment_to_update


def deactivate_payment(
    db: Session,
    payment_id: int
) -> TokenBookPayment:

    payment = (
        db.query(TokenBookPayment)
        .filter(
            TokenBookPayment.id == payment_id,
            TokenBookPayment.is_active == True
        )
        .first()
    )

    if not payment:
        raise TokenBookPaymentNotFoundError()

    payment.is_active = False

    db.commit()
    db.refresh(payment)

    return payment