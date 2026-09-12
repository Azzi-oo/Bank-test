import allure
import pytest

from src.main.api.fixtures.bank_fixture import AccountContext, CreditContext
from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.steps.bank_db_steps import BankDbSteps
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
    def test_credit_is_persisted(
        self, credit_context: AccountContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = credit_context.user.request_credit(
            credit_context.account.id, bank_data.credit_amount, bank_data.term_months,
        )

        assert response.id == credit_context.account.id
        assert response.amount == bank_data.credit_amount
        bank_db_steps.check_credit(
            credit_context.account, response,
            amount=bank_data.credit_amount, term_months=bank_data.term_months,
        )

    @allure.title("Repay: погашение сохраняет списание и нулевую задолженность в БД")
    def test_repayment_is_persisted(
        self, repayment_context: CreditContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = repayment_context.user.repay_credit(
            repayment_context.credit.credit_id, repayment_context.account.id, bank_data.credit_amount,
        )

        assert response.credit_id == repayment_context.credit.credit_id
        assert response.amount_deposited == bank_data.credit_amount
        bank_db_steps.check_repayment(
            repayment_context.account, repayment_context.credit, repayment_context.before_transactions,
            amount=bank_data.credit_amount, term_months=bank_data.term_months,
        )

    @allure.title("Запрещённый кредит не изменяет БД")
    def test_forbidden_credit_leaves_db_unchanged(
        self, deposit_context: AccountContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = deposit_context.user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
            "accountId": deposit_context.account.id,
            "amount": bank_data.credit_amount,
            "termMonths": bank_data.term_months,
        })

        assert response.status_code == 403
        bank_db_steps.check_forbidden_credit(deposit_context.account)

    @allure.title("Отклонённое частичное погашение не изменяет БД")
    def test_partial_repayment_leaves_db_unchanged(
        self, repayment_context: CreditContext, bank_db_steps: BankDbSteps, bank_data: BankTestData,
    ) -> None:
        response = repayment_context.user.raw(Endpoint.CREDIT_REPAY, ResponseSpecs.status(422)).post({
            "creditId": repayment_context.credit.credit_id,
            "accountId": repayment_context.account.id,
            "amount": bank_data.partial_repayment,
        })

        assert response.status_code == 422
        bank_db_steps.check_rejected_repayment(
            repayment_context.account, repayment_context.before_credit,
            repayment_context.before_transactions, amount=bank_data.credit_amount,
        )
