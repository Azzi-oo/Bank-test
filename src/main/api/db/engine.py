import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def database_url() -> str:
    """Переменная окружения приоритетнее локального файла настроек."""
    if value := os.getenv("BANK_DATABASE_URL"):
        return value
    path = Path(__file__).resolve().parents[4] / "resources" / "urls.properties"
    if path.exists():
        for line in path.read_text().splitlines():
            key, separator, value = line.strip().partition("=")
            if separator and key.strip() == "dataBaseUrl":
                return value.strip()
    raise ValueError("Задайте BANK_DATABASE_URL или dataBaseUrl в resources/urls.properties")


def create_db_engine(url: str | None = None) -> Engine:
    return create_engine(
        url or database_url(), pool_pre_ping=True, echo=False, hide_parameters=True,
        connect_args={"connect_timeout": 5},
        isolation_level="READ COMMITTED",
    )
