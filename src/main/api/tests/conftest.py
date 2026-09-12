import uuid
from collections.abc import Callable
from src.main.api.classes.api_manager import ApiManager
from src.main.api.steps.user_steps import UserSteps
from src.main.api.fixtures.bank_fixture import (  # noqa: F401
    credit_context, deposit_context, repayment_context, transfer_context,
    regular_user, regular_account, credit_account, api_transfer_context, api_repayment_context,
)

import pytest

from src.main.api.fixtures.db_fixture import (  # noqa: F401
    bank_db, bank_db_steps, db_engine, db_session, user_db,
)

from src.main.api.fixtures.admin_fixture import admin_api, admin_steps  # noqa: F401
from src.main.api.fixtures.api_fixture import api_manager  # noqa: F401
from src.main.api.fixtures.object_fixture import created_obj  # noqa: F401
from src.main.api.fixtures.user_fixture import create_user_request  # noqa: F401
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.generators.bank_data_generator import BankDataGenerator, BankTestData
from src.main.api.reporting import attach_json
from dataclasses import asdict
from src.main.api.models.requests import CreateUserRequest, UserRole


@pytest.fixture
def bank_data() -> BankTestData:
    data = BankDataGenerator.generate()
    attach_json("Данные банковского сценария", asdict(data))
    return data


@pytest.fixture
def username() -> str:
    return f"U{uuid.uuid4().hex[:14]}"


@pytest.fixture
def make_user(admin_api: ApiManager, created_obj: list[int]) -> Callable[[UserRole], UserSteps]:
    def _make_user(role: UserRole) -> UserSteps:
        name = f"U{uuid.uuid4().hex[:14]}"
        request = RandomModelGenerator.generate(CreateUserRequest, username=name, role=role)
        user = admin_api.admin_steps.create_user(request)
        return admin_api.login_user(user.username, request.password)
    return _make_user
