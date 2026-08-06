from datetime import date, timedelta

import pytest

from app.models.delivery_session import DeliverySession
from app.models.daily_delivery import DailyDelivery
from app.models.employee import Employee
from app.models.subscription import Subscription
from app.models.customer import Customer
from app.models.customer_payment import CustomerPayment
from app.models.customer_bill import CustomerBill
from app.models.delivery_exception import DeliveryException


def _ensure_employee(db_session, route):
    employee = (
        db_session.query(Employee)
        .filter(Employee.route_id == route.id)
        .first()
    )
    if not employee:
        employee = Employee(
            employee_code=f"EMP-AI-{route.id}",
            name="AI Emp",
            phone=f"7777777{route.id:03d}",
            role="DELIVERY_PARTNER",
            route_id=route.id,
            is_active=True,
        )
        db_session.add(employee)
        db_session.flush()
    return employee


def seed_forecast_history(db_session, route, customer, milk_type, days=28, value=10, shift="MORNING",
                          delivery_status="DELIVERED"):
    employee = _ensure_employee(db_session, route)
    today = date.today()
    for offset in range(1, days + 1):
        d = today - timedelta(days=offset)
        session = DeliverySession(
            route_id=route.id,
            delivery_date=d,
            shift=shift,
            delivery_partner_id=employee.id,
            status="CLOSED",
            total_milk_loaded=value,
            total_returned_milk=0,
            reconciliation_status="BALANCED",
            is_active=True,
        )
        db_session.add(session)
        db_session.flush()
        delivery = DailyDelivery(
            session_id=session.id,
            customer_id=customer.id,
            milk_type_id=milk_type.id,
            planned_quantity=int(value),
            delivered_quantity=int(value),
            delivery_status=delivery_status,
            delivery_source="PLANNED",
            shift=shift,
            delivery_date=d,
            is_active=True,
        )
        db_session.add(delivery)
    db_session.commit()


