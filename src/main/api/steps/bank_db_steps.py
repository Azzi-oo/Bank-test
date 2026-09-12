from decimal import Decimal

import allure

from src.main.api.db.models.crud.bank_crud import BankCrudDb


def money(value):
    # PostgreSQL хранит DOUBLE PRECISION; сравниваем денежные значения без округления.
    return Decimal(str(value))


def assert_balance(bank_db, account_id, expected):
    saved = bank_db.get_account(account_id)
    assert saved is not None
    assert money(saved.balance) == Decimal(str(expected))


def assert_transaction(row, kind, amount, source=None, target=None, credit=None):
    assert row.id > 0
    assert row.transaction_type == kind
    assert money(row.amount) == Decimal(str(amount))
    assert row.from_account_id == source
    assert row.to_account_id == target
    assert row.credit_id == credit
    assert row.created_at is not None


def transaction_snapshot(bank_db, account_id):
    return [
        (row.id, row.transaction_type, row.amount, row.from_account_id,
         row.to_account_id, row.credit_id, row.created_at)
        for row in bank_db.get_transactions(account_id)
    ]


class BankDbSteps:
    def __init__(self, bank_db: BankCrudDb):
        self.bank_db = bank_db

    @allure.step("Проверить новый счёт в БД")
    def check_empty_account(self, account_id):
        assert_balance(self.bank_db, account_id, 0)
        assert self.bank_db.get_credits(account_id) == []
        assert self.bank_db.get_transactions(account_id) == []

    @allure.step("Проверить состояние счетов перед переводом")
    def snapshot_before_transfer(self, source_id, target_id, balance):
        assert_balance(self.bank_db, source_id, balance)
        self.check_empty_account(target_id)
        before = transaction_snapshot(self.bank_db, source_id)
        assert len(before) == 1
        return before

    @allure.step("Проверить состояние кредита перед погашением")
    def snapshot_before_repayment(self, account_id, amount):
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
    def check_deposit(self, account, response, amount):
        assert response.id == account.id
        assert response.balance == money(amount)
        assert_balance(self.bank_db, account.id, response.balance)
        rows = self.bank_db.get_transactions(account.id)
        assert len(rows) == 1
        assert_transaction(rows[0], "deposit", amount, target=account.id)

    @allure.step("Проверить списание, зачисление и единственную запись перевода")
    def check_transfer(self, source, target, response, before, source_balance, amount):
        assert response.from_account_id == source.id
        assert response.to_account_id == target.id
        assert response.from_account_balance == money(source_balance) - money(amount)
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
    def check_credit(self, account, response, amount, term_months):
        assert response.id == account.id
        assert response.amount == money(amount)
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
    def check_repayment(self, account, credit, response, before, amount, term_months):
        assert response.credit_id == credit.credit_id
        assert response.amount_deposited == money(amount)
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
    def check_forbidden_credit(self, account):
        assert_balance(self.bank_db, account.id, 0)
        assert self.bank_db.get_credits(account.id) == []
        assert self.bank_db.get_transactions(account.id) == []

    @allure.step("Проверить неизменность счёта, кредита и транзакций")
    def check_rejected_repayment(self, account, before_credit, before_transactions, amount):
        assert_balance(self.bank_db, account.id, amount)
        credits = self.bank_db.get_credits(account.id)
        assert len(credits) == 1
        saved = credits[0]
        assert (saved.id, saved.account_id, saved.amount, saved.term_months,
                saved.balance, saved.created_at) == before_credit
        assert transaction_snapshot(self.bank_db, account.id) == before_transactions
