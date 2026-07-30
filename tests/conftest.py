import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.core.security import hash_password
from app.models.user import User
from app.models.route import Route
from app.models.customer import Customer
from app.models.milk_type import MilkType
from app.models.employee import Employee
from app.models.subscription import Subscription
from app.models.delivery_exception import DeliveryException
from app.models.token_identity import TokenIdentity
from app.models.token_book_issue import TokenBookIssue
from app.models.token_book_payment import TokenBookPayment
from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery
from app.models.customer_bill import CustomerBill
from app.models.customer_payment import CustomerPayment

ACTUAL_DB_URL = os.getenv(
    "TEST_DB_URL",
    "postgresql://postgres:admin@localhost:5432/milk_managemen_ai"
)

USE_ACTUAL_DB = os.getenv("USE_ACTUAL_DB", "true").lower() == "true"

if USE_ACTUAL_DB:
    SQLALCHEMY_DATABASE_URL = ACTUAL_DB_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

_test_connection = None
_test_session_override = None


def override_get_db():
    if _test_session_override:
        yield _test_session_override
    else:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_db():
    global _test_connection, _test_session_override

    if USE_ACTUAL_DB:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    yield

    if USE_ACTUAL_DB:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    global _test_connection, _test_session_override

    if USE_ACTUAL_DB:
        _test_connection = engine.connect()
        transaction = _test_connection.begin()
        session = TestingSessionLocal(bind=_test_connection)
        _test_session_override = session

        yield session

        _test_session_override = None
        session.close()
        transaction.rollback()
        _test_connection.close()
        _test_connection = None
    else:
        Base.metadata.create_all(bind=engine)
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    return TestClient(app)


