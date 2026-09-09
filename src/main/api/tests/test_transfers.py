from decimal import Decimal

import pytest

from src.main.api.models.requests import UserRole


@pytest.mark.api
class TestTransfers:
    def test_user_can_transfer_between_own_accounts(self, make_user):
        user = make_user(UserRole.USER)
        source = user.create_account()
        target = user.create_account()
        user.deposit(source.id, 1000.50)

        transfer = user.transfer(source.id, target.id, 500.75)

        assert transfer.from_account_id == source.id
        assert transfer.to_account_id == target.id
        assert transfer.from_account_balance == Decimal("499.75")
        assert user.get_account(source.id).balance == Decimal("499.75")
        assert user.get_account(target.id).balance == Decimal("500.75")
