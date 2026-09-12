import allure

from decimal import Decimal

import pytest

from src.main.api.models.requests import UserRole


@allure.epic("Bank API")
@allure.feature("Счета")
@allure.parent_suite("API-тесты")
@allure.suite("Счета")
@pytest.mark.api
class TestAccounts:
    @allure.title("Пользователь создаёт счёт с нулевым балансом")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_create_account(self, make_user):
        user = make_user(UserRole.USER)

        account = user.create_account()

        with allure.step("Проверить результат операции"):
            assert account.id > 0
            assert account.balance == 0

    @allure.title("Создание счёта по логину и паролю")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_create_account_with_credentials(self, api_manager, create_user_request):
        account = api_manager.user_steps.create_account(create_user_request)
        user = api_manager.login_user(create_user_request.username, create_user_request.password)

        with allure.step("Проверить результат операции"):
            assert account.id > 0
            assert account.balance == 0
            assert user.get_account(account.id).id == account.id

    @allure.title("Пополнение увеличивает баланс счёта")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_deposit_money(self, make_user):
        user = make_user(UserRole.USER)
        account = user.create_account()

        deposit = user.deposit(account.id, 1000.50)

        with allure.step("Проверить результат операции"):
            assert deposit.id == account.id
            assert deposit.balance == Decimal("1000.50")
            assert user.get_account(account.id).balance == Decimal("1000.50")
