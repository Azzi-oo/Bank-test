import pytest

from src.main.api.config import USER_PASSWORD
from src.main.api.models.requests import CreateUserRequest, LoginRequest, UserRole


@pytest.mark.api
class TestUsers:
    def test_admin_can_create_regular_user(self, admin_steps, username):
        user = admin_steps.create_user(CreateUserRequest(
            username=username, password=USER_PASSWORD, role=UserRole.USER,
        ))

        assert user.username == username
        assert user.role == UserRole.USER
        assert user.id > 0

    @pytest.mark.parametrize(
        "invalid_username,password",
        [
            ("абв", USER_PASSWORD),
            ("ab", USER_PASSWORD),
            ("user!", USER_PASSWORD),
            (None, "short"),
            (None, "password"),
        ],
        ids=["non-latin-name", "short-name", "special-character", "short-password", "weak-password"],
    )
    def test_admin_cannot_create_user_with_invalid_data(
        self, admin_steps, username, invalid_username, password,
    ):
        admin_steps.create_invalid_user({
            "username": invalid_username if invalid_username is not None else username,
            "password": password,
            "role": UserRole.USER.value,
        })

    def test_created_user_can_login(self, admin_steps, create_user_request):
        login = admin_steps.login_user(LoginRequest(
            username=create_user_request.username,
            password=create_user_request.password,
        ))

        assert login.token
        assert login.user.username == create_user_request.username
        assert login.user.role == create_user_request.role
