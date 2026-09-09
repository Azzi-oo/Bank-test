import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.fixture
def api_manager():
    manager = ApiManager()
    try:
        yield manager
    finally:
        manager.close()
