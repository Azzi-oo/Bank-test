from collections.abc import Iterator
import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.fixture
def api_manager() -> Iterator[ApiManager]:
    manager = ApiManager()
    try:
        yield manager
    finally:
        manager.close()
