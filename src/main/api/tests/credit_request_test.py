import pytest
import requests


@pytest.mark.api
class TestCreditRequest:
    def test_credit_request(self, username):
        admin_login = requests.post(
            "http://localhost:4111/api/auth/token/login",
            json={"username": "admin", "password": "123456"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["token"]

        create_user = requests.post(
            "http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_CREDIT_SECRET",
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}",
            },
        )
        assert create_user.status_code == 200

        user_login = requests.post(
            "http://localhost:4111/api/auth/token/login",
            json={"username": username, "password": "Pas!sw0rd"},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        assert user_login.status_code == 200

        user_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {user_login.json()['token']}",
        }

        create_account = requests.post(
            "http://localhost:4111/api/account/create",
            headers=user_headers,
        )
        assert create_account.status_code == 201
        account_id = create_account.json()["id"]

        credit_request = requests.post(
            "http://localhost:4111/api/credit/request",
            json={
                "accountId": account_id,
                "amount": 5000,
                "termMonths": 12,
            },
            headers=user_headers,
        )
        assert credit_request.status_code == 201
