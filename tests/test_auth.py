class TestLogin:

    def test_login_success(self, client, seed_user):
        response = client.post(
            "/auth/login",
            json={
                "username": "testadmin",
                "password": "admin123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, seed_user):
        response = client.post(
            "/auth/login",
            json={
                "username": "testadmin",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_nonexistent_user(self, client, seed_user):
        response = client.post(
            "/auth/login",
            json={
                "username": "nouser",
                "password": "nopass"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_missing_fields(self, client, seed_user):
        response = client.post(
            "/auth/login",
            json={
                "username": "testadmin"
            }
        )
        assert response.status_code == 422


class TestGetMe:

    def test_get_me_authenticated(self, client, auth_headers):
        response = client.get(
            "/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testadmin"
        assert data["role"] == "OWNER"

    def test_get_me_no_token(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer invalid.token.here"
            }
        )
        assert response.status_code == 401


class TestChangePassword:

    def test_change_password_success(
        self, client, auth_headers
    ):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "admin123",
                "new_password": "newadmin456",
                "confirm_password": "newadmin456"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully."

        login_old = client.post(
            "/auth/login",
            json={
                "username": "testadmin",
                "password": "admin123"
            }
        )
        assert login_old.status_code == 401

        login_new = client.post(
            "/auth/login",
            json={
                "username": "testadmin",
                "password": "newadmin456"
            }
        )
        assert login_new.status_code == 200

    def test_change_password_wrong_current(
        self, client, auth_headers
    ):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "wrongpass",
                "new_password": "newadmin789",
                "confirm_password": "newadmin789"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_mismatch_new(
        self, client, auth_headers
    ):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "admin123",
                "new_password": "newpass1",
                "confirm_password": "newpass2"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_change_password_same_as_current(
        self, client, auth_headers
    ):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "admin123",
                "new_password": "admin123",
                "confirm_password": "admin123"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_change_password_no_token(self, client):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "admin123",
                "new_password": "newpass123",
                "confirm_password": "newpass123"
            }
        )
        assert response.status_code == 401

    def test_change_password_missing_fields(
        self, client, auth_headers
    ):
        response = client.put(
            "/auth/change-password",
            json={
                "current_password": "admin123"
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestOwnerDashboard:

    def test_owner_dashboard_success(self, client, auth_headers):
        response = client.get(
            "/auth/owner-dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Welcome Owner"

    def test_owner_dashboard_forbidden_for_employee(
        self, client, employee_auth_headers
    ):
        response = client.get(
            "/auth/owner-dashboard",
            headers=employee_auth_headers
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied"

    def test_owner_dashboard_no_token(self, client):
        response = client.get("/auth/owner-dashboard")
        assert response.status_code == 401
