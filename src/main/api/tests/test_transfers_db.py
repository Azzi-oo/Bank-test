import allure
import pytest

from src.main.api.fixtures.bank_fixture import TransferContext
from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.steps.bank_db_steps import BankDbSteps


@allure.epic("Bank API")
@allure.feature("Переводы")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Переводы — БД")
@pytest.mark.api
@pytest.mark.db
class TestTransfersDb:
    @allure.title("Transfer: оба баланса и транзакция сохраняются в БД")
    def test_transfer_is_persisted(
        self, transfer_context: TransferContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = transfer_context.user.transfer(
            transfer_context.source.id, transfer_context.target.id, bank_data.transfer_amount,
        )

        assert response.from_account_id == transfer_context.source.id
        assert response.to_account_id == transfer_context.target.id
        assert response.from_account_balance == bank_data.remaining_balance
        bank_db_steps.check_transfer(
            transfer_context.source, transfer_context.target, transfer_context.before,
            source_balance=bank_data.deposit_amount, amount=bank_data.transfer_amount,
        )
