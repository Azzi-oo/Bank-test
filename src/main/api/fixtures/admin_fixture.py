import pytest

from src.main.api.config import ADMIN_PASSWORD, ADMIN_USERNAME


@pytest.fixture
def admin_api(api_manager):
    api_manager.login_admin(ADMIN_USERNAME, ADMIN_PASSWORD)
    return api_manager


@pytest.fixture
def admin_steps(admin_api, created_obj):
    return admin_api.admin_steps
