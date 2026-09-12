import allure
import pytest

from src.main.api.models.requests import UserRole


@allure.epic("Bank API")
@allure.feature("Счета")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Счета — БД")
@pytest.mark.api
@pytest.mark.db
class TestAccountsDb:
    @allure.title("Deposit: баланс и транзакция сохраняются в БД")
    def test_deposit_is_persisted(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.USER)
        account = user.create_account()
        bank_db_steps.check_empty_account(account.id)

        response = user.deposit(account.id, bank_data.deposit_amount)

        bank_db_steps.check_deposit(account, response, amount=bank_data.deposit_amount)
