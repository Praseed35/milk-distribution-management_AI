class TestCreateEmployee:

    def test_create_employee_success(
        self, client, seed_route, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Ram Kumar",
                "phone": "9876543210",
                "address": "123 Main St",
                "role": "DELIVERY_PARTNER",
                "route_id": seed_route.id
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Ram Kumar"
        assert data["phone"] == "9876543210"
        assert data["role"] == "DELIVERY_PARTNER"
        assert data["route_id"] == seed_route.id
        assert data["is_active"] is True
        assert data["employee_code"].startswith("E")
        assert data["username"] is None

    def test_create_employee_auto_code(
        self, client, seed_route, auth_headers
    ):
        for i in range(3):
            response = client.post(
                "/employees/",
                json={
                    "name": f"Employee {i}",
                    "phone": f"9876543{200 + i:04d}",
                    "role": "DELIVERY_PARTNER",
                    "route_id": seed_route.id
                },
                headers=auth_headers
            )
            assert response.status_code == 201

        response = client.get("/employees/")
        codes = [e["employee_code"] for e in response.json()]
        assert len(codes) == 3
        assert len(set(codes)) == 3

    def test_create_employee_route_not_found(
        self, client, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "No Route",
                "phone": "9876543300",
                "role": "DELIVERY_PARTNER",
                "route_id": 9999
            },
            headers=auth_headers
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."

    def test_create_employee_inactive_route(
        self, client, db_session, auth_headers
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
            "/employees/",
            json={
                "name": "Bad Route Employee",
                "phone": "9876543400",
                "role": "DELIVERY_PARTNER",
                "route_id": route.id
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "inactive" in response.json()["detail"].lower()

    def test_create_employee_duplicate_phone(
        self, client, seed_route, db_session, auth_headers
    ):
        from app.models.employee import Employee
        existing = Employee(
            employee_code="E00001",
            name="Existing",
            phone="9876543500",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(existing)
        db_session.commit()

        response = client.post(
            "/employees/",
            json={
                "name": "Duplicate Phone",
                "phone": "9876543500",
                "role": "DELIVERY_PARTNER",
                "route_id": seed_route.id
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_employee_missing_fields(
        self, client, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Incomplete"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_employee_without_route(
        self, client, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "No Route Employee",
                "phone": "9876543600",
                "role": "CHECKER"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["route_id"] is None

    def test_create_employee_without_auth(self, client):
        response = client.post(
            "/employees/",
            json={
                "name": "No Auth Employee",
                "phone": "9876543601",
                "role": "CHECKER"
            }
        )
        assert response.status_code == 401

    def test_create_employee_forbidden_for_checker(
        self, client, employee_auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Checker Creates",
                "phone": "9876543602",
                "role": "CHECKER"
            },
            headers=employee_auth_headers
        )
        assert response.status_code == 403


class TestCreateEmployeeWithCredentials:

    def test_create_employee_with_credentials(
        self, client, seed_route, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Cred Employee",
                "phone": "9876545000",
                "role": "CHECKER",
                "route_id": seed_route.id,
                "username": "checker_rahul",
                "password": "rahul123",
                "confirm_password": "rahul123"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cred Employee"
        assert data["username"] == "checker_rahul"

        login_response = client.post(
            "/auth/login",
            json={
                "username": "checker_rahul",
                "password": "rahul123"
            }
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_create_employee_credentials_mismatch(
        self, client, seed_route, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Bad Cred",
                "phone": "9876545001",
                "role": "CHECKER",
                "username": "bad_creds",
                "password": "pass123",
                "confirm_password": "different123"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_employee_partial_credentials(
        self, client, seed_route, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "Partial Cred",
                "phone": "9876545002",
                "role": "CHECKER",
                "username": "partial_user"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_employee_duplicate_username(
        self, client, seed_route, auth_headers
    ):
        client.post(
            "/employees/",
            json={
                "name": "First Employee",
                "phone": "9876545003",
                "role": "CHECKER",
                "username": "dup_user",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )

        response = client.post(
            "/employees/",
            json={
                "name": "Second Employee",
                "phone": "9876545004",
                "role": "CHECKER",
                "username": "dup_user",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_employee_without_credentials(
        self, client, seed_route, auth_headers
    ):
        response = client.post(
            "/employees/",
            json={
                "name": "No Cred Employee",
                "phone": "9876545005",
                "role": "CHECKER"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] is None


class TestUpdateEmployeeCredentials:

    def test_update_credentials_success(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Cred Update",
                "phone": "9876545100",
                "role": "DELIVERY_PARTNER",
                "username": "delivery_old",
                "password": "oldpass123",
                "confirm_password": "oldpass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "username": "delivery_new",
                "password": "newpass123",
                "confirm_password": "newpass123"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "delivery_new"

        login_old = client.post(
            "/auth/login",
            json={
                "username": "delivery_old",
                "password": "oldpass123"
            }
        )
        assert login_old.status_code == 401

        login_new = client.post(
            "/auth/login",
            json={
                "username": "delivery_new",
                "password": "newpass123"
            }
        )
        assert login_new.status_code == 200

    def test_update_credentials_password_only(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Password Only",
                "phone": "9876545101",
                "role": "CHECKER",
                "username": "pass_only_user",
                "password": "oldpass123",
                "confirm_password": "oldpass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "password": "newpass456",
                "confirm_password": "newpass456"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "pass_only_user"

        login_new = client.post(
            "/auth/login",
            json={
                "username": "pass_only_user",
                "password": "newpass456"
            }
        )
        assert login_new.status_code == 200

    def test_update_credentials_username_only(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Username Only",
                "phone": "9876545102",
                "role": "CHECKER",
                "username": "old_username",
                "password": "samepass123",
                "confirm_password": "samepass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "username": "new_username"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "new_username"

        login_new = client.post(
            "/auth/login",
            json={
                "username": "new_username",
                "password": "samepass123"
            }
        )
        assert login_new.status_code == 200

    def test_update_credentials_employee_not_found(
        self, client, auth_headers
    ):
        response = client.put(
            "/employees/9999/credentials",
            json={
                "username": "ghost_user",
                "password": "ghost123",
                "confirm_password": "ghost123"
            },
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_credentials_no_linked_user(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "No User Emp",
                "phone": "9876545103",
                "role": "CHECKER"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "username": "new_user",
                "password": "newpass123",
                "confirm_password": "newpass123"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "no linked user" in response.json()["detail"].lower()

    def test_update_credentials_password_mismatch(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Mismatch Cred",
                "phone": "9876545104",
                "role": "CHECKER",
                "username": "mismatch_user",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "password": "newpass",
                "confirm_password": "different"
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_update_credentials_duplicate_username(
        self, client, seed_route, auth_headers
    ):
        client.post(
            "/employees/",
            json={
                "name": "Existing User",
                "phone": "9876545105",
                "role": "CHECKER",
                "username": "taken_username",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )

        create_response = client.post(
            "/employees/",
            json={
                "name": "Try Rename",
                "phone": "9876545106",
                "role": "CHECKER",
                "username": "my_own_name",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={
                "username": "taken_username"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_credentials_empty_body(
        self, client, seed_route, auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Empty Body",
                "phone": "9876545107",
                "role": "CHECKER",
                "username": "empty_body_user",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=auth_headers
        )
        emp_id = create_response.json()["id"]

        response = client.put(
            f"/employees/{emp_id}/credentials",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_update_credentials_forbidden_for_checker(
        self, client, seed_route, employee_auth_headers
    ):
        create_response = client.post(
            "/employees/",
            json={
                "name": "Protected Cred",
                "phone": "9876545108",
                "role": "CHECKER",
                "username": "protected_user",
                "password": "pass123",
                "confirm_password": "pass123"
            },
            headers=employee_auth_headers
        )

        if create_response.status_code == 201:
            emp_id = create_response.json()["id"]
            response = client.put(
                f"/employees/{emp_id}/credentials",
                json={
                    "username": "hacked_user"
                },
                headers=employee_auth_headers
            )
            assert response.status_code == 403


class TestGetEmployees:

    def test_get_employees_empty(self, client):
        response = client.get("/employees/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_employees_with_data(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee
        emp = Employee(
            employee_code="E00001",
            name="Test Employee",
            phone="9876543700",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()

        response = client.get("/employees/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Test Employee"

    def test_get_employee_by_id(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee
        emp = Employee(
            employee_code="E00002",
            name="ByID Employee",
            phone="9876543800",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.get(f"/employees/{emp.id}")
        assert response.status_code == 200
        assert response.json()["employee_code"] == "E00002"

    def test_get_employee_not_found(self, client):
        response = client.get("/employees/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Employee not found."

    def test_get_employee_excludes_inactive(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee
        active = Employee(
            employee_code="E00003",
            name="Active",
            phone="9876543900",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        inactive = Employee(
            employee_code="E00004",
            name="Inactive",
            phone="9876543901",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=False
        )
        db_session.add_all([active, inactive])
        db_session.commit()

        response = client.get("/employees/")
        assert len(response.json()) == 1


class TestUpdateEmployee:

    def test_update_employee_success(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee
        emp = Employee(
            employee_code="E00005",
            name="Update Me",
            phone="9876544000",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.put(
            f"/employees/{emp.id}",
            json={
                "name": "Updated Name",
                "phone": "9876544000",
                "role": "CHECKER",
                "route_id": seed_route.id
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["role"] == "CHECKER"

    def test_update_employee_not_found(self, client, seed_route):
        response = client.put(
            "/employees/9999",
            json={
                "name": "Ghost",
                "phone": "9876544100",
                "role": "DELIVERY_PARTNER"
            }
        )
        assert response.status_code == 404

    def test_update_employee_route_not_found(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee
        emp = Employee(
            employee_code="E00006",
            name="Bad Route Update",
            phone="9876544200",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.put(
            f"/employees/{emp.id}",
            json={
                "name": "Updated",
                "phone": "9876544200",
                "role": "DELIVERY_PARTNER",
                "route_id": 9999
            }
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Route not found."

    def test_update_employee_inactive_route(
        self, client, seed_route, db_session
    ):
        from app.models.route import Route
        from app.models.employee import Employee

        route = Route(
            route_code="R_INACT",
            route_name="Inactive Route",
            is_active=False
        )
        db_session.add(route)
        db_session.commit()
        db_session.refresh(route)

        emp = Employee(
            employee_code="E00007",
            name="Inactive Route Update",
            phone="9876544300",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.put(
            f"/employees/{emp.id}",
            json={
                "name": "Updated",
                "phone": "9876544300",
                "role": "DELIVERY_PARTNER",
                "route_id": route.id
            }
        )
        assert response.status_code == 400

    def test_update_employee_duplicate_phone(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee

        e1 = Employee(
            employee_code="E00008",
            name="First",
            phone="9876544400",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        e2 = Employee(
            employee_code="E00009",
            name="Second",
            phone="9876544500",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add_all([e1, e2])
        db_session.commit()
        db_session.refresh(e1)

        response = client.put(
            f"/employees/{e1.id}",
            json={
                "name": "First Updated",
                "phone": "9876544500",
                "role": "DELIVERY_PARTNER"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_update_employee_partial(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee

        emp = Employee(
            employee_code="E00010",
            name="Partial Update",
            phone="9876544600",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.put(
            f"/employees/{emp.id}",
            json={
                "name": "Only Name Changed"
            }
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Only Name Changed"
        assert response.json()["phone"] == "9876544600"


class TestDeleteEmployee:

    def test_delete_employee_success(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee

        emp = Employee(
            employee_code="E00011",
            name="Delete Me",
            phone="9876544700",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.delete(f"/employees/{emp.id}")
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        get_response = client.get(f"/employees/{emp.id}")
        assert get_response.status_code == 404

    def test_delete_employee_not_found(self, client):
        response = client.delete("/employees/9999")
        assert response.status_code == 404

    def test_delete_employee_soft_delete_only(
        self, client, seed_route, db_session
    ):
        from app.models.employee import Employee

        emp = Employee(
            employee_code="E00012",
            name="Soft Delete Check",
            phone="9876544800",
            role="DELIVERY_PARTNER",
            route_id=seed_route.id,
            is_active=True
        )
        db_session.add(emp)
        db_session.commit()
        db_session.refresh(emp)

        response = client.delete(f"/employees/{emp.id}")
        assert response.status_code == 200

        db_session.expire_all()
        employee = db_session.query(Employee).filter(
            Employee.id == emp.id
        ).first()
        assert employee is not None
        assert employee.is_active is False
