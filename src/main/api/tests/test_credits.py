import pytest

from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestCredits:
    def test_user_with_credit_role_can_request_credit(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)

        account_response = user.accounts.create_account()
        assert account_response.status_code == 201, account_response.text

        account_id = account_response.json()["id"]

        response = user.credits.request_credit(
            account_id=account_id,
            amount=5000,
            term_months=12,
        )

        assert response.status_code == 201, response.text

    def test_user_without_credit_role_cannot_request_credit(self, make_user):
        user = make_user(UserRole.USER)

        account_response = user.accounts.create_account()
        assert account_response.status_code == 201, account_response.text

        response = user.credits.request_credit(
            account_id=account_response.json()["id"],
            amount=5000,
            term_months=12,
        )

        assert response.status_code == 403, response.text

    def test_credit_user_can_fully_repay_own_credit(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)

        account_response = user.accounts.create_account()
        assert account_response.status_code == 201, account_response.text
        account_id = account_response.json()["id"]

        request_response = user.credits.request_credit(
            account_id=account_id,
            amount=5000,
            term_months=12,
        )
        assert request_response.status_code == 201, request_response.text

        history_response = user.credits.get_history()
        assert history_response.status_code == 200, history_response.text

        credits = history_response.json()["credits"]
        credit = next(
            item for item in credits
            if item["accountId"] == account_id
        )

        repay_response = user.credits.repay_credit(
            credit_id=credit["creditId"],
            account_id=account_id,
            amount=5000,
        )

        assert repay_response.status_code == 200, repay_response.text

    def test_partial_credit_repayment_returns_422(self, make_user):
        user = make_user(UserRole.CREDIT_SECRET)

        account = user.accounts.create_account()
        assert account.status_code == 201, account.text
        account_id = account.json()["id"]

        credit = user.credits.request_credit(
            account_id=account_id,
            amount=5000,
            term_months=12,
        )
        assert credit.status_code == 201, credit.text

        history = user.credits.get_history()
        assert history.status_code == 200, history.text

        credit_id = next(
            item["creditId"]
            for item in history.json()["credits"]
            if item["accountId"] == account_id
        )

        response = user.credits.repay_credit(
            credit_id=credit_id,
            account_id=account_id,
            amount=1000,
        )

        assert response.status_code == 422, response.text