"""Согласованные случайные данные для банковских сценариев."""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BankTestData:
    deposit_amount: float
    transfer_amount: float
    credit_amount: int
    term_months: int
    partial_repayment: int

    @property
    def remaining_balance(self) -> float:
        return self.deposit_amount - self.transfer_amount


class BankDataGenerator:
    # Ограничения DTO банковского API.
    MIN_CREDIT_AMOUNT = 5_000
    MAX_CREDIT_AMOUNT = 15_000
    MIN_TERM_MONTHS = 1
    MAX_TERM_MONTHS = 60
    MIN_DEPOSIT_AMOUNT = 1_000
    MAX_DEPOSIT_AMOUNT = 9_000
    MIN_TRANSFER_AMOUNT = 500
    MAX_TRANSFER_AMOUNT = 10_000
    MONEY_UNITS_PER_CURRENCY = 4

    @classmethod
    def generate(cls, rng: random.Random | None = None) -> BankTestData:
        rng = rng if rng is not None else random.Random()
        # Четверти денежной единицы точно представимы в DOUBLE PRECISION БД.
        # Это позволяет проверять точные балансы без случайных ошибок округления.
        deposit_units = rng.randint(
            cls.MIN_DEPOSIT_AMOUNT * cls.MONEY_UNITS_PER_CURRENCY,
            cls.MAX_DEPOSIT_AMOUNT * cls.MONEY_UNITS_PER_CURRENCY,
        )
        transfer_units = rng.randint(
            cls.MIN_TRANSFER_AMOUNT * cls.MONEY_UNITS_PER_CURRENCY,
            min(deposit_units - 1, cls.MAX_TRANSFER_AMOUNT * cls.MONEY_UNITS_PER_CURRENCY),
        )
        credit_amount = rng.randint(cls.MIN_CREDIT_AMOUNT, cls.MAX_CREDIT_AMOUNT)
        return BankTestData(
            deposit_amount=deposit_units / cls.MONEY_UNITS_PER_CURRENCY,
            transfer_amount=transfer_units / cls.MONEY_UNITS_PER_CURRENCY,
            credit_amount=credit_amount,
            term_months=rng.randint(cls.MIN_TERM_MONTHS, cls.MAX_TERM_MONTHS),
            partial_repayment=rng.randint(1, credit_amount - 1),
        )
