import pytest

from src.main.api.config import USER_PASSWORD
from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestUsers:
    def test_admin_can_create_regular_user(self, admin_client, username):

        response = admin_client.create_user(
            username=username,
            password=USER_PASSWORD,
            role=UserRole.USER.value,
        )

        created_user = response.json()
        assert response.status_code == 200, response.text
        assert response.json()["username"] == username
        assert response.json()["role"] == UserRole.USER.value
        assert created_user["id"] > 0

    @pytest.mark.parametrize(
        "username,password",
        [
            ("абв", USER_PASSWORD),
            ("ab", USER_PASSWORD),
            ("user!", USER_PASSWORD),
            ("ValidUser", "short"),
            ("ValidUser", "password"),
        ],
    )
    def test_admin_cannot_create_user_with_invalid_data(
        self,
        admin_client,
        username,
        password,
    ):
        response = admin_client.create_user(
            username=username,
            password=password,
            role=UserRole.USER.value,
        )

        assert response.status_code == 400, response.text