@pytest.fixture
def seed_user(db_session):
    user = User(
        username="testadmin",
        password_hash=hash_password("admin123"),
        role="OWNER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_employee_user(db_session):
    user = User(
        username="testemployee",
        password_hash=hash_password("emp123"),
        role="EMPLOYEE",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, seed_user):
    response = client.post(
        "/auth/login",
        json={
            "username": "testadmin",
            "password": "admin123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_auth_headers(client, seed_employee_user):
    response = client.post(
        "/auth/login",
        json={
            "username": "testemployee",
            "password": "emp123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_route(db_session):
    route = Route(
        route_code="R001",
        route_name="Downtown Route",
        description="Main downtown delivery route",
        is_active=True
    )
    db_session.add(route)
    db_session.commit()
    db_session.refresh(route)
    return route


@pytest.fixture
def seed_customer(db_session, seed_route):
    customer = Customer(
        customer_code="C00001",
        customer_name="John Doe",
        primary_phone="9876543210",
        alternate_phone="9876543211",
        address="123 Main St",
        route_id=seed_route.id,
        remarks=None,
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def seed_milk_type(db_session):
    milk_type = MilkType(
        milk_name="Full Cream Milk",
        volume_ml=1000,
        description="Full cream dairy milk",
        is_active=True
    )
    db_session.add(milk_type)
    db_session.commit()
    db_session.refresh(milk_type)
    return milk_type


@pytest.fixture
def seed_subscription(db_session, seed_customer, seed_milk_type):
    subscription = Subscription(
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        morning_quantity=2,
        evening_quantity=1,
        status="ACTIVE",
        remarks="Test subscription",
        is_active=True
    )
    db_session.add(subscription)
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


@pytest.fixture
def seed_delivery_exception(db_session, seed_subscription):
    from datetime import datetime, timedelta
    exception = DeliveryException(
        subscription_id=seed_subscription.id,
        exception_type="VACATION",
        start_date=datetime(2026, 8, 1),
        end_date=datetime(2026, 8, 5),
        reason="Family vacation",
        status="ACTIVE",
        is_active=True
    )
    db_session.add(exception)
    db_session.commit()
    db_session.refresh(exception)
    return exception


@pytest.fixture
def seed_token_identity(db_session, seed_customer, seed_milk_type):
    identity = TokenIdentity(
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        token_number=1001,
        is_active=True
    )
    db_session.add(identity)
    db_session.commit()
    db_session.refresh(identity)
    return identity


@pytest.fixture
def seed_token_book_issue(db_session, seed_token_identity, seed_customer, seed_milk_type):
    issue = TokenBookIssue(
        token_identity_id=seed_token_identity.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        book_number="BK-001",
        total_sheets=30,
        issue_number=1,
        current_sheet=0,
        status="WAITING",
        is_active=True
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def seed_token_book_payment(db_session, seed_token_book_issue):
    payment = TokenBookPayment(
        token_book_issue_id=seed_token_book_issue.id,
        payment_mode="PREPAID",
        payment_status="PAID",
        book_price=500.00,
        amount_paid=500.00,
        balance_amount=0,
        is_active=True
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


# ---- Role-based users for reports ----

@pytest.fixture
def seed_admin_user(db_session):
    user = User(
        username="testadmin_reports",
        password_hash=hash_password("admin123"),
        role="ADMIN",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_checker_user(db_session):
    user = User(
        username="testchecker",
        password_hash=hash_password("checker123"),
        role="CHECKER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_delivery_partner_user(db_session, seed_route):
    from app.models.employee import Employee
    emp = Employee(
        employee_code="DP001",
        name="Delivery Partner One",
        phone="9999999999",
        role="DELIVERY_PARTNER",
        route_id=seed_route.id,
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    user = User(
        username="testdeliverypartner",
        password_hash=hash_password("dp123"),
        role="DELIVERY_PARTNER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    emp.user_id = user.id
    db_session.commit()
    return user


@pytest.fixture
def admin_auth_headers(client, seed_admin_user):
    response = client.post(
        "/auth/login",
        json={"username": "testadmin_reports", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def checker_auth_headers(client, seed_checker_user):
    response = client.post(
        "/auth/login",
        json={"username": "testchecker", "password": "checker123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def delivery_partner_auth_headers(client, seed_delivery_partner_user):
    response = client.post(
        "/auth/login",
        json={"username": "testdeliverypartner", "password": "dp123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---- Report seed data fixtures ----

@pytest.fixture
def seed_employee(db_session, seed_route):
    from app.models.employee import Employee
    emp = Employee(
        employee_code="EMP001",
        name="Test Employee",
        phone="8888888888",
        role="DELIVERY_PARTNER",
        route_id=seed_route.id,
        is_active=True
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def seed_second_route(db_session):
    route = Route(
        route_code="R002",
        route_name="Uptown Route",
        description="Uptown delivery route",
        is_active=True
    )
    db_session.add(route)
    db_session.commit()
    db_session.refresh(route)
    return route


@pytest.fixture
def seed_second_customer(db_session, seed_second_route):
    customer = Customer(
        customer_code="C00002",
        customer_name="Jane Smith",
        primary_phone="9876543222",
        alternate_phone="9876543223",
        address="456 Oak St",
        route_id=seed_second_route.id,
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def seed_delivery_session(db_session, seed_route, seed_customer, seed_employee):
    from datetime import date
    session = DeliverySession(
        route_id=seed_route.id,
        delivery_date=date.today(),
        shift="MORNING",
        delivery_partner_id=seed_employee.id,
        status="CLOSED",
        total_milk_loaded=10.00,
        total_token_registered=6.00,
        total_cash_sales=2.00,
        total_returned_milk=2.00,
        reconciliation_status="BALANCED",
        is_active=True
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def seed_daily_delivery(db_session, seed_delivery_session, seed_customer, seed_milk_type):
    delivery = DailyDelivery(
        session_id=seed_delivery_session.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        planned_quantity=2,
        delivered_quantity=2,
        delivery_status="DELIVERED",
        delivery_source="PLANNED",
        shift="MORNING",
        delivery_date=seed_delivery_session.delivery_date,
        is_active=True
    )
    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)
    return delivery


@pytest.fixture
def seed_customer_bill(db_session, seed_customer):
    from datetime import date, timedelta
    bill = CustomerBill(
        customer_id=seed_customer.id,
        bill_date=date.today(),
        bill_period_start=date.today().replace(day=1),
        bill_period_end=date.today(),
        total_amount=1000.00,
        paid_amount=600.00,
        balance_amount=400.00,
        due_date=date.today() + timedelta(days=7),
        status="PARTIAL",
        is_active=True
    )
    db_session.add(bill)
    db_session.commit()
    db_session.refresh(bill)
    return bill


@pytest.fixture
def seed_customer_payment(db_session, seed_customer, seed_customer_bill):
    from datetime import datetime
    payment = CustomerPayment(
        customer_id=seed_customer.id,
        bill_id=seed_customer_bill.id,
        amount=600.00,
        payment_mode="CASH",
        payment_type="BILL_PAYMENT",
        payment_date=datetime.now(),
        is_active=True
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment
