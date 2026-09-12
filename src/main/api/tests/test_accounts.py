import allure

import pytest

from src.main.api.fixtures.bank_fixture import AccountContext
from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.classes.api_manager import ApiManager
from src.main.api.steps.user_steps import UserSteps
from src.main.api.models.requests import CreateUserRequest


@allure.epic("Bank API")
@allure.feature("Счета")
@allure.parent_suite("API-тесты")
@allure.suite("Счета")
@pytest.mark.api
class TestAccounts:
    @allure.title("Пользователь создаёт счёт с нулевым балансом")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_create_account(self, regular_user: UserSteps) -> None:
        account = regular_user.create_account()

        with allure.step("Проверить результат операции"):
            assert account.id > 0
            assert account.balance == 0

    @allure.title("Создание счёта по логину и паролю")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_create_account_with_credentials(
        self, api_manager: ApiManager, create_user_request: CreateUserRequest,
    ) -> None:
        account = api_manager.user_steps.create_account(create_user_request)
        user = api_manager.login_user(create_user_request.username, create_user_request.password)

        with allure.step("Проверить результат операции"):
            assert account.id > 0
            assert account.balance == 0
            assert user.get_account(account.id).id == account.id

    @allure.title("Пополнение увеличивает баланс счёта")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_deposit_money(
        self, regular_account: AccountContext, bank_data: BankTestData,
    ) -> None:
        deposit = regular_account.user.deposit(regular_account.account.id, bank_data.deposit_amount)

        with allure.step("Проверить результат операции"):
            assert deposit.id == regular_account.account.id
            assert deposit.balance == bank_data.deposit_amount
            assert regular_account.user.get_account(regular_account.account.id).balance == bank_data.deposit_amount
