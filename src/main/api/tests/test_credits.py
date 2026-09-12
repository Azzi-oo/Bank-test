import allure

import pytest

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import UserRole
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
    def test_user_with_credit_role_can_request_credit(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()

        credit = user.request_credit(account.id, 5000, 12)

        with allure.step("Проверить результат операции"):
            assert credit.id == account.id
            assert credit.amount == 5000
        history = user.get_credit_history().credits
        with allure.step("Проверить результат операции"):
            assert len(history) == 1
            assert history[0].credit_id == credit.credit_id
            assert history[0].account_id == account.id
            assert history[0].term_months == 12
            assert history[0].balance == -5000
            assert user.get_account(account.id).balance == 5000

    @allure.title("Кредит без нужной роли запрещён: HTTP 403")
    @allure.story("Негативные сценарии")
    @allure.severity(allure.severity_level.NORMAL)
    def test_user_without_credit_role_cannot_request_credit(self, make_user):
        user = make_user(UserRole.USER)
        account = user.create_account()

        user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
            "accountId": account.id, "amount": 5000, "termMonths": 12,
        })

        with allure.step("Проверить результат операции"):
            assert user.get_account(account.id).balance == 0

    @allure.title("Полное погашение обнуляет задолженность")
    @allure.story("Положительные сценарии")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_credit_user_can_fully_repay_own_credit(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, 5000, 12)

        repayment = user.repay_credit(credit.credit_id, account.id, 5000)

        with allure.step("Проверить результат операции"):
            assert repayment.credit_id == credit.credit_id
            assert repayment.amount_deposited == 5000
        history = user.get_credit_history().credits
        with allure.step("Проверить результат операции"):
            assert len(history) == 1
            assert history[0].credit_id == credit.credit_id
            assert history[0].balance == 0
            assert user.get_account(account.id).balance == 0

    @allure.title("Частичное погашение отклоняется без изменения баланса")
    @allure.story("Негативные сценарии")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partial_credit_repayment_returns_422(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, 5000, 12)
        before_account = user.get_account(account.id)
        before_history = user.get_credit_history()

        user.raw(Endpoint.CREDIT_REPAY, ResponseSpecs.status(422)).post({
            "creditId": credit.credit_id, "accountId": account.id, "amount": 1000,
        })

        with allure.step("Проверить результат операции"):
            assert user.get_account(account.id) == before_account
            assert user.get_credit_history() == before_history
