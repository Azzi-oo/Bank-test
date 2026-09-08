from dataclasses import dataclass
import uuid
from datetime import datetime

import pytest

from src.main.api.clients.account_client import AccountClient
from src.main.api.clients.admin_client import AdminClient
from src.main.api.clients.auth_client import AuthClient
from src.main.api.clients.credit_client import CreditClient
from src.main.api.config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    BASE_URL,
    USER_PASSWORD,
)
from src.main.api.models.requests import UserRole


@dataclass
class UserApi:
    username: str
    token: str
    accounts: AccountClient
    credits: CreditClient


def assert_status(response, expected_status: int):
    assert response.status_code == expected_status, response.text


@pytest.fixture
def admin_client():
    auth_client = AuthClient(BASE_URL)

    response = auth_client.login(
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD,
    )
    assert_status(response, 200)

    return AdminClient(BASE_URL, response.json()["token"])


@pytest.fixture
def username():
    now = datetime.now()

    return f"U{now:%d%H%M%S}{now.microsecond % 100000:05d}"


@pytest.fixture
def make_user(admin_client):
    def _make_user(role: UserRole) -> UserApi:
        username = f"User{uuid.uuid4().hex[:8]}"

        create_response = admin_client.create_user(
            username=username,
            password=USER_PASSWORD,
            role=role.value,
        )
        assert_status(create_response, 200)

        auth_client = AuthClient(BASE_URL)
        login_response = auth_client.login(
            username=username,
            password=USER_PASSWORD,
        )
        assert_status(login_response, 200)

        token = login_response.json()["token"]

        return UserApi(
            username=username,
            token=token,
            accounts=AccountClient(BASE_URL, token),
            credits=CreditClient(BASE_URL, token),
        )

    return _make_user