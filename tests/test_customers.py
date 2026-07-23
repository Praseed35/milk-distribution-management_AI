class TestCreateCustomer:

    def test_create_customer_success(self, client, seed_route):
        response = client.post(
            "/customers/",
            json={
                "customer_name": "Jane Smith",
                "primary_phone": "9876543000",
                "alternate_phone": "9876543001",
                "address": "456 Oak Ave",
                "route_id": seed_route.id,
                "remarks": None
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Jane Smith"
        assert data["primary_phone"] == "9876543000"
        assert data["route_id"] == seed_route.id
        assert data["is_active"] is True
        assert data["customer_code"].startswith("C")

    def test_create_customer_auto_code(self, client, seed_route):
        for i in range(3):
            response = client.post(
                "/customers/",
                json={
                    "customer_name": f"Customer {i}",
                    "primary_phone": f"987654{3000 + i:04d}",
                    "route_id": seed_route.id
                }
            )
            assert response.status_code == 200

        response = client.get("/customers/")
        codes = [c["customer_code"] for c in response.json()]
        assert len(codes) == 3
        assert len(set(codes)) == 3

    def test_create_customer_route_not_found(self, client):
        response = client.post(
            "/customers/",
            json={
                "customer_name": "No Route",
                "primary_phone": "9876543010",
                "route_id": 9999
            }
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."

    def test_create_customer_inactive_route(
        self, client, db_session
    ):
        from app.models.route import Route
        route = Route(
            route_code="R_INACTIVE",
            route_name="Inactive Route",
            is_active=False
        )
        db_session.add(route)
        db_session.commit()
        db_session.refresh(route)

        response = client.post(
            "/customers/",
            json={
                "customer_name": "Bad Route Customer",
                "primary_phone": "9876543020",
                "route_id": route.id
            }
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

    def test_create_customer_same_phone_numbers(
        self, client, seed_route
    ):
        response = client.post(
            "/customers/",
            json={
                "customer_name": "Same Phone",
                "primary_phone": "9876543030",
                "alternate_phone": "9876543030",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 400
        assert "same" in response.json()["detail"].lower()

    def test_create_customer_duplicate_phone(
        self, client, seed_customer, seed_route
    ):
        response = client.post(
            "/customers/",
            json={
                "customer_name": "Duplicate Phone",
                "primary_phone": "9876543210",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_customer_missing_fields(self, client):
        response = client.post(
            "/customers/",
            json={
                "customer_name": "Incomplete"
            }
        )
        assert response.status_code == 422


class TestGetCustomers:

    def test_get_customers_empty(self, client):
        response = client.get("/customers/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_customers_with_data(
        self, client, seed_customer
    ):
        response = client.get("/customers/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["customer_name"] == "John Doe"

    def test_get_customer_by_id(self, client, seed_customer):
        response = client.get(f"/customers/{seed_customer.id}")
        assert response.status_code == 200
        assert response.json()["customer_code"] == "C00001"

    def test_get_customer_not_found(self, client):
        response = client.get("/customers/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found."

    def test_get_customer_excludes_inactive(
        self, client, seed_customer, db_session
    ):
        from app.models.customer import Customer
        inactive = Customer(
            customer_code="C99999",
            customer_name="Inactive",
            primary_phone="9876543999",
            route_id=seed_customer.route_id,
            is_active=False
        )
        db_session.add(inactive)
        db_session.commit()

        response = client.get("/customers/")
        assert len(response.json()) == 1


class TestUpdateCustomer:

    def test_update_customer_success(
        self, client, seed_customer, seed_route
    ):
        response = client.put(
            f"/customers/{seed_customer.id}",
            json={
                "customer_name": "Jane Updated",
                "primary_phone": "9876543210",
                "alternate_phone": "9876543211",
                "address": "789 New St",
                "route_id": seed_route.id,
                "remarks": "Updated"
            }
        )
        assert response.status_code == 200
        assert response.json()["customer_name"] == "Jane Updated"
        assert response.json()["address"] == "789 New St"

    def test_update_customer_not_found(self, client, seed_route):
        response = client.put(
            "/customers/9999",
            json={
                "customer_name": "Ghost",
                "primary_phone": "9876543050",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 404

    def test_update_customer_route_not_found(
        self, client, seed_customer
    ):
        response = client.put(
            f"/customers/{seed_customer.id}",
            json={
                "customer_name": "Updated",
                "primary_phone": "9876543210",
                "route_id": 9999
            }
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."

    def test_update_customer_inactive_route(
        self, client, seed_customer, db_session
    ):
        from app.models.route import Route
        route = Route(
            route_code="R_INACT",
            route_name="Inactive Route",
            is_active=False
        )
        db_session.add(route)
        db_session.commit()
        db_session.refresh(route)

        response = client.put(
            f"/customers/{seed_customer.id}",
            json={
                "customer_name": "Updated",
                "primary_phone": "9876543210",
                "route_id": route.id
            }
        )
        assert response.status_code == 400

    def test_update_customer_same_phone_numbers(
        self, client, seed_customer, seed_route
    ):
        response = client.put(
            f"/customers/{seed_customer.id}",
            json={
                "customer_name": "Same Phone",
                "primary_phone": "9876543210",
                "alternate_phone": "9876543210",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 400

    def test_update_customer_duplicate_phone(
        self, client, db_session, seed_route
    ):
        from app.models.customer import Customer
        c1 = Customer(
            customer_code="C00010",
            customer_name="First",
            primary_phone="9876543060",
            route_id=seed_route.id,
            is_active=True
        )
        c2 = Customer(
            customer_code="C00011",
            customer_name="Second",
            primary_phone="9876543070",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add_all([c1, c2])
        db_session.commit()
        db_session.refresh(c1)

        response = client.put(
            f"/customers/{c1.id}",
            json={
                "customer_name": "First Updated",
                "primary_phone": "9876543070",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestDeleteCustomer:

    def test_delete_customer_success(
        self, client, seed_customer
    ):
        response = client.delete(
            f"/customers/{seed_customer.id}"
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        get_response = client.get(
            f"/customers/{seed_customer.id}"
        )
        assert get_response.status_code == 404

    def test_delete_customer_not_found(self, client):
        response = client.delete("/customers/9999")
        assert response.status_code == 404

    def test_delete_customer_soft_delete_only(
        self, client, seed_customer, db_session
    ):
        response = client.delete(
            f"/customers/{seed_customer.id}"
        )
        assert response.status_code == 200

        from app.models.customer import Customer
        db_session.expire_all()
        customer = db_session.query(Customer).filter(
            Customer.id == seed_customer.id
        ).first()
        assert customer is not None
        assert customer.is_active is False
