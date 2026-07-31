import pytest
from datetime import datetime, timedelta


class TestCreateDeliveryException:

    def test_create_delivery_exception_success(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "HOLIDAY",
            "start_date": datetime(2026, 9, 1).isoformat(),
            "end_date": datetime(2026, 9, 3).isoformat(),
            "reason": "Public holiday"
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subscription_id"] == seed_subscription.id
        assert data["exception_type"] == "HOLIDAY"
        assert data["reason"] == "Public holiday"
        assert data["is_active"] is True
        assert data["status"] == "ACTIVE"

    def test_create_delivery_exception_no_end_date(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "NO_MILK",
            "start_date": datetime(2026, 10, 1).isoformat(),
            "reason": "Supplier issue"
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["end_date"] is None
        assert data["exception_type"] == "NO_MILK"

    def test_create_delivery_exception_with_shift(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "shift": "MORNING",
            "start_date": datetime(2026, 12, 10).isoformat(),
            "end_date": datetime(2026, 12, 12).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        assert response.json()["shift"] == "MORNING"

    def test_create_delivery_exception_invalid_shift(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "shift": "NOON",
            "start_date": datetime(2026, 12, 20).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 422

    def test_create_delivery_exception_overlaps_whole_day(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "shift": "MORNING",
            "start_date": datetime(2026, 8, 3).isoformat(),
            "end_date": datetime(2026, 8, 7).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 400

    def test_create_delivery_exception_whole_day_overlaps_shift(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 8, 3).isoformat(),
            "end_date": datetime(2026, 8, 7).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 400

    def test_create_delivery_exception_same_shift_overlap(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        client.post(
            "/delivery-exceptions/",
            json={
                "subscription_id": seed_subscription.id,
                "exception_type": "VACATION",
                "shift": "MORNING",
                "start_date": datetime(2026, 12, 1).isoformat(),
                "end_date": datetime(2026, 12, 5).isoformat()
            }
        )

        response = client.post(
            "/delivery-exceptions/",
            json={
                "subscription_id": seed_subscription.id,
                "exception_type": "HOLIDAY",
                "shift": "MORNING",
                "start_date": datetime(2026, 12, 4).isoformat(),
                "end_date": datetime(2026, 12, 6).isoformat()
            }
        )

        assert response.status_code == 400

    def test_create_delivery_exception_different_shifts_coexist(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response_morning = client.post(
            "/delivery-exceptions/",
            json={
                "subscription_id": seed_subscription.id,
                "exception_type": "VACATION",
                "shift": "MORNING",
                "start_date": datetime(2026, 12, 10).isoformat(),
                "end_date": datetime(2026, 12, 12).isoformat()
            }
        )

        response_evening = client.post(
            "/delivery-exceptions/",
            json={
                "subscription_id": seed_subscription.id,
                "exception_type": "HOLIDAY",
                "shift": "EVENING",
                "start_date": datetime(2026, 12, 11).isoformat(),
                "end_date": datetime(2026, 12, 12).isoformat()
            }
        )

        assert response_morning.status_code == 201
        assert response_evening.status_code == 201

    def test_create_delivery_exception_inactive_subscription(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        seed_subscription.is_active = False
        db_session.commit()

        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 11, 1).isoformat(),
            "end_date": datetime(2026, 11, 5).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 404

    def test_create_delivery_exception_nonexistent_subscription(
        self,
        client,
        db_session,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": 99999,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 12, 1).isoformat(),
            "end_date": datetime(2026, 12, 5).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 404

    def test_create_delivery_exception_end_before_start(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 8, 10).isoformat(),
            "end_date": datetime(2026, 8, 5).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 400

    def test_create_delivery_exception_overlap(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 8, 3).isoformat(),
            "end_date": datetime(2026, 8, 7).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 400

    def test_create_delivery_exception_adjacent_dates(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "HOLIDAY",
            "start_date": datetime(2026, 8, 6).isoformat(),
            "end_date": datetime(2026, 8, 10).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201

    def test_create_delivery_exception_invalid_type(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "",
            "start_date": datetime(2026, 6, 1).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 422

    def test_create_delivery_exception_missing_subscription_id(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "exception_type": "VACATION",
            "start_date": datetime(2026, 8, 1).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 422


class TestGetAllDeliveryExceptions:

    def test_get_all_delivery_exceptions_empty(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get("/delivery-exceptions/")

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_all_delivery_exceptions_returns_data(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get("/delivery-exceptions/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        first = data[0]
        assert "id" in first
        assert "subscription_id" in first
        assert "customer_code" in first
        assert "customer_name" in first
        assert "route_name" in first
        assert "exception_type" in first
        assert "shift" in first
        assert "start_date" in first
        assert "is_active" in first


class TestGetDeliveryExceptionById:

    def test_get_delivery_exception_by_id_success(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get(
            f"/delivery-exceptions/{seed_delivery_exception.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_delivery_exception.id
        assert data["exception_type"] == "VACATION"
        assert data["reason"] == "Family vacation"
        assert "shift" in data
        assert "subscription" in data
        assert "customer" in data["subscription"]

    def test_get_delivery_exception_by_id_not_found(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get("/delivery-exceptions/99999")

        assert response.status_code == 404


class TestGetDeliveryExceptionsBySubscriptionId:

    def test_get_exceptions_by_subscription_success(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get(
            f"/delivery-exceptions/subscription/{seed_subscription.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["subscription_id"] == seed_subscription.id

    def test_get_exceptions_by_subscription_empty(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.get("/delivery-exceptions/subscription/99999")

        assert response.status_code == 404


class TestUpdateDeliveryException:

    def test_update_exception_type(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={"exception_type": "HOLIDAY"}
        )

        assert response.status_code == 200
        assert response.json()["exception_type"] == "HOLIDAY"

    def test_update_reason(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={"reason": "Updated reason"}
        )

        assert response.status_code == 200
        assert response.json()["reason"] == "Updated reason"

    def test_update_dates(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={
                "start_date": datetime(2026, 8, 2).isoformat(),
                "end_date": datetime(2026, 8, 6).isoformat()
            }
        )

        assert response.status_code == 200
        assert "2026-08-02" in response.json()["start_date"]

    def test_update_status(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={"status": "COMPLETED"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

    def test_update_shift(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={"shift": "EVENING"}
        )

        assert response.status_code == 200
        assert response.json()["shift"] == "EVENING"

    def test_update_shift_clear_to_whole_day(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        from app.models.delivery_exception import DeliveryException

        seed_delivery_exception.shift = "MORNING"
        db_session.commit()

        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={"shift": None}
        )

        assert response.status_code == 200
        assert response.json()["shift"] is None

    def test_update_shift_overlap(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        from app.models.delivery_exception import DeliveryException

        first = DeliveryException(
            subscription_id=seed_subscription.id,
            exception_type="HOLIDAY",
            shift="MORNING",
            start_date=datetime(2026, 9, 1),
            end_date=datetime(2026, 9, 5),
            status="ACTIVE",
            is_active=True
        )
        db_session.add(first)
        second = DeliveryException(
            subscription_id=seed_subscription.id,
            exception_type="VACATION",
            shift="MORNING",
            start_date=datetime(2026, 9, 2),
            end_date=datetime(2026, 9, 4),
            status="ACTIVE",
            is_active=True
        )
        db_session.add(second)
        db_session.commit()
        db_session.refresh(first)
        db_session.refresh(second)

        response = client.put(
            f"/delivery-exceptions/{second.id}",
            json={
                "start_date": datetime(2026, 9, 1).isoformat(),
                "end_date": datetime(2026, 9, 3).isoformat()
            }
        )

        assert response.status_code == 400

    def test_update_not_found(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            "/delivery-exceptions/99999",
            json={"exception_type": "HOLIDAY"}
        )

        assert response.status_code == 404

    def test_update_end_before_start(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.put(
            f"/delivery-exceptions/{seed_delivery_exception.id}",
            json={
                "start_date": datetime(2026, 8, 10).isoformat(),
                "end_date": datetime(2026, 8, 5).isoformat()
            }
        )

        assert response.status_code == 400

    def test_update_overlap_with_existing(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        from app.models.delivery_exception import DeliveryException

        second = DeliveryException(
            subscription_id=seed_subscription.id,
            exception_type="HOLIDAY",
            start_date=datetime(2026, 9, 1),
            end_date=datetime(2026, 9, 5),
            status="ACTIVE",
            is_active=True
        )
        db_session.add(second)
        db_session.commit()
        db_session.refresh(second)

        response = client.put(
            f"/delivery-exceptions/{second.id}",
            json={
                "start_date": datetime(2026, 8, 3).isoformat(),
                "end_date": datetime(2026, 8, 7).isoformat()
            }
        )

        assert response.status_code == 400


class TestDeleteDeliveryException:

    def test_delete_delivery_exception_success(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.delete(
            f"/delivery-exceptions/{seed_delivery_exception.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["status"] == "CANCELLED"

    def test_delete_delivery_exception_not_found(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        response = client.delete("/delivery-exceptions/99999")

        assert response.status_code == 404

    def test_delete_delivery_exception_already_inactive(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        client.delete(
            f"/delivery-exceptions/{seed_delivery_exception.id}"
        )

        response = client.delete(
            f"/delivery-exceptions/{seed_delivery_exception.id}"
        )

        assert response.status_code == 404


class TestDeliveryExceptionStatuses:

    def test_create_vacation_exception(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "VACATION",
            "start_date": datetime(2026, 7, 1).isoformat(),
            "end_date": datetime(2026, 7, 5).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        assert response.json()["exception_type"] == "VACATION"

    def test_create_holiday_exception(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "HOLIDAY",
            "start_date": datetime(2026, 7, 15).isoformat(),
            "end_date": datetime(2026, 7, 15).isoformat()
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        assert response.json()["exception_type"] == "HOLIDAY"

    def test_create_no_milk_exception(
        self,
        client,
        db_session,
        seed_subscription,
        seed_delivery_exception
    ):
        exception_data = {
            "subscription_id": seed_subscription.id,
            "exception_type": "NO_MILK",
            "start_date": datetime(2026, 7, 20).isoformat(),
            "reason": "No milk available from supplier"
        }

        response = client.post(
            "/delivery-exceptions/",
            json=exception_data
        )

        assert response.status_code == 201
        assert response.json()["exception_type"] == "NO_MILK"
