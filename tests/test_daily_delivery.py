from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.constants.statuses import (
    BookIssueStatus,
    DeliverySource,
    DeliveryStatus,
    SessionStatus,
)
from app.models.customer import Customer
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_exception import DeliveryException
from app.models.delivery_session import DeliverySession
from app.models.employee import Employee
from app.models.milk_type import MilkType
from app.models.route import Route
from app.models.subscription import Subscription
from app.models.token_book_issue import TokenBookIssue
from app.models.token_identity import TokenIdentity


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_employee(db_session: Session, seed_route: Route) -> Employee:
    emp = Employee(
        employee_code="DEL001",
        name="Raju Delivery",
        phone="9999990001",
        address="123 Worker St",
        role="DELIVERY_PARTNER",
        route_id=seed_route.id,
        is_active=True,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def seed_session(
    db_session: Session, seed_route: Route, seed_employee: Employee
) -> DeliverySession:
    sess = DeliverySession(
        route_id=seed_route.id,
        delivery_date=date(2026, 8, 15),
        shift="MORNING",
        delivery_partner_id=seed_employee.id,
        status=SessionStatus.PLANNED,
    )
    db_session.add(sess)
    db_session.commit()
    db_session.refresh(sess)
    return sess


@pytest.fixture
def seed_started_session(
    db_session: Session, seed_session: DeliverySession
) -> DeliverySession:
    seed_session.status = SessionStatus.STARTED
    seed_session.total_milk_loaded = 50.0
    db_session.commit()
    db_session.refresh(seed_session)
    return seed_session


@pytest.fixture
def seed_completed_session(
    db_session: Session, seed_started_session: DeliverySession
) -> DeliverySession:
    seed_started_session.status = SessionStatus.COMPLETED
    db_session.commit()
    db_session.refresh(seed_started_session)
    return seed_started_session


@pytest.fixture
def seed_closed_session(
    db_session: Session, seed_completed_session: DeliverySession
) -> DeliverySession:
    seed_completed_session.status = SessionStatus.CLOSED
    seed_completed_session.reconciliation_status = "BALANCED"
    db_session.commit()
    db_session.refresh(seed_completed_session)
    return seed_completed_session


@pytest.fixture
def seed_second_milk_type(db_session: Session) -> MilkType:
    mt = MilkType(
        milk_name="Toned Milk",
        volume_ml=500,
        description="Toned dairy milk",
        is_active=True,
    )
    db_session.add(mt)
    db_session.commit()
    db_session.refresh(mt)
    return mt


@pytest.fixture
def seed_subscription_morning(
    db_session: Session,
    seed_customer: Customer,
    seed_milk_type: MilkType,
) -> Subscription:
    sub = Subscription(
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        morning_quantity=2,
        evening_quantity=0,
        status="ACTIVE",
        is_active=True,
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


@pytest.fixture
def seed_subscription_evening(
    db_session: Session,
    seed_customer: Customer,
    seed_milk_type: MilkType,
) -> Subscription:
    sub = Subscription(
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        morning_quantity=0,
        evening_quantity=3,
        status="ACTIVE",
        is_active=True,
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


@pytest.fixture
def seed_customer2(
    db_session: Session, seed_route: Route
) -> Customer:
    c = Customer(
        customer_code="C00002",
        customer_name="Jane Doe",
        primary_phone="9876543222",
        address="456 Elm St",
        route_id=seed_route.id,
        is_active=True,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture
def seed_active_token_book(
    db_session: Session,
    seed_customer: Customer,
    seed_milk_type: MilkType,
) -> TokenBookIssue:
    identity = TokenIdentity(
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        token_number=1001,
        is_active=True,
    )
    db_session.add(identity)
    db_session.commit()
    db_session.refresh(identity)

    issue = TokenBookIssue(
        token_identity_id=identity.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        book_number="BK-001",
        total_sheets=30,
        issue_number=1,
        current_sheet=1,
        status=BookIssueStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def seed_planned_delivery(
    db_session: Session, seed_session: DeliverySession,
    seed_customer: Customer, seed_milk_type: MilkType,
) -> DailyDelivery:
    d = DailyDelivery(
        session_id=seed_session.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        planned_quantity=2,
        delivered_quantity=0,
        delivery_status="PLANNED",
        delivery_source=DeliverySource.PLANNED,
        shift=seed_session.shift,
        delivery_date=seed_session.delivery_date,
    )
    db_session.add(d)
    db_session.commit()
    db_session.refresh(d)
    return d


@pytest.fixture
def seed_delivery_in_closed_session(
    db_session: Session,
    seed_closed_session: DeliverySession,
    seed_customer: Customer,
    seed_milk_type: MilkType,
    seed_active_token_book: TokenBookIssue,
) -> DailyDelivery:
    d = DailyDelivery(
        session_id=seed_closed_session.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        planned_quantity=2,
        delivered_quantity=2,
        delivery_status="DELIVERED",
        delivery_source=DeliverySource.PLANNED,
        token_sheet_number=1,
        token_book_issue_id=seed_active_token_book.id,
        shift=seed_closed_session.shift,
        delivery_date=seed_closed_session.delivery_date,
    )
    db_session.add(d)
    db_session.commit()
    db_session.refresh(d)
    return d


# =============================================================================
# Session CRUD
# =============================================================================

class TestCreateSession:

    def test_create_session_success(
        self, client: TestClient, seed_route: Route, seed_employee: Employee
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201
        data = response.json()
        assert data["route_id"] == seed_route.id
        assert data["shift"] == "MORNING"
        assert data["status"] == SessionStatus.PLANNED
        assert data["route_id"] == seed_route.id

    def test_create_session_duplicate(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_session.route_id,
            "delivery_date": seed_session.delivery_date.isoformat(),
            "shift": seed_session.shift,
            "delivery_partner_id": seed_session.delivery_partner_id,
        })
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_session_route_not_found(
        self, client: TestClient, seed_employee: Employee
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": 99999,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 404

    def test_create_session_employee_not_found(
        self, client: TestClient, seed_route: Route
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": 99999,
        })
        assert response.status_code == 404

    def test_create_session_invalid_shift(self, client: TestClient):
        response = client.post("/deliveries/sessions/", json={
            "route_id": 1,
            "delivery_date": "2026-08-15",
            "shift": "INVALID",
            "delivery_partner_id": 1,
        })
        assert response.status_code == 422

    def test_create_session_evening_shift(
        self, client: TestClient, seed_route: Route, seed_employee: Employee
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "EVENING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201
        assert response.json()["shift"] == "EVENING"


class TestCreateSessionChecklist:

    def test_create_session_generates_checklist(
        self, client: TestClient,
        seed_route: Route,
        seed_employee: Employee,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_subscription_morning: Subscription,
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201

        checklist = client.get(
            f"/deliveries/sessions/{response.json()['id']}/checklist"
        )
        data = checklist.json()
        assert data["total_expected"] == 1
        assert data["customers"][0]["customer_id"] == seed_customer.id
        assert data["customers"][0]["quantity"] == 2

    def test_create_session_evening_uses_evening_quantity(
        self, client: TestClient,
        seed_route: Route,
        seed_employee: Employee,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_subscription_evening: Subscription,
    ):
        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "EVENING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201

        checklist = client.get(
            f"/deliveries/sessions/{response.json()['id']}/checklist"
        )
        data = checklist.json()
        assert data["total_expected"] == 1
        assert data["customers"][0]["quantity"] == 3

    def test_create_session_skips_zero_quantity_subscription(
        self, client: TestClient,
        seed_route: Route,
        seed_employee: Employee,
        seed_customer: Customer,
        seed_customer2: Customer,
        seed_milk_type: MilkType,
        seed_subscription_morning: Subscription,
        db_session: Session,
    ):
        zero_sub = Subscription(
            customer_id=seed_customer2.id,
            milk_type_id=seed_milk_type.id,
            morning_quantity=0,
            evening_quantity=0,
            status="ACTIVE",
            is_active=True,
        )
        db_session.add(zero_sub)
        db_session.commit()

        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201

        checklist = client.get(
            f"/deliveries/sessions/{response.json()['id']}/checklist"
        )
        data = checklist.json()
        assert data["total_expected"] == 1
        assert data["customers"][0]["customer_id"] == seed_customer.id

    def test_create_session_excludes_exception_customer(
        self, client: TestClient,
        seed_route: Route,
        seed_employee: Employee,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_subscription_morning: Subscription,
        db_session: Session,
    ):
        from datetime import datetime

        exc = DeliveryException(
            subscription_id=seed_subscription_morning.id,
            exception_type="VACATION",
            start_date=datetime(2026, 8, 1),
            end_date=datetime(2026, 8, 20),
            reason="Family vacation",
            status="ACTIVE",
            is_active=True,
        )
        db_session.add(exc)
        db_session.commit()

        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201

        checklist = client.get(
            f"/deliveries/sessions/{response.json()['id']}/checklist"
        )
        data = checklist.json()
        assert data["total_expected"] == 0
        assert data["customers"] == []

    def test_create_session_exception_shift_mismatch_keeps_customer(
        self, client: TestClient,
        seed_route: Route,
        seed_employee: Employee,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_subscription_morning: Subscription,
        db_session: Session,
    ):
        from datetime import datetime

        exc = DeliveryException(
            subscription_id=seed_subscription_morning.id,
            exception_type="VACATION",
            start_date=datetime(2026, 8, 1),
            end_date=datetime(2026, 8, 20),
            shift="EVENING",
            reason="Evening only vacation",
            status="ACTIVE",
            is_active=True,
        )
        db_session.add(exc)
        db_session.commit()

        response = client.post("/deliveries/sessions/", json={
            "route_id": seed_route.id,
            "delivery_date": "2026-08-15",
            "shift": "MORNING",
            "delivery_partner_id": seed_employee.id,
        })
        assert response.status_code == 201

        checklist = client.get(
            f"/deliveries/sessions/{response.json()['id']}/checklist"
        )
        data = checklist.json()
        assert data["total_expected"] == 1


class TestListSessions:

    def test_list_sessions_empty(self, client: TestClient):
        response = client.get("/deliveries/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["sessions"] == []

    def test_list_sessions_with_data(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get("/deliveries/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(s["id"] == seed_session.id for s in data["sessions"])

    def test_list_sessions_filter_by_route(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/?route_id={seed_session.route_id}"
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_list_sessions_filter_by_status(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            "/deliveries/sessions/?status=PLANNED"
        )
        assert response.status_code == 200
        data = response.json()
        for s in data["sessions"]:
            assert s["status"] == "PLANNED"

    def test_list_sessions_no_match(self, client: TestClient):
        response = client.get("/deliveries/sessions/?route_id=99999")
        assert response.status_code == 200
        assert response.json()["total"] == 0

    def test_list_sessions_pagination(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get("/deliveries/sessions/?skip=0&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 1
        assert data["total"] >= 1


class TestGetSession:

    def test_get_session_success(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(f"/deliveries/sessions/{seed_session.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_session.id
        assert data["status"] == "PLANNED"
        assert "deliveries" in data

    def test_get_session_not_found(self, client: TestClient):
        response = client.get("/deliveries/sessions/99999")
        assert response.status_code == 404


# =============================================================================
# Session Lifecycle (Start / Dispatch / Close)
# =============================================================================

class TestStartSession:

    def test_start_session_success(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_session.id}/start",
            json={"total_milk_loaded": 50.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "STARTED"
        assert float(data["total_milk_loaded"]) == 50.0

    def test_start_session_already_started(
        self, client: TestClient, seed_started_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_started_session.id}/start",
            json={"total_milk_loaded": 60.0},
        )
        assert response.status_code == 400

    def test_start_session_not_found(self, client: TestClient):
        response = client.post(
            "/deliveries/sessions/99999/start",
            json={"total_milk_loaded": 50.0},
        )
        assert response.status_code == 404

    def test_start_session_zero_loaded(self, client: TestClient, db_session, seed_route, seed_employee):
        sess = DeliverySession(
            route_id=seed_route.id,
            delivery_date=date(2026, 8, 20),
            shift="MORNING",
            delivery_partner_id=seed_employee.id,
            status=SessionStatus.PLANNED,
        )
        db_session.add(sess)
        db_session.commit()
        db_session.refresh(sess)

        response = client.post(
            f"/deliveries/sessions/{sess.id}/start",
            json={"total_milk_loaded": 0},
        )
        assert response.status_code == 422


class TestRecordDispatch:

    def test_dispatch_success(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_session.id}/dispatch",
            json={"total_milk_loaded": 75.5},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "STARTED"
        assert float(data["total_milk_loaded"]) == 75.5

    def test_dispatch_twice(
        self, client: TestClient, seed_started_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_started_session.id}/dispatch",
            json={"total_milk_loaded": 80.0},
        )
        assert response.status_code == 400

    def test_dispatch_on_closed(
        self, client: TestClient, seed_closed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_closed_session.id}/dispatch",
            json={"total_milk_loaded": 10.0},
        )
        assert response.status_code == 400


class TestCompleteSession:

    def test_complete_session_success(
        self, client: TestClient, seed_started_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_started_session.id}/complete"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_complete_session_not_started(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_session.id}/complete"
        )
        assert response.status_code == 400

    def test_complete_session_not_found(self, client: TestClient):
        response = client.post("/deliveries/sessions/99999/complete")
        assert response.status_code == 404

    def test_close_after_complete_balanced(
        self, client: TestClient,
        seed_completed_session: DeliverySession,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        db_session: Session,
    ):
        delivery = DailyDelivery(
            session_id=seed_completed_session.id,
            customer_id=seed_customer.id,
            milk_type_id=seed_milk_type.id,
            planned_quantity=50,
            delivered_quantity=50,
            delivery_status="DELIVERED",
            delivery_source="PLANNED",
            shift=seed_completed_session.shift,
            delivery_date=seed_completed_session.delivery_date,
        )
        db_session.add(delivery)
        db_session.commit()

        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/close"
        )
        assert response.status_code == 200
        assert response.json()["status"] == "CLOSED"


class TestCloseSession:

    def test_close_session_unbalanced(
        self, client: TestClient, seed_completed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/close"
        )
        assert response.status_code == 400
        assert "not balanced" in response.json()["detail"].lower()

    def test_close_session_not_completed(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_session.id}/close"
        )
        assert response.status_code == 400

    def test_close_session_not_found(self, client: TestClient):
        response = client.post("/deliveries/sessions/99999/close")
        assert response.status_code == 404


# =============================================================================
# Delivery Checklist (generate_delivery_list)
# =============================================================================

class TestDeliveryChecklist:

    def test_get_checklist_empty(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/{seed_session.id}/checklist"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_expected"] == 0
        assert data["customers"] == []

    def test_get_checklist_not_found(self, client: TestClient):
        response = client.get("/deliveries/sessions/99999/checklist")
        assert response.status_code == 404


# =============================================================================
# Unplanned Delivery
# =============================================================================

class TestUnplannedDelivery:

    def test_add_unplanned_pending(
        self, client: TestClient,
        seed_started_session: DeliverySession,
        seed_customer: Customer,
        seed_milk_type: MilkType,
    ):
        response = client.post("/deliveries/unplanned", json={
            "session_id": seed_started_session.id,
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "delivered_quantity": 2,
            "delivery_status": "PENDING_TOKEN",
            "registration_method": "PENDING",
            "reason": "Customer will pay later",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["delivery_status"] == "PENDING_TOKEN"
        assert data["delivery_source"] == "UNPLANNED"
        assert data["session_id"] == seed_started_session.id

    def test_add_unplanned_cash(
        self, client: TestClient,
        seed_started_session: DeliverySession,
        seed_customer2: Customer,
        seed_milk_type: MilkType,
    ):
        response = client.post("/deliveries/unplanned", json={
            "session_id": seed_started_session.id,
            "customer_id": seed_customer2.id,
            "milk_type_id": seed_milk_type.id,
            "delivered_quantity": 1,
            "delivery_status": "CASH_SALE",
            "registration_method": "CASH",
            "reason": "Walk-in customer",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["delivery_status"] == "CASH_SALE"

    def test_add_unplanned_with_token(
        self, client: TestClient,
        seed_started_session: DeliverySession,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post("/deliveries/unplanned", json={
            "session_id": seed_started_session.id,
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "delivered_quantity": 2,
            "delivery_status": "DELIVERED",
            "registration_method": "TOKEN_SHEET",
            "token_sheet_number": 1,
            "reason": "Extra delivery",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["token_sheet_number"] == 1
        assert data["delivery_source"] == "UNPLANNED"

    def test_add_unplanned_session_not_found(self, client: TestClient):
        response = client.post("/deliveries/unplanned", json={
            "session_id": 99999,
            "customer_id": 1,
            "milk_type_id": 1,
            "delivered_quantity": 1,
            "delivery_status": "CASH_SALE",
            "registration_method": "CASH",
            "reason": "Test",
        })
        assert response.status_code == 404

    def test_add_unplanned_customer_not_found(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.post("/deliveries/unplanned", json={
            "session_id": seed_session.id,
            "customer_id": 99999,
            "milk_type_id": 1,
            "delivered_quantity": 1,
            "delivery_status": "CASH_SALE",
            "registration_method": "CASH",
            "reason": "Test",
        })
        assert response.status_code == 404


# =============================================================================
# Token Validation
# =============================================================================

class TestValidateToken:

    def test_validate_token_success(
        self, client: TestClient,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "sheet_number": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_token_nonexistent_customer(self, client: TestClient):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": 99999,
            "milk_type_id": 1,
            "sheet_number": 1,
        })
        assert response.status_code == 404

    def test_validate_token_no_active_book(
        self, client: TestClient,
        seed_customer: Customer,
        seed_milk_type: MilkType,
    ):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "sheet_number": 1,
        })
        assert response.status_code == 400

    def test_validate_token_activates_waiting_book(
        self, client: TestClient,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_token_book_issue: TokenBookIssue,
        db_session: Session,
    ):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "sheet_number": 1,
        })
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        db_session.expire_all()
        book = db_session.query(TokenBookIssue).filter(
            TokenBookIssue.id == seed_token_book_issue.id
        ).first()
        assert book.status == BookIssueStatus.ACTIVE

    def test_validate_token_sheet_out_of_range(
        self, client: TestClient,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "sheet_number": 999,
        })
        assert response.status_code == 400

    def test_validate_token_non_sequential_sheet(
        self, client: TestClient,
        seed_customer: Customer,
        seed_milk_type: MilkType,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post("/deliveries/validate-token", json={
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "sheet_number": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["requires_acknowledgment"] is True
        assert any(w["code"] == "NON_SEQUENTIAL_SHEET" for w in data["warnings"])


# =============================================================================
# Token Registration
# =============================================================================

class TestRegisterToken:

    def test_register_token_success(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post(
            f"/deliveries/{seed_planned_delivery.id}/register-token",
            json={"token_sheet_number": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sheet_registered"] is True
        assert data["delivery_id"] == seed_planned_delivery.id

    def test_register_token_activates_waiting_book(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
        seed_token_book_issue: TokenBookIssue,
        db_session: Session,
    ):
        response = client.post(
            f"/deliveries/{seed_planned_delivery.id}/register-token",
            json={"token_sheet_number": 1},
        )
        assert response.status_code == 200
        assert response.json()["sheet_registered"] is True
        db_session.expire_all()
        book = db_session.query(TokenBookIssue).filter(
            TokenBookIssue.id == seed_token_book_issue.id
        ).first()
        assert book.status == BookIssueStatus.ACTIVE
        assert book.current_sheet == 2

    def test_register_token_with_acknowledgment(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.post(
            f"/deliveries/{seed_planned_delivery.id}/register-token",
            json={
                "token_sheet_number": 10,
                "acknowledged_warnings": ["NON_SEQUENTIAL_SHEET"],
                "acknowledgment_reason": "Customer skipped ahead",
            },
        )
        assert response.status_code == 200
        assert response.json()["sheet_registered"] is True

    def test_register_token_delivery_not_found(self, client: TestClient):
        response = client.post(
            "/deliveries/99999/register-token",
            json={"token_sheet_number": 1},
        )
        assert response.status_code == 404

    def test_register_token_already_used(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
        seed_active_token_book: TokenBookIssue,
        db_session: Session,
    ):
        client.post(
            f"/deliveries/{seed_planned_delivery.id}/register-token",
            json={"token_sheet_number": 1},
        )

        other_delivery = DailyDelivery(
            session_id=seed_planned_delivery.session_id,
            customer_id=seed_planned_delivery.customer_id,
            milk_type_id=seed_planned_delivery.milk_type_id,
            planned_quantity=1,
            delivered_quantity=0,
            delivery_status="PLANNED",
            delivery_source=DeliverySource.PLANNED,
            shift=seed_planned_delivery.shift,
            delivery_date=seed_planned_delivery.delivery_date,
        )
        db_session.add(other_delivery)
        db_session.commit()
        db_session.refresh(other_delivery)

        response = client.post(
            f"/deliveries/{other_delivery.id}/register-token",
            json={"token_sheet_number": 1},
        )
        assert response.status_code == 400

    def test_register_token_updates_book_current_sheet(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
        seed_active_token_book: TokenBookIssue,
        db_session: Session,
    ):
        client.post(
            f"/deliveries/{seed_planned_delivery.id}/register-token",
            json={"token_sheet_number": 1},
        )
        db_session.expire_all()
        book = db_session.query(TokenBookIssue).filter(
            TokenBookIssue.id == seed_active_token_book.id
        ).first()
        assert book.current_sheet == 2


# =============================================================================
# Delivery Update (PUT /deliveries/{id})
# =============================================================================

class TestUpdateDelivery:

    def test_update_delivery_status(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
    ):
        response = client.put(
            f"/deliveries/{seed_planned_delivery.id}",
            json={"delivery_status": "NOT_DELIVERED"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["delivery_status"] == "NOT_DELIVERED"

    def test_update_delivery_quantity(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
    ):
        response = client.put(
            f"/deliveries/{seed_planned_delivery.id}",
            json={"delivered_quantity": 5},
        )
        assert response.status_code == 200
        assert response.json()["delivered_quantity"] == 5

    def test_update_delivery_not_found(self, client: TestClient):
        response = client.put(
            "/deliveries/99999",
            json={"delivery_status": "DELIVERED"},
        )
        assert response.status_code == 404

    def test_update_delivery_optimistic_locking(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
    ):
        response = client.put(
            f"/deliveries/{seed_planned_delivery.id}",
            json={"delivery_status": "DELIVERED", "version": 999},
        )
        assert response.status_code == 409


# =============================================================================
# Reconciliation
# =============================================================================

class TestGetReconciliation:

    def test_get_reconciliation_empty(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/{seed_session.id}/reconciliation"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_balanced"] is True

    def test_get_reconciliation_summary(
        self, client: TestClient, seed_completed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/summary"
        )
        assert response.status_code == 200

    def test_get_reconciliation_customers(
        self, client: TestClient, seed_completed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/customers"
        )
        assert response.status_code == 200

    def test_validate_reconciliation(
        self, client: TestClient, seed_completed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/validate"
        )
        assert response.status_code == 200
        data = response.json()
        assert "can_close" in data


class TestSubmitReconciliation:

    def test_submit_reconciliation(
        self, client: TestClient,
        seed_completed_session: DeliverySession,
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/submit",
            params={
                "total_cash_collected": 100.0,
                "returned_milk": 5.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "loaded_milk" in data
        assert "total_accounted" in data

    def test_submit_reconciliation_negative_returned_milk(
        self, client: TestClient,
        seed_completed_session: DeliverySession,
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/submit",
            params={
                "total_cash_collected": 100.0,
                "returned_milk": -2.0,
            },
        )
        assert response.status_code == 400

    def test_submit_reconciliation_negative_cash_collected(
        self, client: TestClient,
        seed_completed_session: DeliverySession,
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/submit",
            params={
                "total_cash_collected": -10.0,
                "returned_milk": 5.0,
            },
        )
        assert response.status_code == 400


class TestCashSales:

    def test_add_cash_sale(
        self, client: TestClient,
        seed_completed_session: DeliverySession,
        seed_milk_type: MilkType,
    ):
        response = client.post(
            f"/deliveries/sessions/{seed_completed_session.id}/reconciliation/cash-sales",
            params={
                "customer_name": "Cash Customer",
                "customer_phone": None,
                "milk_type_id": seed_milk_type.id,
                "quantity": 2.0,
                "amount": 100.0,
            },
        )
        assert response.status_code == 201

    def test_remove_cash_sale_not_found(self, client: TestClient):
        response = client.delete(
            "/deliveries/sessions/1/reconciliation/cash-sales/99999"
        )
        assert response.status_code == 404


# =============================================================================
# Session Report
# =============================================================================

class TestSessionReport:

    def test_get_report(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/sessions/{seed_session.id}/report"
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "milk_summary" in data


# =============================================================================
# Customer Token Status
# =============================================================================

class TestCustomerTokenStatus:

    def test_get_token_status(
        self, client: TestClient,
        seed_customer: Customer,
        seed_active_token_book: TokenBookIssue,
    ):
        response = client.get(
            f"/deliveries/customer/{seed_customer.id}/token-status"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == seed_customer.id
        assert len(data["token_books"]) >= 1

    def test_get_token_status_customer_not_found(self, client: TestClient):
        response = client.get("/deliveries/customer/99999/token-status")
        assert response.status_code == 404


# =============================================================================
# Session Deliveries
# =============================================================================

class TestGetSessionDeliveries:

    def test_get_session_deliveries(
        self, client: TestClient,
        seed_session: DeliverySession,
        seed_planned_delivery: DailyDelivery,
    ):
        response = client.get(
            f"/deliveries/session/{seed_session.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(d["id"] == seed_planned_delivery.id for d in data["deliveries"])

    def test_get_session_deliveries_empty(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(f"/deliveries/session/{seed_session.id}")
        assert response.status_code == 200
        assert response.json()["total"] == 0


# =============================================================================
# Session Reopen & Edit (auth required)
# =============================================================================

class TestReopenSession:

    def test_reopen_session_success(
        self, client: TestClient,
        seed_closed_session: DeliverySession,
        auth_headers: dict,
    ):
        response = client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Need to adjust delivery"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["reopen_count"] == 1

    def test_reopen_session_not_closed(
        self, client: TestClient,
        seed_session: DeliverySession,
        auth_headers: dict,
    ):
        response = client.post(
            f"/deliveries/session/{seed_session.id}/reopen",
            json={"reason": "Test reopen"},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_reopen_session_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        response = client.post(
            "/deliveries/session/99999/reopen",
            json={"reason": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_reopen_session_unauthorized(
        self, client: TestClient, seed_closed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Test"},
        )
        assert response.status_code == 401


class TestEditDelivery:

    def test_edit_delivery_status_change(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
        auth_headers: dict,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Customer not home",
                "return_token_sheet": True,
                "version": seed_delivery_in_closed_session.version,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["old_status"] == "DELIVERED"
        assert data["new_status"] == "NOT_DELIVERED"
        assert data["token_sheet_returned"] is True

    def test_edit_delivery_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        response = client.put(
            "/deliveries/99999/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Customer not home",
                "return_token_sheet": False,
            },
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_edit_delivery_concurrent_edit(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
        auth_headers: dict,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Skipped",
                "return_token_sheet": False,
                "version": 999,
            },
            headers=auth_headers,
        )
        assert response.status_code == 409

    def test_edit_delivery_unauthorized(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Test",
                "return_token_sheet": False,
            },
        )
        assert response.status_code == 401


class TestEditHistory:

    def test_get_edit_history(
        self, client: TestClient,
        seed_closed_session: DeliverySession,
        auth_headers: dict,
    ):
        client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Test reopen"},
            headers=auth_headers,
        )

        response = client.get(
            f"/deliveries/session/{seed_closed_session.id}/edit-history"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(e["edit_type"] == "SESSION_REOPEN" for e in data)

    def test_get_edit_history_empty(
        self, client: TestClient, seed_session: DeliverySession
    ):
        response = client.get(
            f"/deliveries/session/{seed_session.id}/edit-history"
        )
        assert response.status_code == 200
        assert response.json() == []


# =============================================================================
# Delivery Warnings
# =============================================================================

class TestDeliveryWarnings:

    def test_get_delivery_warnings_empty(
        self, client: TestClient,
        seed_planned_delivery: DailyDelivery,
    ):
        response = client.get(
            f"/deliveries/{seed_planned_delivery.id}/warnings"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["delivery_id"] == seed_planned_delivery.id
        assert data["warnings"] == []
