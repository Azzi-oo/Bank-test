from decimal import Decimal

import pytest

from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestAccounts:
    def test_user_can_create_account(self, make_user):
        user = make_user(UserRole.USER)

        account = user.create_account()

        assert account.id > 0
        assert account.balance == 0

    def test_user_can_deposit_money(self, make_user):
        user = make_user(UserRole.USER)
        account = user.create_account()

        deposit = user.deposit(account.id, 1000.50)

        assert deposit.id == account.id
        assert deposit.balance == Decimal("1000.50")
        assert user.get_account(account.id).balance == Decimal("1000.50")
