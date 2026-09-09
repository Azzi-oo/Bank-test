import pytest

from src.main.api.config import USER_PASSWORD
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import CreateUserRequest, UserRole
from src.main.api.specs.response_specs import ResponseSpecs


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
        self, admin_steps, created_obj, username, invalid_username, password,
    ):
        # Dictionaries deliberately bypass local request validation in negative tests.
        response = admin_steps.raw(Endpoint.ADMIN_CREATE_USER).post({
            "username": invalid_username if invalid_username is not None else username,
            "password": password,
            "role": UserRole.USER.value,
        })
        if response.status_code == 200:
            created_obj.append(response.json()["id"])
        ResponseSpecs.request_bad()(response)
