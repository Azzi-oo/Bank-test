import allure

import pytest

from src.main.api.models.requests import UserRole


@allure.epic("Bank API")
@allure.feature("Переводы")
@allure.parent_suite("API-тесты")
@allure.suite("Переводы")
@pytest.mark.api
class TestTransfers:
    @allure.title("Перевод корректно изменяет балансы обоих счетов")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_transfer_between_own_accounts(self, make_user, bank_data):
        user = make_user(UserRole.USER)
        source = user.create_account()
        target = user.create_account()
        user.deposit(source.id, bank_data.deposit_amount)

        transfer = user.transfer(source.id, target.id, bank_data.transfer_amount)

        with allure.step("Проверить результат операции"):
            assert transfer.from_account_id == source.id
            assert transfer.to_account_id == target.id
            assert transfer.from_account_balance == bank_data.remaining_balance
            assert user.get_account(source.id).balance == bank_data.remaining_balance
            assert user.get_account(target.id).balance == bank_data.transfer_amount
