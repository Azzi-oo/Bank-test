import allure

import pytest

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.fixtures.bank_fixture import AccountContext, ApiRepaymentContext
from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.specs.response_specs import ResponseSpecs


@allure.epic("Bank API")
@allure.feature("Кредиты")
@allure.parent_suite("API-тесты")
@allure.suite("Кредиты")
@pytest.mark.api
class TestCredits:
    @allure.title("Кредит зачисляется на счёт и появляется в истории")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_with_credit_role_can_request_credit(
        self, credit_account: AccountContext, bank_data: BankTestData,
    ) -> None:
        credit = credit_account.user.request_credit(credit_account.account.id, bank_data.credit_amount, bank_data.term_months)

        with allure.step("Проверить результат операции"):
            assert credit.id == credit_account.account.id
            assert credit.amount == bank_data.credit_amount
        history = credit_account.user.get_credit_history().credits
        with allure.step("Проверить результат операции"):
            assert len(history) == 1
            assert history[0].credit_id == credit.credit_id
            assert history[0].account_id == credit_account.account.id
            assert history[0].term_months == bank_data.term_months
            assert history[0].balance == -bank_data.credit_amount
            assert credit_account.user.get_account(credit_account.account.id).balance == bank_data.credit_amount

    @allure.title("Кредит без нужной роли запрещён: HTTP 403")
    @allure.story("Негативные сценарии")
    @allure.severity(allure.severity_level.NORMAL)
    def test_user_without_credit_role_cannot_request_credit(
        self, regular_account: AccountContext, bank_data: BankTestData,
    ) -> None:
        regular_account.user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
            "accountId": regular_account.account.id, "amount": bank_data.credit_amount, "termMonths": bank_data.term_months,
        })

        with allure.step("Проверить результат операции"):
            assert regular_account.user.get_account(regular_account.account.id).balance == 0

    @allure.title("Полное погашение обнуляет задолженность")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_credit_user_can_fully_repay_own_credit(
        self, api_repayment_context: ApiRepaymentContext, bank_data: BankTestData,
    ) -> None:
        repayment = api_repayment_context.user.repay_credit(api_repayment_context.credit.credit_id, api_repayment_context.account.id, bank_data.credit_amount)

        with allure.step("Проверить результат операции"):
            assert repayment.credit_id == api_repayment_context.credit.credit_id
            assert repayment.amount_deposited == bank_data.credit_amount
        history = api_repayment_context.user.get_credit_history().credits
        with allure.step("Проверить результат операции"):
            assert len(history) == 1
            assert history[0].credit_id == api_repayment_context.credit.credit_id
            assert history[0].balance == 0
            assert api_repayment_context.user.get_account(api_repayment_context.account.id).balance == 0

    @allure.title("Частичное погашение отклоняется без изменения баланса")
    @allure.story("Негативные сценарии")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partial_credit_repayment_returns_422(
        self, api_repayment_context: ApiRepaymentContext, bank_data: BankTestData,
    ) -> None:
        api_repayment_context.user.raw(Endpoint.CREDIT_REPAY, ResponseSpecs.status(422)).post({
            "creditId": api_repayment_context.credit.credit_id, "accountId": api_repayment_context.account.id, "amount": bank_data.partial_repayment,
        })

        with allure.step("Проверить результат операции"):
            assert api_repayment_context.user.get_account(api_repayment_context.account.id) == api_repayment_context.before_account
            assert api_repayment_context.user.get_credit_history() == api_repayment_context.before_history
