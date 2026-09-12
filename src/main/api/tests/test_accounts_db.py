import allure
import pytest

from src.main.api.fixtures.bank_fixture import AccountContext
from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.steps.bank_db_steps import BankDbSteps


@allure.epic("Bank API")
@allure.feature("Счета")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Счета — БД")
@pytest.mark.api
@pytest.mark.db
class TestAccountsDb:
    @allure.title("Deposit: баланс и транзакция сохраняются в БД")
    def test_deposit_is_persisted(
        self, deposit_context: AccountContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = deposit_context.user.deposit(deposit_context.account.id, bank_data.deposit_amount)

        assert response.id == deposit_context.account.id
        assert response.balance == bank_data.deposit_amount
        bank_db_steps.check_deposit(deposit_context.account, amount=bank_data.deposit_amount)
