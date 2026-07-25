import pytest
from decimal import Decimal


class TestCreateTokenIdentity:

    def test_create_token_identity_success(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        identity_data = {
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "token_number": 2001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == seed_customer.id
        assert data["milk_type_id"] == seed_milk_type.id
        assert data["token_number"] == 2001
        assert data["is_active"] is True

    def test_create_token_identity_duplicate(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        identity_data = {
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "token_number": 1001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 400

    def test_create_token_identity_different_token_number(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        identity_data = {
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "token_number": 3001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 201

    def test_create_token_identity_inactive_customer(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        seed_customer.is_active = False
        db_session.commit()

        identity_data = {
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "token_number": 4001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 404

    def test_create_token_identity_inactive_milk_type(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        seed_milk_type.is_active = False
        db_session.commit()

        identity_data = {
            "customer_id": seed_customer.id,
            "milk_type_id": seed_milk_type.id,
            "token_number": 5001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 404

    def test_create_token_identity_nonexistent_customer(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        identity_data = {
            "customer_id": 99999,
            "milk_type_id": 1,
            "token_number": 6001
        }

        response = client.post(
            "/token-books/identities/",
            json=identity_data
        )

        assert response.status_code == 404

    def test_create_token_identity_missing_fields(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.post(
            "/token-books/identities/",
            json={"customer_id": 1}
        )

        assert response.status_code == 422


class TestGetTokenIdentities:

    def test_get_all_identities(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.get("/token-books/identities/")

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_identity_by_id(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.get(
            f"/token-books/identities/{seed_token_identity.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_token_identity.id
        assert data["token_number"] == 1001
        assert "customer" in data
        assert "milk_type" in data

    def test_get_identity_not_found(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.get("/token-books/identities/99999")

        assert response.status_code == 404

    def test_get_identities_by_customer(
        self,
        client,
        db_session,
        seed_customer,
        seed_token_identity
    ):
        response = client.get(
            f"/token-books/identities/customer/{seed_customer.id}"
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_identities_by_customer_not_found(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.get("/token-books/identities/customer/99999")

        assert response.status_code == 404


class TestUpdateTokenIdentity:

    def test_update_token_number(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.put(
            f"/token-books/identities/{seed_token_identity.id}",
            json={"token_number": 9999}
        )

        assert response.status_code == 200
        assert response.json()["token_number"] == 9999

    def test_update_not_found(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.put(
            "/token-books/identities/99999",
            json={"token_number": 1234}
        )

        assert response.status_code == 404

    def test_update_duplicate_token_number(
        self,
        client,
        db_session,
        seed_customer,
        seed_milk_type,
        seed_token_identity
    ):
        from app.models.token_identity import TokenIdentity

        second = TokenIdentity(
            customer_id=seed_customer.id,
            milk_type_id=seed_milk_type.id,
            token_number=5555,
            is_active=True
        )
        db_session.add(second)
        db_session.commit()
        db_session.refresh(second)

        response = client.put(
            f"/token-books/identities/{second.id}",
            json={"token_number": 1001}
        )

        assert response.status_code == 400


class TestDeleteTokenIdentity:

    def test_delete_identity_success(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.delete(
            f"/token-books/identities/{seed_token_identity.id}"
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_identity_not_found(
        self,
        client,
        db_session,
        seed_token_identity
    ):
        response = client.delete("/token-books/identities/99999")

        assert response.status_code == 404


class TestCreateTokenBookIssue:

    def test_create_book_issue_success(
        self,
        client,
        db_session,
        seed_token_identity,
        seed_token_book_issue
    ):
        issue_data = {
            "token_identity_id": seed_token_identity.id,
            "issue_number": 2,
            "remarks": "Second book"
        }

        response = client.post(
            "/token-books/issues/",
            json=issue_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["issue_number"] == 2
        assert data["status"] == "WAITING"
        assert data["current_sheet"] == 0

    def test_create_book_issue_active_exists(
        self,
        client,
        db_session,
        seed_token_identity,
        seed_token_book_issue
    ):
        seed_token_book_issue.status = "ACTIVE"
        db_session.commit()

        issue_data = {
            "token_identity_id": seed_token_identity.id,
            "issue_number": 3
        }

        response = client.post(
            "/token-books/issues/",
            json=issue_data
        )

        assert response.status_code == 400

    def test_create_book_issue_duplicate_number(
        self,
        client,
        db_session,
        seed_token_identity,
        seed_token_book_issue
    ):
        issue_data = {
            "token_identity_id": seed_token_identity.id,
            "issue_number": 1
        }

        response = client.post(
            "/token-books/issues/",
            json=issue_data
        )

        assert response.status_code == 400

    def test_create_book_issue_inactive_identity(
        self,
        client,
        db_session,
        seed_token_identity,
        seed_token_book_issue
    ):
        seed_token_identity.is_active = False
        db_session.commit()

        issue_data = {
            "token_identity_id": seed_token_identity.id,
            "issue_number": 4
        }

        response = client.post(
            "/token-books/issues/",
            json=issue_data
        )

        assert response.status_code == 404

    def test_create_book_issue_nonexistent_identity(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        issue_data = {
            "token_identity_id": 99999,
            "issue_number": 5
        }

        response = client.post(
            "/token-books/issues/",
            json=issue_data
        )

        assert response.status_code == 404


class TestGetTokenBookIssues:

    def test_get_all_book_issues(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.get("/token-books/issues/")

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_book_issue_by_id(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.get(
            f"/token-books/issues/{seed_token_book_issue.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_token_book_issue.id
        assert data["issue_number"] == 1
        assert "token_identity" in data

    def test_get_book_issue_not_found(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.get("/token-books/issues/99999")

        assert response.status_code == 404

    def test_get_book_issues_by_identity(
        self,
        client,
        db_session,
        seed_token_identity,
        seed_token_book_issue
    ):
        response = client.get(
            f"/token-books/issues/identity/{seed_token_identity.id}"
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_book_issues_by_identity_not_found(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.get("/token-books/issues/identity/99999")

        assert response.status_code == 404


class TestUpdateTokenBookIssue:

    def test_update_issue_status(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.put(
            f"/token-books/issues/{seed_token_book_issue.id}",
            json={"status": "ACTIVE"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ACTIVE"

    def test_update_issue_current_sheet(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.put(
            f"/token-books/issues/{seed_token_book_issue.id}",
            json={"current_sheet": 5}
        )

        assert response.status_code == 200
        assert response.json()["current_sheet"] == 5

    def test_update_issue_not_found(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.put(
            "/token-books/issues/99999",
            json={"status": "ACTIVE"}
        )

        assert response.status_code == 404


class TestDeleteTokenBookIssue:

    def test_delete_issue_success(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.delete(
            f"/token-books/issues/{seed_token_book_issue.id}"
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_issue_not_found(
        self,
        client,
        db_session,
        seed_token_book_issue
    ):
        response = client.delete("/token-books/issues/99999")

        assert response.status_code == 404


class TestCreateTokenBookPayment:

    def test_create_payment_prepaid_full(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        from app.models.token_book_issue import TokenBookIssue

        issue2 = TokenBookIssue(
            token_identity_id=seed_token_book_issue.token_identity_id,
            issue_number=10,
            status="WAITING",
            is_active=True
        )
        db_session.add(issue2)
        db_session.commit()
        db_session.refresh(issue2)

        payment_data = {
            "token_book_issue_id": issue2.id,
            "payment_mode": "PREPAID",
            "book_price": 500.00,
            "amount_paid": 500.00
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_mode"] == "PREPAID"
        assert data["payment_status"] == "PAID"
        assert float(data["balance_amount"]) == 0.0

    def test_create_payment_partial(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        from app.models.token_book_issue import TokenBookIssue

        issue2 = TokenBookIssue(
            token_identity_id=seed_token_book_issue.token_identity_id,
            issue_number=11,
            status="WAITING",
            is_active=True
        )
        db_session.add(issue2)
        db_session.commit()
        db_session.refresh(issue2)

        payment_data = {
            "token_book_issue_id": issue2.id,
            "payment_mode": "POSTPAID",
            "book_price": 500.00,
            "amount_paid": 200.00
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_status"] == "PARTIAL"
        assert float(data["balance_amount"]) == 300.0

    def test_create_payment_pending(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        from app.models.token_book_issue import TokenBookIssue

        issue2 = TokenBookIssue(
            token_identity_id=seed_token_book_issue.token_identity_id,
            issue_number=12,
            status="WAITING",
            is_active=True
        )
        db_session.add(issue2)
        db_session.commit()
        db_session.refresh(issue2)

        payment_data = {
            "token_book_issue_id": issue2.id,
            "payment_mode": "POSTPAID",
            "book_price": 500.00,
            "amount_paid": 0
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_status"] == "PENDING"
        assert float(data["balance_amount"]) == 500.0

    def test_create_payment_amount_exceeds_price(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        from app.models.token_book_issue import TokenBookIssue

        issue2 = TokenBookIssue(
            token_identity_id=seed_token_book_issue.token_identity_id,
            issue_number=13,
            status="WAITING",
            is_active=True
        )
        db_session.add(issue2)
        db_session.commit()
        db_session.refresh(issue2)

        payment_data = {
            "token_book_issue_id": issue2.id,
            "payment_mode": "PREPAID",
            "book_price": 500.00,
            "amount_paid": 600.00
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 400

    def test_create_payment_inactive_issue(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        seed_token_book_issue.is_active = False
        db_session.commit()

        payment_data = {
            "token_book_issue_id": seed_token_book_issue.id,
            "payment_mode": "PREPAID",
            "book_price": 500.00,
            "amount_paid": 500.00
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 404

    def test_create_payment_nonexistent_issue(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        payment_data = {
            "token_book_issue_id": 99999,
            "payment_mode": "PREPAID",
            "book_price": 500.00,
            "amount_paid": 500.00
        }

        response = client.post(
            "/token-books/payments/",
            json=payment_data
        )

        assert response.status_code == 404


class TestGetTokenBookPayments:

    def test_get_all_payments(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.get("/token-books/payments/")

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_payment_by_id(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.get(
            f"/token-books/payments/{seed_token_book_payment.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == seed_token_book_payment.id
        assert data["payment_mode"] == "PREPAID"
        assert "token_book_issue" in data

    def test_get_payment_not_found(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.get("/token-books/payments/99999")

        assert response.status_code == 404

    def test_get_payments_by_issue(
        self,
        client,
        db_session,
        seed_token_book_issue,
        seed_token_book_payment
    ):
        response = client.get(
            f"/token-books/payments/issue/{seed_token_book_issue.id}"
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_payments_by_issue_not_found(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.get("/token-books/payments/issue/99999")

        assert response.status_code == 404


class TestUpdateTokenBookPayment:

    def test_update_payment_amount(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.put(
            f"/token-books/payments/{seed_token_book_payment.id}",
            json={"amount_paid": 300.00}
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["amount_paid"]) == 300.0
        assert float(data["balance_amount"]) == 200.0
        assert data["payment_status"] == "PARTIAL"

    def test_update_payment_not_found(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.put(
            "/token-books/payments/99999",
            json={"amount_paid": 100.00}
        )

        assert response.status_code == 404

    def test_update_payment_auto_status_change(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.put(
            f"/token-books/payments/{seed_token_book_payment.id}",
            json={"amount_paid": 0}
        )

        assert response.status_code == 200
        assert response.json()["payment_status"] == "PENDING"


class TestDeleteTokenBookPayment:

    def test_delete_payment_success(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.delete(
            f"/token-books/payments/{seed_token_book_payment.id}"
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_delete_payment_not_found(
        self,
        client,
        db_session,
        seed_token_book_payment
    ):
        response = client.delete("/token-books/payments/99999")

        assert response.status_code == 404
