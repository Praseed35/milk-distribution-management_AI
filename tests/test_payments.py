from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.customer_bill import CustomerBill, CustomerBillItem
from app.models.customer_payment import CustomerPayment
from app.models.daily_delivery import DailyDelivery
from app.models.delivery_session import DeliverySession
from app.models.milk_type import MilkType


# ─── Fixtures ───


@pytest.fixture
def seed_milk_type_with_price(db_session, seed_milk_type):
    seed_milk_type.unit_price = Decimal("50.00")
    db_session.commit()
    db_session.refresh(seed_milk_type)
    return seed_milk_type


@pytest.fixture
def seed_employee(db_session, seed_route):
    from app.models.employee import Employee
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
def seed_delivery_session(db_session, seed_route, seed_employee):
    from app.models.delivery_session import DeliverySession
    session = DeliverySession(
        route_id=seed_route.id,
        delivery_date="2026-07-01",
        shift="MORNING",
        delivery_partner_id=seed_employee.id,
        status="CLOSED",
        total_milk_loaded=10,
        reconciliation_status="BALANCED",
        is_active=True
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def seed_delivered_delivery(db_session, seed_delivery_session, seed_customer, seed_milk_type_with_price):
    delivery = DailyDelivery(
        session_id=seed_delivery_session.id,
        customer_id=seed_customer.id,
        milk_type_id=seed_milk_type_with_price.id,
        planned_quantity=2,
        delivered_quantity=2,
        delivery_status="DELIVERED",
        delivery_source="PLANNED",
        shift="MORNING",
        delivery_date="2026-07-01",
        is_active=True
    )
    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)
    return delivery


@pytest.fixture
def seed_generated_bill(db_session, seed_customer, seed_milk_type_with_price, seed_delivered_delivery):
    from app.services import payment_service
    from app.schemas.payment import BillGenerateRequest
    from datetime import date

    request = BillGenerateRequest(
        customer_id=seed_customer.id,
        bill_period_start=date(2026, 7, 1),
        bill_period_end=date(2026, 7, 31),
    )
    return payment_service.generate_bill(db_session, request)


@pytest.fixture
def seed_payment(db_session, seed_customer):
    payment = CustomerPayment(
        customer_id=seed_customer.id,
        amount=Decimal("100.00"),
        payment_mode="CASH",
        payment_type="ADVANCE",
        is_active=True
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


# ─── Test Create Payment ───


class TestCreateCustomerPayment:

    def test_create_advance_payment_success(
        self,
        client,
        seed_customer,
        seed_milk_type
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "500.00",
                "payment_mode": "CASH",
                "payment_type": "ADVANCE",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert Decimal(data["amount"]) == Decimal("500.00")
        assert data["payment_mode"] == "CASH"
        assert data["payment_type"] == "ADVANCE"
        assert data["customer_id"] == seed_customer.id

    def test_create_bill_payment_success(
        self,
        client,
        seed_customer,
        seed_generated_bill
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "50.00",
                "payment_mode": "UPI",
                "payment_type": "BILL_PAYMENT",
                "bill_id": seed_generated_bill.id,
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["payment_type"] == "BILL_PAYMENT"
        assert data["bill_id"] == seed_generated_bill.id
        assert data["payment_mode"] == "UPI"

    def test_create_payment_customer_not_found(
        self,
        client
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": 99999,
                "amount": "100.00",
                "payment_mode": "CASH",
                "payment_type": "ADVANCE",
            }
        )
        assert response.status_code == 404

    def test_create_payment_invalid_mode(
        self,
        client,
        seed_customer
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "100.00",
                "payment_mode": "INVALID",
                "payment_type": "ADVANCE",
            }
        )
        assert response.status_code == 422

    def test_create_payment_invalid_type(
        self,
        client,
        seed_customer
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "100.00",
                "payment_mode": "CASH",
                "payment_type": "INVALID",
            }
        )
        assert response.status_code == 422

    def test_create_bill_payment_bill_not_found(
        self,
        client,
        seed_customer
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "100.00",
                "payment_mode": "CASH",
                "payment_type": "BILL_PAYMENT",
                "bill_id": 99999,
            }
        )
        assert response.status_code == 404

    def test_create_bill_payment_without_bill_id(
        self,
        client,
        seed_customer
    ):
        response = client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "100.00",
                "payment_mode": "CASH",
                "payment_type": "BILL_PAYMENT",
            }
        )
        assert response.status_code == 404


# ─── Test Get Payments ───


