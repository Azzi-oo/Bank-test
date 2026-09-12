from datetime import datetime
from decimal import Decimal

import allure

from src.main.api.db.models.crud.bank_crud import BankCrudDb
from src.main.api.db.models.bank_tables import Transaction
from src.main.api.models.account import AccountResponse
from src.main.api.models.credit import CreditResponse

Money = Decimal | float | int | str
TransactionSnapshot = tuple[int, str, float, int | None, int | None, int | None, datetime]
CreditSnapshot = tuple[int, int, float, int, float, datetime]


def money(value: Money) -> Decimal:
    # PostgreSQL хранит DOUBLE PRECISION; сравниваем денежные значения без округления.
    return Decimal(str(value))


def assert_balance(bank_db: BankCrudDb, account_id: int, expected: Money) -> None:
    saved = bank_db.get_account(account_id)
    assert saved is not None
    assert money(saved.balance) == Decimal(str(expected))


def assert_transaction(
    row: Transaction, kind: str, amount: Money, source: int | None = None,
    target: int | None = None, credit: int | None = None,
) -> None:
    assert row.id > 0
    assert row.transaction_type == kind
    assert money(row.amount) == Decimal(str(amount))
    assert row.from_account_id == source
    assert row.to_account_id == target
    assert row.credit_id == credit
    assert row.created_at is not None


def transaction_snapshot(bank_db: BankCrudDb, account_id: int) -> list[TransactionSnapshot]:
    return [
        (row.id, row.transaction_type, row.amount, row.from_account_id,
         row.to_account_id, row.credit_id, row.created_at)
        for row in bank_db.get_transactions(account_id)
    ]


class BankDbSteps:
    def __init__(self, bank_db: BankCrudDb) -> None:
        self.bank_db = bank_db

    @allure.step("Проверить новый счёт в БД")
    def check_empty_account(self, account_id: int) -> None:
        assert_balance(self.bank_db, account_id, 0)
        assert self.bank_db.get_credits(account_id) == []
        assert self.bank_db.get_transactions(account_id) == []

    @allure.step("Проверить состояние счетов перед переводом")
    def snapshot_before_transfer(
        self, source_id: int, target_id: int, balance: Money,
    ) -> list[TransactionSnapshot]:
        assert_balance(self.bank_db, source_id, balance)
        self.check_empty_account(target_id)
        before = transaction_snapshot(self.bank_db, source_id)
        assert len(before) == 1
        return before

    @allure.step("Проверить состояние кредита перед погашением")
    def snapshot_before_repayment(
        self, account_id: int, amount: Money,
    ) -> tuple[CreditSnapshot, list[TransactionSnapshot]]:
        assert_balance(self.bank_db, account_id, amount)
        credits = self.bank_db.get_credits(account_id)
        assert len(credits) == 1
        saved = credits[0]
        assert money(saved.balance) == -money(amount)
        before_credit = (saved.id, saved.account_id, saved.amount,
                         saved.term_months, saved.balance, saved.created_at)
        before_transactions = transaction_snapshot(self.bank_db, account_id)
        assert len(before_transactions) == 1
        return before_credit, before_transactions

    @allure.step("Проверить баланс и запись пополнения в БД")
    def check_deposit(self, account: AccountResponse, amount: Money) -> None:
        assert_balance(self.bank_db, account.id, amount)
        rows = self.bank_db.get_transactions(account.id)
        assert len(rows) == 1
        assert_transaction(rows[0], "deposit", amount, target=account.id)

    @allure.step("Проверить списание, зачисление и единственную запись перевода")
    def check_transfer(
        self, source: AccountResponse, target: AccountResponse,
        before: list[TransactionSnapshot], source_balance: Money, amount: Money,
    ) -> None:
        assert_balance(self.bank_db, source.id, money(source_balance) - money(amount))
        assert_balance(self.bank_db, target.id, amount)
        source_rows = self.bank_db.get_transactions(source.id)
        target_rows = self.bank_db.get_transactions(target.id)
        assert len(source_rows) == 2
        assert len(target_rows) == 1
        assert transaction_snapshot(self.bank_db, source.id)[:1] == before
        assert source_rows[-1].id == target_rows[0].id
        assert_transaction(target_rows[0], "transfer", amount,
                           source=source.id, target=target.id)

    @allure.step("Проверить кредит и транзакцию выдачи в БД")
    def check_credit(
        self, account: AccountResponse, response: CreditResponse, amount: Money, term_months: int,
    ) -> None:
        assert_balance(self.bank_db, account.id, amount)
        credits = self.bank_db.get_credits(account.id)
        assert len(credits) == 1
        saved = credits[0]
        assert saved.id == response.credit_id
        assert saved.account_id == account.id
        assert money(saved.amount) == money(amount)
        assert saved.term_months == term_months
        assert money(saved.balance) == -money(amount)
        assert saved.created_at is not None
        rows = self.bank_db.get_transactions(account.id)
        assert len(rows) == 1
        # CreditService выдаёт кредит через deposit без передачи credit_id.
        # Связь кредита со счётом проверена выше через credit.account_id.
        assert_transaction(rows[0], "credit_issuance", amount,
                           target=account.id)

    @allure.step("Проверить погашение кредита и запись списания в БД")
    def check_repayment(
        self, account: AccountResponse, credit: CreditResponse,
        before: list[TransactionSnapshot], amount: Money, term_months: int,
    ) -> None:
        assert_balance(self.bank_db, account.id, 0)
        credits = self.bank_db.get_credits(account.id)
        assert len(credits) == 1
        assert credits[0].id == credit.credit_id
        assert credits[0].account_id == account.id
        assert money(credits[0].balance) == 0
        assert money(credits[0].amount) == money(amount)
        assert credits[0].term_months == term_months
        rows = self.bank_db.get_transactions(account.id)
        assert len(rows) == 2
        assert transaction_snapshot(self.bank_db, account.id)[:1] == before
        assert_transaction(rows[-1], "credit_repayment", amount,
                           source=account.id, credit=credit.credit_id)

    @allure.step("Проверить отсутствие изменений после отказа в кредите")
    def check_forbidden_credit(self, account: AccountResponse) -> None:
        assert_balance(self.bank_db, account.id, 0)
        assert self.bank_db.get_credits(account.id) == []
        assert self.bank_db.get_transactions(account.id) == []

    @allure.step("Проверить неизменность счёта, кредита и транзакций")
    def check_rejected_repayment(
        self, account: AccountResponse, before_credit: CreditSnapshot,
        before_transactions: list[TransactionSnapshot], amount: Money,
    ) -> None:
        assert_balance(self.bank_db, account.id, amount)
        credits = self.bank_db.get_credits(account.id)
        assert len(credits) == 1
        saved = credits[0]
        assert (saved.id, saved.account_id, saved.amount, saved.term_months,
                saved.balance, saved.created_at) == before_credit
        assert transaction_snapshot(self.bank_db, account.id) == before_transactions
