class TestCreateSubscription:

    def test_create_subscription_success(
        self, client, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 2,
                "evening_quantity": 1,
                "status": "ACTIVE",
                "remarks": "Test subscription"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == seed_customer.id
        assert data["milk_type_id"] == seed_milk_type.id
        assert data["morning_quantity"] == 2
        assert data["evening_quantity"] == 1
        assert data["status"] == "ACTIVE"
        assert data["is_active"] is True

    def test_create_subscription_morning_only(
        self, client, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 3,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["morning_quantity"] == 3
        assert data["evening_quantity"] == 0

    def test_create_subscription_evening_only(
        self, client, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 0,
                "evening_quantity": 2
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["morning_quantity"] == 0
        assert data["evening_quantity"] == 2

    def test_create_subscription_zero_quantities(
        self, client, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 0,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 400
        assert "quantity" in response.json()["detail"].lower()

    def test_create_subscription_customer_not_found(
        self, client, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": 9999,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 1,
                "evening_quantity": 1
            }
        )
        assert response.status_code == 404

    def test_create_subscription_milk_type_not_found(
        self, client, seed_customer
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": 9999,
                "morning_quantity": 1,
                "evening_quantity": 1
            }
        )
        assert response.status_code == 404

    def test_create_subscription_duplicate(
        self, client, seed_subscription, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 1,
                "evening_quantity": 1
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_subscription_inactive_customer(
        self, client, db_session, seed_milk_type, seed_route
    ):
        from app.models.customer import Customer
        customer = Customer(
            customer_code="C_INACTIVE",
            customer_name="Inactive Customer",
            primary_phone="9999999001",
            route_id=seed_route.id,
            is_active=False
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": 1,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 404

    def test_create_subscription_inactive_milk_type(
        self, client, seed_customer, db_session
    ):
        from app.models.milk_type import MilkType
        milk_type = MilkType(
            milk_name="Inactive Milk",
            volume_ml=500,
            is_active=False
        )
        db_session.add(milk_type)
        db_session.commit()
        db_session.refresh(milk_type)

        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": milk_type.id,
                "morning_quantity": 1,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 404

    def test_create_subscription_missing_fields(self, client):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": 1
            }
        )
        assert response.status_code == 422

    def test_create_subscription_negative_quantity(
        self, client, seed_customer, seed_milk_type
    ):
        response = client.post(
            "/subscriptions/",
            json={
                "customer_id": seed_customer.id,
                "milk_type_id": seed_milk_type.id,
                "morning_quantity": -1,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 422


class TestGetSubscriptions:

    def test_get_all_subscriptions_empty(self, client):
        response = client.get("/subscriptions/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_all_subscriptions_with_data(
        self, client, seed_subscription
    ):
        response = client.get("/subscriptions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        sub = data[0]
        assert "customer_code" in sub
        assert "customer_name" in sub
        assert "route_name" in sub
        assert "milk_type_name" in sub
        assert "milk_type_volume" in sub

    def test_get_subscription_by_id(
        self, client, seed_subscription
    ):
        response = client.get(
            f"/subscriptions/{seed_subscription.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_subscription.id
        assert "customer" in data
        assert "milk_type" in data
        assert data["customer"]["id"] == seed_subscription.customer_id
        assert data["milk_type"]["id"] == seed_subscription.milk_type_id

    def test_get_subscription_not_found(self, client):
        response = client.get("/subscriptions/99999")
        assert response.status_code == 404

    def test_get_subscriptions_by_customer(
        self, client, seed_subscription, seed_customer
    ):
        response = client.get(
            f"/subscriptions/customer/{seed_customer.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["customer_id"] == seed_customer.id

    def test_get_subscriptions_by_customer_not_found(self, client):
        response = client.get("/subscriptions/customer/99999")
        assert response.status_code == 404

    def test_get_subscriptions_by_customer_empty(
        self, client, db_session, seed_route
    ):
        from app.models.customer import Customer
        customer = Customer(
            customer_code="C_EMPTY",
            customer_name="Empty Customer",
            primary_phone="9999999099",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        response = client.get(
            f"/subscriptions/customer/{customer.id}"
        )
        assert response.status_code == 200
        assert response.json() == []


class TestUpdateSubscription:

    def test_update_subscription_success(
        self, client, seed_subscription
    ):
        response = client.put(
            f"/subscriptions/{seed_subscription.id}",
            json={
                "morning_quantity": 5,
                "evening_quantity": 3,
                "remarks": "Updated quantities"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["morning_quantity"] == 5
        assert data["evening_quantity"] == 3
        assert data["remarks"] == "Updated quantities"

    def test_update_subscription_partial(
        self, client, seed_subscription
    ):
        response = client.put(
            f"/subscriptions/{seed_subscription.id}",
            json={
                "remarks": "Only remarks updated"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["remarks"] == "Only remarks updated"

    def test_update_subscription_not_found(self, client):
        response = client.put(
            "/subscriptions/99999",
            json={
                "morning_quantity": 1
            }
        )
        assert response.status_code == 404

    def test_update_subscription_zero_quantities(
        self, client, seed_subscription
    ):
        response = client.put(
            f"/subscriptions/{seed_subscription.id}",
            json={
                "morning_quantity": 0,
                "evening_quantity": 0
            }
        )
        assert response.status_code == 400
        assert "quantity" in response.json()["detail"].lower()

    def test_update_subscription_status(
        self, client, seed_subscription
    ):
        response = client.put(
            f"/subscriptions/{seed_subscription.id}",
            json={
                "status": "PAUSED"
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PAUSED"


class TestDeleteSubscription:

    def test_delete_subscription_success(
        self, client, seed_subscription
    ):
        response = client.delete(
            f"/subscriptions/{seed_subscription.id}"
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False
        assert response.json()["status"] == "INACTIVE"

        get_response = client.get(
            f"/subscriptions/{seed_subscription.id}"
        )
        assert get_response.status_code == 404

    def test_delete_subscription_not_found(self, client):
        response = client.delete("/subscriptions/99999")
        assert response.status_code == 404

    def test_delete_subscription_already_inactive(
        self, client, seed_subscription
    ):
        response = client.delete(
            f"/subscriptions/{seed_subscription.id}"
        )
        assert response.status_code == 200

        response2 = client.delete(
            f"/subscriptions/{seed_subscription.id}"
        )
        assert response2.status_code == 404

    def test_delete_subscription_soft_delete_only(
        self, client, seed_subscription, db_session
    ):
        sub_id = seed_subscription.id
        response = client.delete(f"/subscriptions/{sub_id}")
        assert response.status_code == 200

        from app.models.subscription import Subscription
        db_session.expire_all()
        sub = db_session.query(Subscription).filter(
            Subscription.id == sub_id
        ).first()
        assert sub is not None
        assert sub.is_active is False

    def test_deleted_subscription_hidden_from_list(
        self, client, seed_subscription, seed_customer
    ):
        response = client.get("/subscriptions/")
        initial_count = len(response.json())

        client.delete(f"/subscriptions/{seed_subscription.id}")

        response = client.get("/subscriptions/")
        assert len(response.json()) == initial_count - 1

    def test_deleted_subscription_hidden_from_customer_list(
        self, client, seed_subscription, seed_customer
    ):
        response = client.get(
            f"/subscriptions/customer/{seed_customer.id}"
        )
        initial_count = len(response.json())

        client.delete(f"/subscriptions/{seed_subscription.id}")

        response = client.get(
            f"/subscriptions/customer/{seed_customer.id}"
        )
        assert len(response.json()) == initial_count - 1
