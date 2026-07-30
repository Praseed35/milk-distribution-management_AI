from datetime import date, datetime, timedelta

import pytest


class TestRouteDelivery:
    def test_route_report_success(self, client, auth_headers, db_session, seed_route, seed_customer, seed_milk_type, seed_delivery_session):
        from app.models.daily_delivery import DailyDelivery
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
            is_active=True,
        )
        db_session.add(delivery)
        db_session.commit()
        response = client.get(
            f"/reports/route-delivery?preset=today&route_id={seed_route.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert data["data"][0]["route_id"] == seed_route.id
        assert data["data"][0]["route_name"] == seed_route.route_name

    def test_route_report_empty_data(self, client, auth_headers, seed_route):
        response = client.get(
            f"/reports/route-delivery?from_date=2099-01-01&to_date=2099-01-31&route_id={seed_route.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_route_report_unauthorized(self, client):
        response = client.get("/reports/route-delivery?preset=today")
        assert response.status_code == 401

    def test_route_report_delivery_partner_wrong_route(self, client, delivery_partner_auth_headers, seed_second_route):
        response = client.get(
            f"/reports/route-delivery?route_id={seed_second_route.id}",
            headers=delivery_partner_auth_headers,
        )
        assert response.status_code == 403

    def test_route_report_csv(self, client, auth_headers, seed_route):
        response = client.get(
            f"/reports/route-delivery?preset=today&format=csv&route_id={seed_route.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]


class TestRevenue:
    def test_revenue_success(self, client, auth_headers, seed_customer, seed_customer_bill, seed_customer_payment):
        response = client.get(
            "/reports/revenue?preset=this_month",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] >= 600.0
        assert data["customer_bill_revenue"] >= 600.0

    def test_revenue_forbidden_for_admin(self, client, admin_auth_headers):
        response = client.get(
            "/reports/revenue?preset=this_month",
            headers=admin_auth_headers,
        )
        assert response.status_code == 403

    def test_revenue_unauthorized(self, client):
        response = client.get("/reports/revenue?preset=this_month")
        assert response.status_code == 401

    def test_revenue_empty(self, client, auth_headers):
        response = client.get(
            "/reports/revenue?from_date=2099-01-01&to_date=2099-01-31",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 0


class TestCollectionEfficiency:
    def test_collection_success(self, client, auth_headers, seed_customer, seed_customer_bill, seed_customer_payment):
        response = client.get(
            "/reports/collection-efficiency",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        item = data["data"][0]
        assert item["total_billed"] == 1000.0
        assert item["total_paid"] == 600.0
        assert item["balance"] == 400.0
        assert item["collection_percentage"] == 60.0

    def test_collection_zero_scenario(self, client, auth_headers, seed_customer):
        response = client.get(
            "/reports/collection-efficiency",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["data"]:
            if item["customer_id"] == seed_customer.id:
                assert item["total_billed"] == 0
                assert item["collection_percentage"] == 0

    def test_collection_forbidden_for_checker(self, client, checker_auth_headers):
        response = client.get(
            "/reports/collection-efficiency",
            headers=checker_auth_headers,
        )
        assert response.status_code == 403

    def test_collection_route_filter(self, client, auth_headers, seed_route, seed_customer, seed_customer_bill, seed_customer_payment):
        response = client.get(
            f"/reports/collection-efficiency?route_id={seed_route.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestCustomerConsumption:
    def test_consumption_success(self, client, auth_headers, seed_customer, seed_delivery_session, seed_milk_type):
        from app.models.daily_delivery import DailyDelivery
        today = date.today()
        for i in range(5):
            d = DailyDelivery(
                session_id=seed_delivery_session.id,
                customer_id=seed_customer.id,
                milk_type_id=seed_milk_type.id,
                planned_quantity=2,
                delivered_quantity=2,
                delivery_status="DELIVERED",
                delivery_source="PLANNED",
                shift="MORNING",
                delivery_date=today - timedelta(days=i),
                is_active=True,
            )
            auth_headers  # reference
        response = client.get(
            f"/reports/customer/{seed_customer.id}/consumption?preset=this_month",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_consumption_not_found(self, client, auth_headers):
        response = client.get(
            "/reports/customer/99999/consumption?preset=this_month",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_consumption_unauthorized(self, client):
        response = client.get("/reports/customer/1/consumption?preset=this_month")
        assert response.status_code == 401


class TestTokenUtilization:
    def test_token_utilization_success(self, client, auth_headers, seed_customer, seed_token_identity, seed_token_book_issue):
        response = client.get(
            "/reports/token-utilization",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_token_utilization_forbidden_for_checker(self, client, checker_auth_headers):
        response = client.get(
            "/reports/token-utilization",
            headers=checker_auth_headers,
        )
        assert response.status_code == 403


class TestOperationalDashboard:
    def test_dashboard_success(self, client, auth_headers, seed_route, seed_customer, seed_delivery_session):
        response = client.get(
            "/reports/dashboard",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "unclosed_sessions" in data

    def test_dashboard_unauthorized(self, client):
        response = client.get("/reports/dashboard")
        assert response.status_code == 401


class TestRBAC:
    def test_owner_can_access_all(self, client, auth_headers):
        for endpoint in ["/reports/route-delivery?preset=today", "/reports/dashboard", "/reports/collection-efficiency?preset=today"]:
            r = client.get(endpoint, headers=auth_headers)
            assert r.status_code in (200, 422), f"{endpoint} returned {r.status_code}"

    def test_delivery_partner_route_delivery(self, client, delivery_partner_auth_headers, seed_route):
        r = client.get("/reports/route-delivery?preset=today", headers=delivery_partner_auth_headers)
        assert r.status_code in (200, 422)

    def test_delivery_partner_dashboard(self, client, delivery_partner_auth_headers):
        r = client.get("/reports/dashboard", headers=delivery_partner_auth_headers)
        assert r.status_code == 200

    def test_delivery_partner_blocked_revenue(self, client, delivery_partner_auth_headers):
        r = client.get("/reports/revenue?preset=this_month", headers=delivery_partner_auth_headers)
        assert r.status_code == 403