class TestGetCustomerPayments:

    def test_get_all_payments(
        self,
        client,
        seed_payment
    ):
        response = client.get("/payments/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_payment_by_id(
        self,
        client,
        seed_payment
    ):
        response = client.get(f"/payments/{seed_payment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_payment.id
        assert Decimal(data["amount"]) == seed_payment.amount

    def test_get_payment_not_found(
        self,
        client
    ):
        response = client.get("/payments/99999")
        assert response.status_code == 404

    def test_get_payments_by_customer(
        self,
        client,
        seed_customer,
        seed_payment
    ):
        response = client.get(f"/payments/customer/{seed_customer.id}")
        assert response.status_code == 200
        assert len(response.json()) >= 1
        assert response.json()[0]["customer_id"] == seed_customer.id

    def test_get_payments_by_customer_not_found(
        self,
        client
    ):
        response = client.get("/payments/customer/99999")
        assert response.status_code == 404

    def test_get_payments_filter_by_mode(
        self,
        client,
        seed_payment
    ):
        response = client.get("/payments/?payment_mode=CASH")
        assert response.status_code == 200
        for p in response.json():
            assert p["payment_mode"] == "CASH"

    def test_get_payments_filter_by_type(
        self,
        client,
        seed_payment
    ):
        response = client.get("/payments/?payment_type=ADVANCE")
        assert response.status_code == 200
        for p in response.json():
            assert p["payment_type"] == "ADVANCE"


# ─── Test Update Payment ───


class TestUpdateCustomerPayment:

    def test_update_payment_success(
        self,
        client,
        seed_payment
    ):
        response = client.put(
            f"/payments/{seed_payment.id}",
            json={
                "amount": "200.00",
                "remarks": "Updated amount"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["amount"]) == Decimal("200.00")
        assert data["remarks"] == "Updated amount"

    def test_update_payment_not_found(
        self,
        client
    ):
        response = client.put(
            "/payments/99999",
            json={"amount": "100.00"}
        )
        assert response.status_code == 404


# ─── Test Delete Payment ───


class TestDeleteCustomerPayment:

    def test_delete_payment_success(
        self,
        client,
        seed_payment
    ):
        response = client.delete(f"/payments/{seed_payment.id}")
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_payment_not_found(
        self,
        client
    ):
        response = client.delete("/payments/99999")
        assert response.status_code == 404


# ─── Test Generate Bill ───


class TestGenerateCustomerBill:

    def test_generate_bill_success(
        self,
        client,
        seed_customer,
        seed_milk_type_with_price,
        seed_delivery_session,
        seed_delivered_delivery
    ):
        from datetime import date
        response = client.post(
            "/payments/bills/generate",
            json={
                "customer_id": seed_customer.id,
                "bill_period_start": "2026-07-01",
                "bill_period_end": "2026-07-31",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == seed_customer.id
        assert Decimal(data["total_amount"]) == Decimal("100.00")
        assert data["status"] == "PENDING"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert Decimal(data["items"][0]["unit_price"]) == Decimal("50.00")
        assert Decimal(data["items"][0]["amount"]) == Decimal("100.00")

    def test_generate_bill_customer_not_found(
        self,
        client
    ):
        from datetime import date
        response = client.post(
            "/payments/bills/generate",
            json={
                "customer_id": 99999,
                "bill_period_start": "2026-07-01",
                "bill_period_end": "2026-07-31",
            }
        )
        assert response.status_code == 404

    def test_generate_bill_no_deliveries(
        self,
        client,
        seed_customer
    ):
        from datetime import date
        response = client.post(
            "/payments/bills/generate",
            json={
                "customer_id": seed_customer.id,
                "bill_period_start": "2026-01-01",
                "bill_period_end": "2026-01-31",
            }
        )
        assert response.status_code == 400


# ─── Test Get Bills ───


class TestGetCustomerBills:

    def test_get_all_bills(
        self,
        client,
        seed_generated_bill
    ):
        response = client.get("/payments/bills/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_bill_by_id(
        self,
        client,
        seed_generated_bill
    ):
        response = client.get(f"/payments/bills/{seed_generated_bill.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_generated_bill.id
        assert len(data["items"]) >= 1

    def test_get_bill_not_found(
        self,
        client
    ):
        response = client.get("/payments/bills/99999")
        assert response.status_code == 404

    def test_get_bills_by_customer(
        self,
        client,
        seed_customer,
        seed_generated_bill
    ):
        response = client.get(f"/payments/bills/customer/{seed_customer.id}")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_bills_by_customer_not_found(
        self,
        client
    ):
        response = client.get("/payments/bills/customer/99999")
        assert response.status_code == 404

    def test_get_bills_filter_by_status(
        self,
        client,
        seed_generated_bill
    ):
        response = client.get("/payments/bills/?status=PENDING")
        assert response.status_code == 200
        for b in response.json():
            assert b["status"] == "PENDING"


# ─── Test Update Bill Status ───


class TestUpdateCustomerBillStatus:

    def test_update_bill_status_success(
        self,
        client,
        seed_generated_bill,
        seed_customer,
        seed_milk_type
    ):
        from app.models.customer_payment import CustomerPayment
        from decimal import Decimal

        response = client.put(
            f"/payments/bills/{seed_generated_bill.id}/status",
            json={"status": "PAID"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PAID"

    def test_update_bill_status_not_found(
        self,
        client
    ):
        response = client.put(
            "/payments/bills/99999/status",
            json={"status": "PAID"}
        )
        assert response.status_code == 404

    def test_update_bill_status_invalid(
        self,
        client,
        seed_generated_bill
    ):
        response = client.put(
            f"/payments/bills/{seed_generated_bill.id}/status",
            json={"status": "INVALID"}
        )
        assert response.status_code == 422


# ─── Test Outstanding Balance ───


class TestOutstandingBalance:

    def test_get_outstanding_balance(
        self,
        client,
        seed_customer,
        seed_generated_bill
    ):
        response = client.get(f"/payments/outstanding/{seed_customer.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == seed_customer.id
        assert Decimal(data["total_billed"]) == Decimal("100.00")
        assert Decimal(data["balance"]) == Decimal("100.00")

    def test_get_outstanding_balance_with_payment(
        self,
        client,
        seed_customer,
        seed_generated_bill
    ):
        client.post(
            "/payments/",
            json={
                "customer_id": seed_customer.id,
                "amount": "40.00",
                "payment_mode": "CASH",
                "payment_type": "BILL_PAYMENT",
                "bill_id": seed_generated_bill.id,
            }
        )

        response = client.get(f"/payments/outstanding/{seed_customer.id}")
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["total_paid"]) == Decimal("40.00")
        assert Decimal(data["balance"]) == Decimal("60.00")

    def test_outstanding_balance_customer_not_found(
        self,
        client
    ):
        response = client.get("/payments/outstanding/99999")
        assert response.status_code == 404
