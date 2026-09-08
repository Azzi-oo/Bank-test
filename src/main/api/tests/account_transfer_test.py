import pytest
import requests


@pytest.mark.api
class TestAccountTransfer:
    def test_login_user(self, username):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                'Content-Type': 'application/json',
                "Accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200

    def test_account_transfer(self, username):
        login_admin_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": "admin",
                "password": "123456"
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        assert login_admin_response.status_code == 200
        admin_token = login_admin_response.json().get("token")

        create_user_response = requests.post(
            url="http://localhost:4111/api/admin/create",
            json={
                "username": username,
                "password": "Pas!sw0rd",
                "role": "ROLE_USER"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {admin_token}"
            }
        )

        assert create_user_response.status_code == 200

        login_user_response = requests.post(
            url="http://localhost:4111/api/auth/token/login",
            json={
                "username": username,
                "password": "Pas!sw0rd"
            },
            headers={
                "Content-Type": "application/json",
                "accept": "application/json"
            }
        )

        assert login_user_response.status_code == 200
        user_token = login_user_response.json().get("token")
        user_headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}"
        }

        from_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers=user_headers
        )
        to_account_response = requests.post(
            url="http://localhost:4111/api/account/create",
            headers=user_headers
        )

        assert from_account_response.status_code == 201
        assert to_account_response.status_code == 201
        from_account_id = from_account_response.json().get("id")
        to_account_id = to_account_response.json().get("id")

        deposit_response = requests.post(
            url="http://localhost:4111/api/account/deposit",
            json={
                "accountId": from_account_id,
                "amount": 1000.5
            },
            headers=user_headers
        )

        assert deposit_response.status_code == 200

        account_transfer_response = requests.post(
            url="http://localhost:4111/api/account/transfer",
            json={
                "fromAccountId": from_account_id,
                "toAccountId": to_account_id,
                "amount": 500.75
            },
            headers=user_headers
        )

        assert account_transfer_response.status_code == 200
        assert account_transfer_response.json().get("fromAccountId") == from_account_id
        assert account_transfer_response.json().get("toAccountId") == to_account_id
        assert account_transfer_response.json().get("fromAccountIdBalance") == 499.75
