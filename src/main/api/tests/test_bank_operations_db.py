from decimal import Decimal

import allure
import pytest

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.requests import UserRole
from src.main.api.specs.response_specs import ResponseSpecs


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


@allure.epic("Bank API")
@allure.feature("Банковские операции")
@allure.story("Сохранение в PostgreSQL")
@allure.parent_suite("API-тесты")
@allure.suite("Банковские операции — БД")
@pytest.mark.api
@pytest.mark.db
class TestBankOperationsDb:
    @allure.title("Deposit: баланс и транзакция сохраняются в БД")
    def test_deposit_is_persisted(self, make_user, bank_db):
        user = make_user(UserRole.USER)
        account = user.create_account()
        assert_balance(bank_db, account.id, 0)
        assert bank_db.get_transactions(account.id) == []

        response = user.deposit(account.id, 1000.50)

        with allure.step("Проверить баланс и запись пополнения в БД"):
            assert response.id == account.id
            assert response.balance == Decimal("1000.50")
            assert_balance(bank_db, account.id, response.balance)
            rows = bank_db.get_transactions(account.id)
            assert len(rows) == 1
            assert_transaction(rows[0], "deposit", "1000.50", target=account.id)

    @allure.title("Transfer: оба баланса и транзакция сохраняются в БД")
    def test_transfer_is_persisted(self, make_user, bank_db):
        user = make_user(UserRole.USER)
        source = user.create_account()
        target = user.create_account()
        user.deposit(source.id, 1000.50)
        assert_balance(bank_db, source.id, "1000.50")
        assert_balance(bank_db, target.id, 0)
        before = transaction_snapshot(bank_db, source.id)
        assert len(before) == 1
        assert bank_db.get_transactions(target.id) == []

        response = user.transfer(source.id, target.id, 500.75)

        with allure.step("Проверить списание, зачисление и единственную запись перевода"):
            assert response.from_account_id == source.id
            assert response.to_account_id == target.id
            assert response.from_account_balance == Decimal("499.75")
            assert_balance(bank_db, source.id, "499.75")
            assert_balance(bank_db, target.id, "500.75")
            source_rows = bank_db.get_transactions(source.id)
            target_rows = bank_db.get_transactions(target.id)
            assert len(source_rows) == 2
            assert len(target_rows) == 1
            assert transaction_snapshot(bank_db, source.id)[:1] == before
            assert source_rows[-1].id == target_rows[0].id
            assert_transaction(target_rows[0], "transfer", "500.75",
                               source=source.id, target=target.id)

    @allure.title("Credit: кредит, задолженность и зачисление сохраняются в БД")
    def test_credit_is_persisted(self, make_user, bank_db):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        assert_balance(bank_db, account.id, 0)
        assert bank_db.get_credits(account.id) == []
        assert bank_db.get_transactions(account.id) == []

        response = user.request_credit(account.id, 5000, 12)

        with allure.step("Проверить кредит и транзакцию выдачи в БД"):
            assert response.id == account.id
            assert response.amount == 5000
            assert_balance(bank_db, account.id, 5000)
            credits = bank_db.get_credits(account.id)
            assert len(credits) == 1
            saved = credits[0]
            assert saved.id == response.credit_id
            assert saved.account_id == account.id
            assert money(saved.amount) == 5000
            assert saved.term_months == 12
            assert money(saved.balance) == -5000
            assert saved.created_at is not None
            rows = bank_db.get_transactions(account.id)
            assert len(rows) == 1
            # CreditService выдаёт кредит через deposit без передачи credit_id.
            # Связь кредита со счётом проверена выше через credit.account_id.
            assert_transaction(rows[0], "credit_issuance", 5000,
                               target=account.id)

    @allure.title("Repay: погашение сохраняет списание и нулевую задолженность в БД")
    def test_repayment_is_persisted(self, make_user, bank_db):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, 5000, 12)
        assert_balance(bank_db, account.id, 5000)
        credits = bank_db.get_credits(account.id)
        assert len(credits) == 1
        assert money(credits[0].balance) == -5000
        before = transaction_snapshot(bank_db, account.id)
        assert len(before) == 1

        response = user.repay_credit(credit.credit_id, account.id, 5000)

        with allure.step("Проверить погашение кредита и запись списания в БД"):
            assert response.credit_id == credit.credit_id
            assert response.amount_deposited == 5000
            assert_balance(bank_db, account.id, 0)
            credits = bank_db.get_credits(account.id)
            assert len(credits) == 1
            assert credits[0].id == credit.credit_id
            assert credits[0].account_id == account.id
            assert money(credits[0].balance) == 0
            assert money(credits[0].amount) == 5000
            assert credits[0].term_months == 12
            rows = bank_db.get_transactions(account.id)
            assert len(rows) == 2
            assert transaction_snapshot(bank_db, account.id)[:1] == before
            assert_transaction(rows[-1], "credit_repayment", 5000,
                               source=account.id, credit=credit.credit_id)

    @allure.title("Запрещённый кредит не изменяет БД")
    def test_forbidden_credit_leaves_db_unchanged(self, make_user, bank_db):
        user = make_user(UserRole.USER)
        account = user.create_account()
        assert_balance(bank_db, account.id, 0)
        assert bank_db.get_credits(account.id) == []
        assert bank_db.get_transactions(account.id) == []

        user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
            "accountId": account.id, "amount": 5000, "termMonths": 12,
        })

        with allure.step("Проверить отсутствие изменений после отказа в кредите"):
            assert_balance(bank_db, account.id, 0)
            assert bank_db.get_credits(account.id) == []
            assert bank_db.get_transactions(account.id) == []

    @allure.title("Отклонённое частичное погашение не изменяет БД")
    def test_partial_repayment_leaves_db_unchanged(self, make_user, bank_db):
        user = make_user(UserRole.CREDIT_SECRET)
        account = user.create_account()
        credit = user.request_credit(account.id, 5000, 12)
        assert_balance(bank_db, account.id, 5000)
        credits = bank_db.get_credits(account.id)
        assert len(credits) == 1
        saved = credits[0]
        before_credit = (saved.id, saved.account_id, saved.amount,
                         saved.term_months, saved.balance, saved.created_at)
        before_transactions = transaction_snapshot(bank_db, account.id)

        user.raw(Endpoint.CREDIT_REPAY, ResponseSpecs.status(422)).post({
            "creditId": credit.credit_id, "accountId": account.id, "amount": 1000,
        })

        with allure.step("Проверить неизменность счёта, кредита и транзакций"):
            assert_balance(bank_db, account.id, 5000)
            credits = bank_db.get_credits(account.id)
            assert len(credits) == 1
            saved = credits[0]
            assert (saved.id, saved.account_id, saved.amount, saved.term_months,
                    saved.balance, saved.created_at) == before_credit
            assert transaction_snapshot(bank_db, account.id) == before_transactions
