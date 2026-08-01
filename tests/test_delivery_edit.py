from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.constants.statuses import (
    DeliverySource,
    DeliveryStatus,
    SessionStatus,
)
from app.models.customer import Customer
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession
from app.models.employee import Employee
from app.models.milk_type import MilkType
from app.models.route import Route


@pytest.fixture
def seed_closed_session(
    db_session: Session, seed_route: Route, seed_employee: Employee
) -> DeliverySession:
    sess = DeliverySession(
        route_id=seed_route.id,
        delivery_date=date(2026, 8, 15),
        shift="MORNING",
        delivery_partner_id=seed_employee.id,
        status=SessionStatus.CLOSED,
        total_milk_loaded=10.0,
        reconciliation_status="BALANCED",
    )
    db_session.add(sess)
    db_session.commit()
    db_session.refresh(sess)
    return sess


@pytest.fixture
def seed_delivery_in_closed_session(
    db_session: Session,
    seed_closed_session: DeliverySession,
    seed_customer: Customer,
    seed_milk_type: MilkType,
) -> DailyDelivery:
    d = DailyDelivery(
        session_id=seed_closed_session.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type.id,
        planned_quantity=2,
        delivered_quantity=2,
        delivery_status=DeliveryStatus.DELIVERED,
        delivery_source=DeliverySource.PLANNED,
        token_sheet_number=1,
        shift=seed_closed_session.shift,
        delivery_date=seed_closed_session.delivery_date,
    )
    db_session.add(d)
    db_session.commit()
    db_session.refresh(d)
    return d


class TestEditDeliveryOwnerRbac:

    def test_edit_delivery_owner_allowed(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
        auth_headers: dict,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Customer not home",
                "return_token_sheet": False,
                "version": seed_delivery_in_closed_session.version,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["old_status"] == "DELIVERED"
        assert data["new_status"] == "NOT_DELIVERED"

    def test_edit_delivery_admin_forbidden(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
        admin_auth_headers: dict,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Customer not home",
                "return_token_sheet": False,
                "version": seed_delivery_in_closed_session.version,
            },
            headers=admin_auth_headers,
        )
        assert response.status_code == 403

    def test_edit_delivery_checker_forbidden(
        self, client: TestClient,
        seed_delivery_in_closed_session: DailyDelivery,
        checker_auth_headers: dict,
    ):
        response = client.put(
            f"/deliveries/{seed_delivery_in_closed_session.id}/edit",
            json={
                "delivery_status": "NOT_DELIVERED",
                "reason": "Customer not home",
                "return_token_sheet": False,
                "version": seed_delivery_in_closed_session.version,
            },
            headers=checker_auth_headers,
        )
        assert response.status_code == 403

    def test_edit_delivery_unauthenticated(
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


class TestReopenSessionOwnerRbac:

    def test_reopen_session_owner_allowed(
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

    def test_reopen_session_admin_forbidden(
        self, client: TestClient,
        seed_closed_session: DeliverySession,
        admin_auth_headers: dict,
    ):
        response = client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Test reopen"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 403

    def test_reopen_session_checker_forbidden(
        self, client: TestClient,
        seed_closed_session: DeliverySession,
        checker_auth_headers: dict,
    ):
        response = client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Test reopen"},
            headers=checker_auth_headers,
        )
        assert response.status_code == 403

    def test_reopen_session_unauthenticated(
        self, client: TestClient, seed_closed_session: DeliverySession
    ):
        response = client.post(
            f"/deliveries/session/{seed_closed_session.id}/reopen",
            json={"reason": "Test reopen"},
        )
        assert response.status_code == 401