class TestForecast:
    def test_forecast_success(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_history"] is True
        assert data["method"] == "weekday_seasonal_moving_average"
        assert len(data["items"]) == 7
        assert data["total_expected"] == 70.0
        assert data["low_range"] == 70.0
        assert data["high_range"] == 70.0
        assert data["items"][0]["predicted_quantity"] == 10.0

    def test_forecast_horizon_custom(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=5)
        response = client.get("/api/v1/ai/forecast?horizon_days=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total_expected"] == 15.0

    def test_forecast_insufficient_history(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=5, value=10)
        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_history"] is False
        assert "Insufficient history" in (data["message"] or "")
        assert len(data["items"]) == 7
        assert data["total_expected"] is not None

    def test_forecast_route_filter(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_route, seed_second_customer,
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        seed_forecast_history(db_session, seed_second_route, seed_second_customer, seed_milk_type, days=28, value=20)
        response_a = client.get(f"/api/v1/ai/forecast?route_id={seed_route.id}", headers=auth_headers)
        assert response_a.status_code == 200
        assert response_a.json()["total_expected"] == 70.0
        response_b = client.get(f"/api/v1/ai/forecast?route_id={seed_second_route.id}", headers=auth_headers)
        assert response_b.json()["total_expected"] == 140.0

    def test_forecast_milk_type_filter(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type,
    ):
        from app.models.milk_type import MilkType
        mt2 = MilkType(milk_name="Toned Milk", volume_ml=500, description="Second", is_active=True)
        db_session.add(mt2)
        db_session.commit()
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        seed_forecast_history(db_session, seed_route, seed_customer, mt2, days=28, value=30, shift="EVENING")
        response = client.get(f"/api/v1/ai/forecast?milk_type_id={seed_milk_type.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total_expected"] == 70.0

    def test_forecast_milk_type_not_found(self, client, auth_headers):
        response = client.get("/api/v1/ai/forecast?milk_type_id=99999", headers=auth_headers)
        assert response.status_code == 404

    def test_forecast_unauthorized(self, client):
        response = client.get("/api/v1/ai/forecast")
        assert response.status_code == 401

    def test_forecast_forbidden_checker(self, client, checker_auth_headers):
        response = client.get("/api/v1/ai/forecast", headers=checker_auth_headers)
        assert response.status_code == 403

    def test_forecast_forbidden_delivery_partner(self, client, delivery_partner_auth_headers):
        response = client.get("/api/v1/ai/forecast", headers=delivery_partner_auth_headers)
        assert response.status_code == 403

    def test_forecast_horizon_boundary_min(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        response = client.get("/api/v1/ai/forecast?horizon_days=1", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1
        assert response.json()["total_expected"] == 10.0

    def test_forecast_horizon_boundary_max(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        response = client.get("/api/v1/ai/forecast?horizon_days=30", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 30
        assert response.json()["total_expected"] == 300.0

    def test_forecast_no_history(self, client, auth_headers):
        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_history"] is False
        assert "Insufficient history" in (data["message"] or "")
        assert data["total_expected"] == 0.0
        assert len(data["items"]) == 7
        assert all(i["predicted_quantity"] == 0.0 for i in data["items"])

    def test_forecast_nonexistent_route(self, client, auth_headers):
        response = client.get("/api/v1/ai/forecast?route_id=99999", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_history"] is False
        assert data["total_expected"] == 0.0

    def test_forecast_excludes_non_delivered_status(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        emp = _ensure_employee(db_session, seed_route)
        for offset, status in ((1, "NOT_DELIVERED"), (2, "CANCELLED")):
            session = _make_session(
                db_session, seed_route, emp, date.today() - timedelta(days=offset), shift="EVENING"
            )
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=1000, status=status)
        db_session.commit()

        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total_expected"] == 70.0

    def test_forecast_excludes_inactive_delivery(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        emp = _ensure_employee(db_session, seed_route)
        session = _make_session(db_session, seed_route, emp, date.today() - timedelta(days=1), shift="EVENING")
        db_session.add(DailyDelivery(
            session_id=session.id,
            customer_id=seed_customer.id,
            milk_type_id=seed_milk_type.id,
            planned_quantity=1000,
            delivered_quantity=1000,
            delivery_status="DELIVERED",
            delivery_source="PLANNED",
            shift="MORNING",
            delivery_date=session.delivery_date,
            is_active=False,
        ))
        db_session.commit()

        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total_expected"] == 70.0

    def test_forecast_includes_cash_sale(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=14, value=5,
                              delivery_status="CASH_SALE")
        response = client.get("/api/v1/ai/forecast", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_sufficient_history"] is True
        assert data["total_expected"] == 35.0
        assert all(i["predicted_quantity"] == 5.0 for i in data["items"])

    def test_forecast_cache_and_refresh(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type, monkeypatch
    ):
        clock = {"now": 1000.0}
        monkeypatch.setattr("app.services.reports.cache.time.time", lambda: clock["now"])

        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=28, value=10)
        first = client.get("/api/v1/ai/forecast", headers=auth_headers).json()
        assert first["total_expected"] == 70.0

        seed_forecast_history(db_session, seed_route, seed_customer, seed_milk_type, days=14, value=20,
                              shift="EVENING")
        cached = client.get("/api/v1/ai/forecast", headers=auth_headers).json()
        assert cached["total_expected"] == 70.0

        refreshed = client.get("/api/v1/ai/forecast?refresh=true", headers=auth_headers).json()
        assert refreshed["total_expected"] > 70.0

        clock["now"] += 301
        expired = client.get("/api/v1/ai/forecast", headers=auth_headers).json()
        assert expired["total_expected"] > 70.0

    def test_forecast_invalid_horizon_zero(self, client, auth_headers):
        response = client.get("/api/v1/ai/forecast?horizon_days=0", headers=auth_headers)
        assert response.status_code == 422

    def test_forecast_invalid_horizon_high(self, client, auth_headers):
        response = client.get("/api/v1/ai/forecast?horizon_days=31", headers=auth_headers)
        assert response.status_code == 422


def _make_session(db_session, route, employee, delivery_date, shift="MORNING", status="CLOSED",
                  loaded=0.0, returned=0.0, rec_status="BALANCED"):
    session = DeliverySession(
        route_id=route.id,
        delivery_date=delivery_date,
        shift=shift,
        delivery_partner_id=employee.id,
        status=status,
        total_milk_loaded=loaded,
        total_returned_milk=returned,
        reconciliation_status=rec_status,
        is_active=True,
    )
    db_session.add(session)
    db_session.flush()
    return session


def _make_delivery(db_session, session, customer, milk_type, delivered, status="DELIVERED",
                   planned=None, source="PLANNED"):
    delivery = DailyDelivery(
        session_id=session.id,
        customer_id=customer.id,
        milk_type_id=milk_type.id,
        planned_quantity=planned if planned is not None else delivered,
        delivered_quantity=delivered,
        delivery_status=status,
        delivery_source=source,
        shift=session.shift,
        delivery_date=session.delivery_date,
        is_active=True,
    )
    db_session.add(delivery)
    db_session.flush()
    return delivery


def _make_subscription(db_session, customer, milk_type, morning=0, evening=0):
    sub = Subscription(
        customer_id=customer.id,
        milk_type_id=milk_type.id,
        morning_quantity=morning,
        evening_quantity=evening,
        status="ACTIVE",
        is_active=True,
    )
    db_session.add(sub)
    db_session.flush()
    return sub


class TestAnomalies:
    def test_reconciliation_shortage(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        session = _make_session(
            db_session, seed_route, emp, today, loaded=10.0, returned=0.0, rec_status="UNBALANCED"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=8)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "RECONCILIATION_SHORTAGE"]
        assert items
        item = items[0]
        assert item["severity"] == "HIGH"
        assert item["entity_type"] == "session"
        assert item["expected"] == 10.0
        assert item["actual"] == 8.0
        assert item["deviation"] == -2.0

    def test_unclosed_session(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        yesterday = date.today() - timedelta(days=1)
        session = _make_session(
            db_session, seed_route, emp, yesterday, status="IN_PROGRESS"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=0)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "UNCLOSED_SESSION"]
        assert items
        assert items[0]["severity"] == "MEDIUM"
        assert items[0]["entity_type"] == "session"
        assert items[0]["occurred_on"] == str(yesterday)

    def test_delivery_shortfall(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        for offset in (1, 2, 3):
            d = date.today() - timedelta(days=offset)
            session = _make_session(db_session, seed_route, emp, d)
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=2)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "DELIVERY_SHORTFALL"]
        assert items
        assert items[0]["severity"] == "MEDIUM"
        assert items[0]["entity_type"] == "route"
        assert items[0]["expected"] == 10.0
        assert any(i["actual"] == 2.0 for i in items)

    def test_consumption_drop(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 22):
            d = today - timedelta(days=offset)
            qty = 2 if offset <= 6 else 10
            session = _make_session(db_session, seed_route, emp, d)
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=qty)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "CONSUMPTION_DROP"]
        assert items
        item = items[0]
        assert item["severity"] == "MEDIUM"
        assert item["entity_type"] == "customer"
        assert item["expected"] == 10.0
        assert item["actual"] == 2.0

    def test_payment_spike(
        self, client, auth_headers, db_session, seed_route, seed_customer
    ):
        for i in range(20):
            amount = 8 + (i % 5)
            payment = CustomerPayment(
                customer_id=seed_customer.id,
                amount=amount,
                payment_mode="CASH",
                payment_type="REGULAR",
                is_active=True,
            )
            db_session.add(payment)
        spike = CustomerPayment(
            customer_id=seed_customer.id,
            amount=10000,
            payment_mode="CASH",
            payment_type="REGULAR",
            is_active=True,
        )
        db_session.add(spike)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "PAYMENT_SPIKE"]
        assert items
        item = items[0]
        assert item["severity"] == "LOW"
        assert item["entity_type"] == "payment"
        assert item["actual"] == 10000.0

    def test_unplanned_overage(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        for offset in (1, 2):
            d = date.today() - timedelta(days=offset)
            session = _make_session(db_session, seed_route, emp, d)
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=20)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "UNPLANNED_OVERAGE"]
        assert items
        assert items[0]["severity"] == "LOW"
        assert items[0]["entity_type"] == "route"
        assert items[0]["expected"] == 10.0
        assert items[0]["actual"] == 20.0

    def test_balanced_session_not_flagged(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        session = _make_session(
            db_session, seed_route, emp, date.today(), loaded=10.0, returned=0.0, rec_status="BALANCED"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "RECONCILIATION_SHORTAGE"]
        assert items == []

    def test_unclosed_session_today_not_flagged(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        session = _make_session(
            db_session, seed_route, emp, date.today(), status="IN_PROGRESS"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=0)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "UNCLOSED_SESSION"]
        assert items == []

    def test_anomalies_days_back_boundary_and_filtering(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in (0, 1):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=2)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies?days_back=1", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "DELIVERY_SHORTFALL"]
        assert items
        assert all(i["occurred_on"] == str(today) for i in items)

    def test_anomalies_days_back_max_boundary(self, client, auth_headers):
        response = client.get("/api/v1/ai/anomalies?days_back=30", headers=auth_headers)
        assert response.status_code == 200
        assert "count" in response.json()

    def test_anomalies_inactive_delivery_excluded_from_reconciliation(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        session = _make_session(
            db_session, seed_route, emp, date.today(), loaded=10.0, returned=0.0, rec_status="UNBALANCED"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=8)
        inactive = _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=5)
        inactive.is_active = False
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        items = [i for i in response.json()["items"] if i["type"] == "RECONCILIATION_SHORTAGE"]
        assert items
        assert items[0]["actual"] == 8.0
        assert items[0]["deviation"] == -2.0

    def test_anomalies_severity_ordering(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        session = _make_session(
            db_session, seed_route, emp, today, loaded=10.0, returned=0.0, rec_status="UNBALANCED"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=8)
        _make_session(
            db_session, seed_route, emp, today - timedelta(days=2), status="IN_PROGRESS"
        )
        for _ in range(20):
            _make_payment(db_session, seed_customer, 8)
        _make_payment(db_session, seed_customer, 10000)
        db_session.commit()

        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        severities = [order[i["severity"]] for i in response.json()["items"]]
        assert severities == sorted(severities)
        assert severities == [0, 1, 2]

    def test_anomalies_nonexistent_route(self, client, auth_headers):
        response = client.get("/api/v1/ai/anomalies?route_id=99999", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_anomalies_empty(self, client, auth_headers, seed_route):
        response = client.get("/api/v1/ai/anomalies", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["items"] == []

    def test_anomalies_route_filter(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_route,
    ):
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        session = _make_session(
            db_session, seed_route, emp, today, loaded=10.0, returned=0.0, rec_status="UNBALANCED"
        )
        _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=8)
        db_session.commit()

        response = client.get(f"/api/v1/ai/anomalies?route_id={seed_route.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["count"] > 0

        response_other = client.get(
            f"/api/v1/ai/anomalies?route_id={seed_second_route.id}", headers=auth_headers
        )
        assert response_other.status_code == 200
        assert response_other.json()["count"] == 0

    def test_anomalies_unauthorized(self, client):
        response = client.get("/api/v1/ai/anomalies")
        assert response.status_code == 401

    def test_anomalies_forbidden_checker(self, client, checker_auth_headers):
        response = client.get("/api/v1/ai/anomalies", headers=checker_auth_headers)
        assert response.status_code == 403

    def test_anomalies_forbidden_delivery_partner(self, client, delivery_partner_auth_headers):
        response = client.get("/api/v1/ai/anomalies", headers=delivery_partner_auth_headers)
        assert response.status_code == 403

    def test_anomalies_invalid_days_back_zero(self, client, auth_headers):
        response = client.get("/api/v1/ai/anomalies?days_back=0", headers=auth_headers)
        assert response.status_code == 422

    def test_anomalies_invalid_days_back_high(self, client, auth_headers):
        response = client.get("/api/v1/ai/anomalies?days_back=31", headers=auth_headers)
        assert response.status_code == 422


def _make_exception(db_session, subscription, start_date, end_date):
    exception = DeliveryException(
        subscription_id=subscription.id,
        exception_type="VACATION",
        start_date=start_date,
        end_date=end_date,
        reason="Vacation",
        status="ACTIVE",
        is_active=True,
    )
    db_session.add(exception)
    db_session.flush()
    return exception


def _make_payment(db_session, customer, amount, when=None):
    payment = CustomerPayment(
        customer_id=customer.id,
        amount=amount,
        payment_mode="CASH",
        payment_type="REGULAR",
        payment_date=when,
        is_active=True,
    )
    db_session.add(payment)
    db_session.flush()
    return payment


def _make_bill(db_session, customer, balance, due_date):
    bill = CustomerBill(
        customer_id=customer.id,
        bill_period_start=due_date - timedelta(days=30),
        bill_period_end=due_date,
        total_amount=balance,
        paid_amount=0,
        balance_amount=balance,
        status="PENDING",
        due_date=due_date,
        is_active=True,
    )
    db_session.add(bill)
    db_session.flush()
    return bill


class TestChurnRisk:
    def test_churn_high_declining_consumption(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 7):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=2)
        for offset in range(7, 21):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        items = response.json()["items"]
        item = next(i for i in items if i["customer_id"] == seed_customer.id)
        assert item["risk_level"] == "HIGH"
        assert item["risk_score"] >= 70
        factor = next(f for f in item["factors"] if f["factor"] == "declining_consumption")
        assert factor["weight"] == 30
        assert factor["contribution"] >= 20

    def test_churn_exception_and_missed_elevated(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 4):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        for offset in range(4, 7):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=0, status="NOT_DELIVERED")
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_payment(db_session, seed_customer, 100)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        item = next(i for i in response.json()["items"] if i["customer_id"] == seed_customer.id)
        assert item["risk_level"] in ("MEDIUM", "HIGH")
        factors = {f["factor"] for f in item["factors"]}
        assert "delivery_exceptions" in factors
        assert "missed_deliveries" in factors

    def test_churn_steady_low(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 21):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        _make_payment(db_session, seed_customer, 100)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        item = next(i for i in response.json()["items"] if i["customer_id"] == seed_customer.id)
        assert item["risk_level"] == "LOW"
        assert item["risk_score"] == 0

    def test_churn_outstanding_balance_factor(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 15):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        _make_payment(db_session, seed_customer, 100)
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        item = next(i for i in response.json()["items"] if i["customer_id"] == seed_customer.id)
        factor = next(f for f in item["factors"] if f["factor"] == "outstanding_balance")
        assert factor["weight"] == 15
        assert factor["contribution"] == 15

    def test_churn_route_filter(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_route, seed_second_customer,
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 21):
            qty = 2 if offset <= 6 else 10
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=qty)
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))

        sub2 = _make_subscription(db_session, seed_second_customer, seed_milk_type, morning=10, evening=0)
        emp2 = _ensure_employee(db_session, seed_second_route)
        for offset in range(1, 15):
            session = _make_session(db_session, seed_second_route, emp2, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_second_customer, seed_milk_type, delivered=10)
        _make_payment(db_session, seed_second_customer, 100)
        db_session.commit()

        response_a = client.get(f"/api/v1/ai/churn-risk?route_id={seed_route.id}", headers=auth_headers)
        assert response_a.status_code == 200
        ids_a = {i["customer_id"] for i in response_a.json()["items"]}
        assert seed_customer.id in ids_a
        assert seed_second_customer.id not in ids_a

        response_b = client.get(f"/api/v1/ai/churn-risk?route_id={seed_second_route.id}", headers=auth_headers)
        ids_b = {i["customer_id"] for i in response_b.json()["items"]}
        assert seed_second_customer.id in ids_b
        assert seed_customer.id not in ids_b

    def test_churn_limit(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_customer,
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 21):
            qty = 2 if offset <= 6 else 10
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=qty)
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))

        sub2 = _make_subscription(db_session, seed_second_customer, seed_milk_type, morning=10, evening=0)
        emp2 = _ensure_employee(db_session, seed_route)
        for offset in range(1, 15):
            session = _make_session(db_session, seed_route, emp2, today - timedelta(days=offset), shift="EVENING")
            _make_delivery(db_session, session, seed_second_customer, seed_milk_type, delivered=10)
        _make_payment(db_session, seed_second_customer, 100)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk?limit=1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["customer_id"] == seed_customer.id

    def test_churn_unauthorized(self, client):
        response = client.get("/api/v1/ai/churn-risk")
        assert response.status_code == 401

    def test_churn_forbidden_checker(self, client, checker_auth_headers):
        response = client.get("/api/v1/ai/churn-risk", headers=checker_auth_headers)
        assert response.status_code == 403

    def test_churn_forbidden_delivery_partner(self, client, delivery_partner_auth_headers):
        response = client.get("/api/v1/ai/churn-risk", headers=delivery_partner_auth_headers)
        assert response.status_code == 403

    def test_churn_invalid_limit_zero(self, client, auth_headers):
        response = client.get("/api/v1/ai/churn-risk?limit=0", headers=auth_headers)
        assert response.status_code == 422

    def test_churn_invalid_limit_high(self, client, auth_headers):
        response = client.get("/api/v1/ai/churn-risk?limit=101", headers=auth_headers)
        assert response.status_code == 422

    def test_churn_limit_max_boundary(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        db_session.commit()
        response = client.get("/api/v1/ai/churn-risk?limit=100", headers=auth_headers)
        assert response.status_code == 200
        assert 0 <= len(response.json()["items"]) <= 100

    def test_churn_no_history_default_risk(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        item = next(i for i in response.json()["items"] if i["customer_id"] == seed_customer.id)
        assert item["risk_level"] == "LOW"
        assert item["risk_score"] == 15
        factor = next(f for f in item["factors"] if f["factor"] == "payment_recency")
        assert factor["contribution"] == 15

    def test_churn_score_sum_invariant_capped(
        self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 8):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=0)
        for offset in range(8, 29):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        for offset in range(1, 8):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset), shift="EVENING")
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=0,
                           status="NOT_DELIVERED")
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        item = next(i for i in response.json()["items"] if i["customer_id"] == seed_customer.id)
        assert item["risk_level"] == "HIGH"
        assert item["risk_score"] == sum(f["contribution"] for f in item["factors"])
        assert item["risk_score"] <= 100
        assert {f["factor"] for f in item["factors"]} == {
            "declining_consumption", "delivery_exceptions", "missed_deliveries",
            "payment_recency", "outstanding_balance",
        }

    def test_churn_inactive_customer_and_subscription_excluded(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_route,
    ):
        _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        db_session.commit()

        inactive_sub_customer = Customer(
            customer_code="C00099",
            customer_name="Inactive Sub",
            primary_phone="9999999901",
            address="1 Inactive Way",
            route_id=seed_route.id,
            is_active=True,
        )
        db_session.add(inactive_sub_customer)
        db_session.flush()
        sub2 = _make_subscription(db_session, inactive_sub_customer, seed_milk_type, morning=10, evening=0)
        sub2.is_active = False

        inactive_customer = Customer(
            customer_code="C00098",
            customer_name="Inactive Cust",
            primary_phone="9999999902",
            address="2 Inactive Way",
            route_id=seed_second_route.id,
            is_active=False,
        )
        db_session.add(inactive_customer)
        db_session.flush()
        _make_subscription(db_session, inactive_customer, seed_milk_type, morning=10, evening=0)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk", headers=auth_headers)
        assert response.status_code == 200
        ids = {i["customer_id"] for i in response.json()["items"]}
        assert seed_customer.id in ids
        assert inactive_sub_customer.id not in ids
        assert inactive_customer.id not in ids

    def test_churn_nonexistent_route(self, client, auth_headers):
        response = client.get("/api/v1/ai/churn-risk?route_id=99999", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_churn_sorted_by_risk_score_desc(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, seed_second_customer,
    ):
        sub = _make_subscription(db_session, seed_customer, seed_milk_type, morning=10, evening=0)
        emp = _ensure_employee(db_session, seed_route)
        today = date.today()
        for offset in range(1, 7):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=2)
        for offset in range(7, 21):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset))
            _make_delivery(db_session, session, seed_customer, seed_milk_type, delivered=10)
        for _ in range(5):
            _make_exception(db_session, sub, today - timedelta(days=5), today - timedelta(days=3))
        _make_bill(db_session, seed_customer, 1000, today - timedelta(days=90))

        _make_subscription(db_session, seed_second_customer, seed_milk_type, morning=10, evening=0)
        for offset in range(1, 21):
            session = _make_session(db_session, seed_route, emp, today - timedelta(days=offset),
                                    shift="EVENING")
            _make_delivery(db_session, session, seed_second_customer, seed_milk_type, delivered=10)
        _make_payment(db_session, seed_second_customer, 100)
        db_session.commit()

        response = client.get("/api/v1/ai/churn-risk?limit=100", headers=auth_headers)
        assert response.status_code == 200
        scores = [i["risk_score"] for i in response.json()["items"]]
        assert scores == sorted(scores, reverse=True)


