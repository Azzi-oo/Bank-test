import pytest

from src.main.api.clients.auth_client import AuthClient
from src.main.api.config import ADMIN_PASSWORD, ADMIN_USERNAME, BASE_URL


@pytest.mark.api
class TestAuthentication:
    def test_admin_can_login(self):
        response = AuthClient(BASE_URL).login(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
        )

        assert response.status_code == 200, response.text
        assert response.json()["token"]
        assert response.json()["user"]["username"] == ADMIN_USERNAME
        assert response.json()["user"]["role"] == "ROLE_ADMIN"

    def test_login_with_invalid_password(self):
        response = AuthClient(BASE_URL).login(
            username=ADMIN_USERNAME,
            password="wrong-password",
        )

        assert response.status_code == 401, response.text