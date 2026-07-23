class TestCreateRoute:

    def test_create_route_success(self, client):
        response = client.post(
            "/routes/",
            json={
                "route_code": "R100",
                "route_name": "East Side",
                "description": "East side delivery"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["route_code"] == "R100"
        assert data["route_name"] == "East Side"
        assert data["is_active"] is True

    def test_create_route_duplicate_code(self, client, seed_route):
        response = client.post(
            "/routes/",
            json={
                "route_code": "R001",
                "route_name": "New Route",
                "description": "Different route"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_route_duplicate_name(self, client, seed_route):
        response = client.post(
            "/routes/",
            json={
                "route_code": "R999",
                "route_name": "Downtown Route",
                "description": "Different route"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_route_missing_fields(self, client):
        response = client.post(
            "/routes/",
            json={
                "route_code": "R200"
            }
        )
        assert response.status_code == 422


class TestGetRoutes:

    def test_get_routes_empty(self, client):
        response = client.get("/routes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_routes_with_data(self, client, seed_route):
        response = client.get("/routes/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["route_code"] == "R001"

    def test_get_route_by_id(self, client, seed_route):
        response = client.get(f"/routes/{seed_route.id}")
        assert response.status_code == 200
        assert response.json()["route_name"] == "Downtown Route"

    def test_get_route_not_found(self, client):
        response = client.get("/routes/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."


class TestUpdateRoute:

    def test_update_route_success(self, client, seed_route):
        response = client.put(
            f"/routes/{seed_route.id}",
            json={
                "route_code": "R001",
                "route_name": "Updated Downtown",
                "description": "Updated description"
            }
        )
        assert response.status_code == 200
        assert response.json()["route_name"] == "Updated Downtown"
        assert response.json()["description"] == "Updated description"

    def test_update_route_not_found(self, client):
        response = client.put(
            "/routes/9999",
            json={
                "route_code": "R999",
                "route_name": "Ghost Route",
                "description": "Does not exist"
            }
        )
        assert response.status_code == 404

    def test_update_route_duplicate_code(
        self, client, db_session
    ):
        from app.models.route import Route
        r1 = Route(
            route_code="R10",
            route_name="Route A",
            is_active=True
        )
        r2 = Route(
            route_code="R20",
            route_name="Route B",
            is_active=True
        )
        db_session.add_all([r1, r2])
        db_session.commit()
        db_session.refresh(r1)
        db_session.refresh(r2)

        response = client.put(
            f"/routes/{r1.id}",
            json={
                "route_code": "R20",
                "route_name": "Route A Updated",
                "description": None
            }
        )
        assert response.status_code == 400

    def test_update_route_duplicate_name(
        self, client, db_session
    ):
        from app.models.route import Route
        r1 = Route(
            route_code="R30",
            route_name="Route C",
            is_active=True
        )
        r2 = Route(
            route_code="R40",
            route_name="Route D",
            is_active=True
        )
        db_session.add_all([r1, r2])
        db_session.commit()
        db_session.refresh(r1)
        db_session.refresh(r2)

        response = client.put(
            f"/routes/{r1.id}",
            json={
                "route_code": "R30",
                "route_name": "Route D",
                "description": None
            }
        )
        assert response.status_code == 400


class TestDeleteRoute:

    def test_delete_route_success(self, client, seed_route):
        response = client.delete(f"/routes/{seed_route.id}")
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        get_response = client.get(f"/routes/{seed_route.id}")
        assert get_response.status_code == 404

    def test_delete_route_not_found(self, client):
        response = client.delete("/routes/9999")
        assert response.status_code == 404

    def test_delete_route_soft_delete_only(
        self, client, seed_route, db_session
    ):
        response = client.delete(f"/routes/{seed_route.id}")
        assert response.status_code == 200

        from app.models.route import Route
        db_session.expire_all()
        route = db_session.query(Route).filter(
            Route.id == seed_route.id
        ).first()
        assert route is not None
        assert route.is_active is False
