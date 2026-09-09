import pytest

from src.main.api.config import ADMIN_PASSWORD, ADMIN_USERNAME
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import UserRole
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestAuthentication:
    def test_admin_can_login(self, api_manager):
        login = api_manager.user_steps.login(ADMIN_USERNAME, ADMIN_PASSWORD)

        assert login.token
        assert login.user.username == ADMIN_USERNAME
        assert login.user.role == UserRole.ADMIN

    def test_login_with_invalid_password(self, api_manager):
        api_manager.user_steps.raw(Endpoint.AUTH_LOGIN, ResponseSpecs.status(401)).post({
            "username": ADMIN_USERNAME, "password": "wrong-password",
        })
