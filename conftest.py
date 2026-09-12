import pytest


def pytest_addoption(parser):
    parser.addoption("--db", action="store_true", help="Запустить API-проверки с PostgreSQL")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--db"):
        marker = pytest.mark.skip(reason="Проверка PostgreSQL включается флагом --db")
        for item in items:
            if item.get_closest_marker("db"):
                item.add_marker(marker)
