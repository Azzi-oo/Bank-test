import requests
import pytest


@pytest.mark.api
class TestUserLogin:
    def test_user_login_admin(self):
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
        assert login_admin_response.json()["user"]["username"] == "admin"
        assert login_admin_response.json()["user"]["role"] == "ROLE_ADMIN"

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
        assert login_user_response.json()["user"]["username"] == username
        assert login_user_response.json()["user"]["role"] == "ROLE_USER"
        
        