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
