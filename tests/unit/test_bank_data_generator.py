import random
from decimal import Decimal

from src.main.api.generators.bank_data_generator import BankDataGenerator
from src.main.api.models.requests import CreditRequest, DepositRequest, TransferRequest


def test_generated_scenarios_respect_api_limits_and_balance_relationships():
    rng = random.Random(42)
    samples = [BankDataGenerator.generate(rng) for _ in range(100)]
    for data in samples:
        DepositRequest(account_id=1, amount=data.deposit_amount)
        TransferRequest(from_account_id=1, to_account_id=2, amount=data.transfer_amount)
        CreditRequest(account_id=1, amount=data.credit_amount, term_months=data.term_months)
        assert 0 < data.transfer_amount < data.deposit_amount
        assert 0 < data.partial_repayment < data.credit_amount
        assert 5_000 <= data.credit_amount <= 15_000
        assert 1_000 <= data.deposit_amount <= 9_000
        assert 500 <= data.transfer_amount <= 10_000
        assert Decimal(str(data.remaining_balance)) == (
            Decimal(str(data.deposit_amount)) - Decimal(str(data.transfer_amount))
        )
    assert len({data.credit_amount for data in samples}) > 1
    assert any(not data.deposit_amount.is_integer() for data in samples)


def test_generator_can_reproduce_data_with_seed():
    assert BankDataGenerator.generate(random.Random(123)) == BankDataGenerator.generate(random.Random(123))
