import allure
import pytest

from src.main.api.models.requests import UserRole


@allure.epic("Bank API")
@allure.feature("Переводы")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Переводы — БД")
@pytest.mark.api
@pytest.mark.db
class TestTransfersDb:
    @allure.title("Transfer: оба баланса и транзакция сохраняются в БД")
    def test_transfer_is_persisted(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.USER)
        source = user.create_account()
        target = user.create_account()
        user.deposit(source.id, bank_data.deposit_amount)
        before = bank_db_steps.snapshot_before_transfer(source.id, target.id, balance=bank_data.deposit_amount)

        response = user.transfer(source.id, target.id, bank_data.transfer_amount)

        bank_db_steps.check_transfer(source, target, response, before,
                                     source_balance=bank_data.deposit_amount, amount=bank_data.transfer_amount)
