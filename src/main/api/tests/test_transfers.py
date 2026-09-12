import allure

import pytest

from src.main.api.fixtures.bank_fixture import ApiTransferContext
from src.main.api.generators.bank_data_generator import BankTestData


@allure.epic("Bank API")
@allure.feature("Переводы")
@allure.parent_suite("API-тесты")
@allure.suite("Переводы")
@pytest.mark.api
class TestTransfers:
    @allure.title("Перевод корректно изменяет балансы обоих счетов")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_can_transfer_between_own_accounts(
        self, api_transfer_context: ApiTransferContext, bank_data: BankTestData,
    ) -> None:
        transfer = api_transfer_context.user.transfer(api_transfer_context.source.id, api_transfer_context.target.id, bank_data.transfer_amount)

        with allure.step("Проверить результат операции"):
            assert transfer.from_account_id == api_transfer_context.source.id
            assert transfer.to_account_id == api_transfer_context.target.id
            assert transfer.from_account_balance == bank_data.remaining_balance
            assert api_transfer_context.user.get_account(api_transfer_context.source.id).balance == bank_data.remaining_balance
            assert api_transfer_context.user.get_account(api_transfer_context.target.id).balance == bank_data.transfer_amount