class TestInsights:
    def test_insights_narrative_with_mocked_client(
        self, client, auth_headers, db_session, seed_route, seed_customer,
        seed_milk_type, monkeypatch,
    ):
        captured = {}

        def fake_is_available():
            return True

        def fake_chat_completion(messages, max_tokens=None):
            captured["messages"] = messages
            return "This month the business delivered 885L of milk."

        monkeypatch.setattr("app.services.ai.client.is_available", fake_is_available)
        monkeypatch.setattr("app.services.ai.client.chat_completion", fake_chat_completion)

        response = client.get("/api/v1/ai/insights", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["stats_only"] is False
        assert data["narrative"] == "This month the business delivered 885L of milk."
        assert "forecast" in data
        assert "anomalies" in data
        assert "churn_risk" in data

        payload_text = " ".join(m.get("content", "") for m in captured["messages"])
        assert "9876543210" not in payload_text
        assert "123 Main St" not in payload_text

    def test_insights_stats_only_when_llm_disabled(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        response = client.get("/api/v1/ai/insights", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["stats_only"] is True
        assert data["narrative"] is None
        assert data["forecast"]["items"] is not None
        assert data["anomalies"]["count"] >= 0
        assert "churn_risk" in data
        assert "operational" in data

    def test_insights_stats_only_when_llm_raises(self, client, auth_headers, monkeypatch):
        from app.exceptions.ai import AIUnavailableError

        def fake_is_available():
            return True

        def fake_chat_completion(messages, max_tokens=None):
            raise AIUnavailableError()

        monkeypatch.setattr("app.services.ai.client.is_available", fake_is_available)
        monkeypatch.setattr("app.services.ai.client.chat_completion", fake_chat_completion)

        response = client.get("/api/v1/ai/insights", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["stats_only"] is True
        assert data["narrative"] is None

    def test_insights_owner_allowed(self, client, auth_headers):
        response = client.get("/api/v1/ai/insights", headers=auth_headers)
        assert response.status_code == 200

    def test_insights_admin_forbidden(self, client, admin_auth_headers):
        response = client.get("/api/v1/ai/insights", headers=admin_auth_headers)
        assert response.status_code == 403

    def test_insights_checker_forbidden(self, client, checker_auth_headers):
        response = client.get("/api/v1/ai/insights", headers=checker_auth_headers)
        assert response.status_code == 403

    def test_insights_unauthorized(self, client):
        response = client.get("/api/v1/ai/insights")
        assert response.status_code == 401

    def test_insights_invalid_date(self, client, auth_headers):
        response = client.get("/api/v1/ai/insights?from_date=not-a-date", headers=auth_headers)
        assert response.status_code == 422

    def test_insights_presets(self, client, auth_headers, monkeypatch):
        from app.services.reports.common import resolve_date_range

        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        presets = ("today", "yesterday", "this_week", "last_week",
                   "this_month", "last_month", "this_year")
        for preset in presets:
            expected_from, expected_to = resolve_date_range(preset)
            response = client.get(f"/api/v1/ai/insights?preset={preset}", headers=auth_headers)
            assert response.status_code == 200, preset
            data = response.json()
            assert data["stats_only"] is True
            assert data["data_range"]["from"] == str(expected_from), preset
            assert data["data_range"]["to"] == str(expected_to), preset

    def test_insights_custom_date_range(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        frm = (date.today() - timedelta(days=5)).isoformat()
        to = (date.today() - timedelta(days=1)).isoformat()
        response = client.get(
            f"/api/v1/ai/insights?from_date={frm}&to_date={to}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data_range"]["from"] == frm
        assert data["data_range"]["to"] == to

    def test_insights_from_date_only(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        frm = (date.today() - timedelta(days=5)).isoformat()
        response = client.get(f"/api/v1/ai/insights?from_date={frm}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data_range"]["from"] == frm
        assert data["data_range"]["to"] == frm

    def test_insights_reversed_range_echoed(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        frm = date.today().isoformat()
        to = (date.today() - timedelta(days=5)).isoformat()
        response = client.get(
            f"/api/v1/ai/insights?from_date={frm}&to_date={to}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data_range"]["from"] == frm
        assert data["data_range"]["to"] == to

    def test_insights_unknown_preset_falls_back(self, client, auth_headers, monkeypatch):
        from app.services.reports.common import resolve_date_range

        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        expected_from, expected_to = resolve_date_range()
        response = client.get("/api/v1/ai/insights?preset=bogus", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data_range"]["from"] == str(expected_from)
        assert data["data_range"]["to"] == str(expected_to)

    def test_insights_future_range(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        frm = (date.today() + timedelta(days=5)).isoformat()
        to = (date.today() + timedelta(days=10)).isoformat()
        response = client.get(
            f"/api/v1/ai/insights?from_date={frm}&to_date={to}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stats_only"] is True
        assert data["data_range"]["from"] == frm
        assert data["data_range"]["to"] == to

    def test_insights_refresh_param(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        response = client.get("/api/v1/ai/insights?refresh=true", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["stats_only"] is True


class TestChat:
    def test_chat_success_with_mocked_client(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "Downtown Route collected 500.00 this month.",
        )

        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "How much did Downtown Route collect this month?", "history": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "Downtown Route" in data["reply"]
        assert "from" in data["data_range"]
        assert "to" in data["data_range"]
        assert data["sources"]
        assert data["stats_only"] is False

    def test_chat_rate_limited(self, client, auth_headers, monkeypatch):
        from app.services.ai.chat import RateLimiter

        monkeypatch.setattr("app.services.ai.chat.rate_limiter", RateLimiter(20))
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "reply",
        )

        body = {"message": "hello", "history": []}
        for _ in range(20):
            response = client.post("/api/v1/ai/chat", headers=auth_headers, json=body)
            assert response.status_code == 200
        response = client.post("/api/v1/ai/chat", headers=auth_headers, json=body)
        assert response.status_code == 429

    def test_chat_llm_unavailable(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: False)
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 503

    def test_chat_llm_raises(self, client, auth_headers, monkeypatch):
        from app.exceptions.ai import AIUnavailableError

        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)

        def fake_chat_completion(messages, max_tokens=None):
            raise AIUnavailableError()

        monkeypatch.setattr("app.services.ai.client.chat_completion", fake_chat_completion)
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 503

    def test_chat_empty_message(self, client, auth_headers):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "", "history": []},
        )
        assert response.status_code == 422

    def test_chat_message_too_long(self, client, auth_headers):
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "x" * 2001, "history": []},
        )
        assert response.status_code == 422

    def test_chat_history_too_long(self, client, auth_headers):
        history = [{"role": "user", "content": "hi"}] * 9
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "hello", "history": history},
        )
        assert response.status_code == 422

    def test_chat_message_max_boundary(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "reply",
        )
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "x" * 2000, "history": []},
        )
        assert response.status_code == 200

    def test_chat_history_max_boundary(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "reply",
        )
        history = [{"role": "user", "content": "hi"}] * 8
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "hello", "history": history},
        )
        assert response.status_code == 200

    def test_chat_whitespace_message_passes_validation(self, client, auth_headers, monkeypatch):
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "reply",
        )
        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "   ", "history": []},
        )
        assert response.status_code == 200

    def test_chat_rate_limiter_sliding_window(self, client, auth_headers, monkeypatch):
        from app.services.ai.chat import RateLimiter

        clock = {"t": 0.0}
        monkeypatch.setattr("app.services.ai.chat.time.monotonic", lambda: clock["t"])
        monkeypatch.setattr("app.services.ai.chat.rate_limiter", RateLimiter(2))
        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr(
            "app.services.ai.client.chat_completion",
            lambda messages, max_tokens=None: "reply",
        )

        body = {"message": "hello", "history": []}
        assert client.post("/api/v1/ai/chat", headers=auth_headers, json=body).status_code == 200
        assert client.post("/api/v1/ai/chat", headers=auth_headers, json=body).status_code == 200
        assert client.post("/api/v1/ai/chat", headers=auth_headers, json=body).status_code == 429

        clock["t"] = 61.0
        assert client.post("/api/v1/ai/chat", headers=auth_headers, json=body).status_code == 200

    def test_chat_context_strips_pii(
        self, client, auth_headers, db_session, seed_route, seed_customer, monkeypatch
    ):
        captured = {}

        def fake_chat_completion(messages, max_tokens=None):
            captured["messages"] = messages
            return "reply"

        monkeypatch.setattr("app.services.ai.client.is_available", lambda: True)
        monkeypatch.setattr("app.services.ai.client.chat_completion", fake_chat_completion)

        response = client.post(
            "/api/v1/ai/chat",
            headers=auth_headers,
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 200
        payload_text = " ".join(m.get("content", "") for m in captured["messages"])
        assert "9876543210" not in payload_text
        assert "123 Main St" not in payload_text

    def test_chat_unauthorized(self, client):
        response = client.post(
            "/api/v1/ai/chat",
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 401

    def test_chat_forbidden_admin(self, client, admin_auth_headers):
        response = client.post(
            "/api/v1/ai/chat",
            headers=admin_auth_headers,
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 403

    def test_chat_forbidden_checker(self, client, checker_auth_headers):
        response = client.post(
            "/api/v1/ai/chat",
            headers=checker_auth_headers,
            json={"message": "hello", "history": []},
        )
        assert response.status_code == 403


class TestLlmPayload:
    def test_strip_sensitive_fields_nested(self):
        from app.services.ai.llm_payload import strip_sensitive_fields

        payload = {
            "customer": {
                "name": "X",
                "primary_phone": "123",
                "alternate_phone": "456",
                "email": "e@x.com",
                "address": "addr",
                "keep": 1,
            },
            "list": [{"address": "a"}, 1, "x"],
            "tuple": ({"email": "t"},),
            "safe": "keep",
        }
        out = strip_sensitive_fields(payload)
        text = str(out)
        assert "primary_phone" not in text
        assert "alternate_phone" not in text
        assert "address" not in text
        assert "email" not in text
        assert out["customer"]["keep"] == 1
        assert out["safe"] == "keep"
