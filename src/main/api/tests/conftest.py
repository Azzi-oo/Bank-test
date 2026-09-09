import uuid

import pytest

from src.main.api.config import USER_PASSWORD
from src.main.api.fixtures.admin_fixture import admin_api, admin_steps  # noqa: F401
from src.main.api.fixtures.api_fixture import api_manager  # noqa: F401
from src.main.api.fixtures.object_fixture import created_obj  # noqa: F401
from src.main.api.models.requests import CreateUserRequest, UserRole


@pytest.fixture
def username():
    return f"U{uuid.uuid4().hex[:14]}"


@pytest.fixture
def make_user(admin_api, created_obj):
    def _make_user(role: UserRole):
        name = f"U{uuid.uuid4().hex[:14]}"
        user = admin_api.admin_steps.create_user(CreateUserRequest(
            username=name, password=USER_PASSWORD, role=role,
        ))
        return admin_api.login_user(user.username, USER_PASSWORD)
    return _make_user
