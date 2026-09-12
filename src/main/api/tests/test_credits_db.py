import allure
import pytest

from src.main.api.models.requests import UserRole
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.specs.response_specs import ResponseSpecs


@allure.epic("Bank API")
@allure.feature("Кредиты")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Кредиты — БД")
@pytest.mark.api
@pytest.mark.db
class TestCreditsDb:
    @allure.title("Credit: кредит, задолженность и зачисление сохраняются в БД")
    def test_credit_is_persisted(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        bank_db_steps.check_empty_account(account.id)

        response = user.request_credit(account.id, bank_data.credit_amount, bank_data.term_months)

        bank_db_steps.check_credit(account, response, amount=bank_data.credit_amount, term_months=bank_data.term_months)

    @allure.title("Repay: погашение сохраняет списание и нулевую задолженность в БД")
    def test_repayment_is_persisted(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, bank_data.credit_amount, bank_data.term_months)
        _, before = bank_db_steps.snapshot_before_repayment(account.id, amount=bank_data.credit_amount)

        response = user.repay_credit(credit.credit_id, account.id, bank_data.credit_amount)

        bank_db_steps.check_repayment(account, credit, response, before,
                                      amount=bank_data.credit_amount, term_months=bank_data.term_months)

    @allure.title("Запрещённый кредит не изменяет БД")
    def test_forbidden_credit_leaves_db_unchanged(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.USER)
        account = user.create_account()
        bank_db_steps.check_empty_account(account.id)

        user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
            "accountId": account.id, "amount": bank_data.credit_amount, "termMonths": bank_data.term_months,
        })

        bank_db_steps.check_forbidden_credit(account)

    @allure.title("Отклонённое частичное погашение не изменяет БД")
    def test_partial_repayment_leaves_db_unchanged(self, make_user, bank_db_steps, bank_data):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, bank_data.credit_amount, bank_data.term_months)
        before_credit, before_transactions = bank_db_steps.snapshot_before_repayment(
            account.id, amount=bank_data.credit_amount,
        )

        user.raw(Endpoint.CREDIT_REPAY, ResponseSpecs.status(422)).post({
            "creditId": credit.credit_id, "accountId": account.id, "amount": bank_data.partial_repayment,
        })

        bank_db_steps.check_rejected_repayment(
            account, before_credit, before_transactions, amount=bank_data.credit_amount,
        )
