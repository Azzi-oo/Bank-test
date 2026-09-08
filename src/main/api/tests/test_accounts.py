import pytest

from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestAccounts:
    def test_user_can_create_account(self, make_user):
        user = make_user(UserRole.USER)

        response = user.accounts.create_account()

        assert response.status_code == 201, response.text
        assert response.json()["id"] > 0
        assert response.json()["balance"] == 0

    def test_user_can_deposit_money(self, make_user):
        user = make_user(UserRole.USER)

        account_response = user.accounts.create_account()
        assert account_response.status_code == 201, account_response.text

        account_id = account_response.json()["id"]

        deposit_response = user.accounts.deposit(
            account_id=account_id,
            amount=1000.50,
        )

        assert deposit_response.status_code == 200, deposit_response.text
        assert deposit_response.json()["balance"] == 1000.50