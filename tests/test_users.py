class TestGetUsers:

    def test_get_users_empty(self, client):
        response = client.get("/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_users_returns_list(self, client, seed_user):
        response = client.get("/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["username"] == "testadmin"


class TestCreateUser:

    def test_create_user_success(self, client):
        response = client.post(
            "/users/",
            json={
                "username": "newuser",
                "password": "pass123",
                "role": "EMPLOYEE"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "EMPLOYEE"
        assert "id" in data

    def test_create_duplicate_user(self, client, seed_user):
        response = client.post(
            "/users/",
            json={
                "username": "testadmin",
                "password": "pass123",
                "role": "EMPLOYEE"
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"

    def test_create_user_missing_fields(self, client):
        response = client.post(
            "/users/",
            json={
                "username": "incomplete"
            }
        )
        assert response.status_code == 422

    def test_create_multiple_users(self, client):
        for i in range(3):
            response = client.post(
                "/users/",
                json={
                    "username": f"user{i}",
                    "password": f"pass{i}",
                    "role": "EMPLOYEE"
                }
            )
            assert response.status_code == 200

        response = client.get("/users/")
        assert len(response.json()) == 3
