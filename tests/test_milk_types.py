class TestCreateMilkType:

    def test_create_milk_type_success(self, client):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "Toned Milk",
                "volume_ml": 500,
                "description": "Low fat toned milk"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["milk_name"] == "Toned Milk"
        assert data["volume_ml"] == 500
        assert data["is_active"] is True

    def test_create_milk_type_duplicate_name(
        self, client, seed_milk_type
    ):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "Full Cream Milk",
                "volume_ml": 500,
                "description": "Duplicate"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_milk_type_missing_fields(self, client):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "Incomplete"
            }
        )
        assert response.status_code == 422

    def test_create_milk_type_zero_volume(self, client):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "Zero Volume",
                "volume_ml": 0,
                "description": "Should fail"
            }
        )
        assert response.status_code == 422

    def test_create_milk_type_negative_volume(self, client):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "Negative",
                "volume_ml": -1,
                "description": "Should fail"
            }
        )
        assert response.status_code == 422

    def test_create_milk_type_without_description(self, client):
        response = client.post(
            "/milk-types/",
            json={
                "milk_name": "No Desc",
                "volume_ml": 250
            }
        )
        assert response.status_code == 200
        assert response.json()["description"] is None


class TestGetMilkTypes:

    def test_get_milk_types_empty(self, client):
        response = client.get("/milk-types/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_milk_types_with_data(
        self, client, seed_milk_type
    ):
        response = client.get("/milk-types/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["milk_name"] == "Full Cream Milk"

    def test_get_milk_type_by_id(
        self, client, seed_milk_type
    ):
        response = client.get(
            f"/milk-types/{seed_milk_type.id}"
        )
        assert response.status_code == 200
        assert response.json()["milk_name"] == "Full Cream Milk"

    def test_get_milk_type_not_found(self, client):
        response = client.get("/milk-types/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Milk type not found."

    def test_get_milk_types_excludes_inactive(
        self, client, db_session
    ):
        from app.models.milk_type import MilkType
        inactive = MilkType(
            milk_name="Inactive Milk",
            volume_ml=250,
            is_active=False
        )
        db_session.add(inactive)
        db_session.commit()

        response = client.get("/milk-types/")
        assert len(response.json()) == 0


class TestUpdateMilkType:

    def test_update_milk_type_success(
        self, client, seed_milk_type
    ):
        response = client.put(
            f"/milk-types/{seed_milk_type.id}",
            json={
                "milk_name": "Updated Milk",
                "volume_ml": 500,
                "description": "Updated description"
            }
        )
        assert response.status_code == 200
        assert response.json()["milk_name"] == "Updated Milk"
        assert response.json()["volume_ml"] == 500
        assert response.json()["description"] == "Updated description"

    def test_update_milk_type_not_found(self, client):
        response = client.put(
            "/milk-types/9999",
            json={
                "milk_name": "Ghost",
                "volume_ml": 250
            }
        )
        assert response.status_code == 404

    def test_update_milk_type_duplicate_name(
        self, client, db_session
    ):
        from app.models.milk_type import MilkType
        m1 = MilkType(
            milk_name="Milk A",
            volume_ml=250,
            is_active=True
        )
        m2 = MilkType(
            milk_name="Milk B",
            volume_ml=500,
            is_active=True
        )
        db_session.add_all([m1, m2])
        db_session.commit()
        db_session.refresh(m1)

        response = client.put(
            f"/milk-types/{m1.id}",
            json={
                "milk_name": "Milk B",
                "volume_ml": 250
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_milk_type_keep_same_name(
        self, client, seed_milk_type
    ):
        response = client.put(
            f"/milk-types/{seed_milk_type.id}",
            json={
                "milk_name": "Full Cream Milk",
                "volume_ml": 2000,
                "description": "Updated description"
            }
        )
        assert response.status_code == 200
        assert response.json()["volume_ml"] == 2000


class TestDeleteMilkType:

    def test_delete_milk_type_success(
        self, client, seed_milk_type
    ):
        response = client.delete(
            f"/milk-types/{seed_milk_type.id}"
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        get_response = client.get(
            f"/milk-types/{seed_milk_type.id}"
        )
        assert get_response.status_code == 404

    def test_delete_milk_type_not_found(self, client):
        response = client.delete("/milk-types/9999")
        assert response.status_code == 404

    def test_delete_milk_type_soft_delete_only(
        self, client, seed_milk_type, db_session
    ):
        response = client.delete(
            f"/milk-types/{seed_milk_type.id}"
        )
        assert response.status_code == 200

        from app.models.milk_type import MilkType
        db_session.expire_all()
        milk_type = db_session.query(MilkType).filter(
            MilkType.id == seed_milk_type.id
        ).first()
        assert milk_type is not None
        assert milk_type.is_active is False
