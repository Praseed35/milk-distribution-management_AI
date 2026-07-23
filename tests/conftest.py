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


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
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
