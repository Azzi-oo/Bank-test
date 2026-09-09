import pytest

from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.requests import CreateUserRequest


@pytest.fixture
def create_user_request(admin_steps, username):
    """Создаёт пользователя с уникальным именем и возвращает данные для входа."""
    user_request = RandomModelGenerator.generate(CreateUserRequest, username=username)
    admin_steps.create_user(user_request)
    return user_request
