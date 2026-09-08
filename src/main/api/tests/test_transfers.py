import pytest

from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestTransfers:
    def test_user_can_transfer_between_own_accounts(self, make_user):
        user = make_user(UserRole.USER)

        from_account = user.accounts.create_account()
        to_account = user.accounts.create_account()

        assert from_account.status_code == 201, from_account.text
        assert to_account.status_code == 201, to_account.text

        from_account_id = from_account.json()["id"]
        to_account_id = to_account.json()["id"]

        deposit = user.accounts.deposit(
            account_id=from_account_id,
            amount=1000.50,
        )
        assert deposit.status_code == 200, deposit.text

        transfer = user.accounts.transfer(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=500.75,
        )

        assert transfer.status_code == 200, transfer.text
        assert transfer.json()["fromAccountId"] == from_account_id
        assert transfer.json()["toAccountId"] == to_account_id
        assert transfer.json()["fromAccountIdBalance"] == 499.75