from src.main.api.classes.api_manager import ApiManager
from src.main.api.steps.admin_steps import AdminSteps
import pytest

from src.main.api.config import ADMIN_PASSWORD, ADMIN_USERNAME


@pytest.fixture
def admin_api(api_manager: ApiManager) -> ApiManager:
    api_manager.login_admin(ADMIN_USERNAME, ADMIN_PASSWORD)
    return api_manager


@pytest.fixture
def admin_steps(admin_api: ApiManager, created_obj: list[int]) -> AdminSteps:
    return admin_api.admin_steps
