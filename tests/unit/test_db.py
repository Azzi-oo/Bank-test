from datetime import datetime

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session

from src.main.api.db.base import Base
from src.main.api.db.models.bank_tables import Account, Credit, Transaction
from src.main.api.db.models.crud.bank_crud import BankCrudDb
from src.main.api.db.engine import database_url
from src.main.api.db.models.crud.user_crud import UserCrudDb
from src.main.api.db.models.user_tabs import User


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)  # Только автономная временная SQLite.
    with Session(engine) as session:
        session.add(User(id=1, username="tester", role="ROLE_USER"))
        session.commit()
        yield session
    engine.dispose()


def test_user_lookup_and_missing_user(db):
    crud = UserCrudDb(db)
    assert crud.get_user_by_username("tester").role == "ROLE_USER"
    assert crud.get_user_by_username("missing") is None
    assert crud.get_user_by_username("' OR 1=1 --") is None


def test_lookup_refreshes_cached_user_after_external_update(db):
    crud = UserCrudDb(db)
    first = crud.get_user_by_username("tester")
    assert first.deleted_at is None
    timestamp = datetime(2026, 9, 12)
    with db.bind.begin() as connection:
        connection.execute(update(User).values(deleted_at=timestamp).where(User.id == 1))
    assert crud.get_user_by_username("tester").deleted_at == timestamp


def test_database_url_environment_has_priority(monkeypatch):
    monkeypatch.setenv("BANK_DATABASE_URL", "postgresql+psycopg2://example/test")
    assert database_url() == "postgresql+psycopg2://example/test"


def test_bank_reads_filter_accounts_and_refresh_external_changes(db):
    now = datetime(2026, 9, 12)
    db.add_all([
        Account(id=1, user_id=1, number="0000001", balance=1000.50),
        Account(id=2, user_id=1, number="0000002", balance=0),
        Account(id=3, user_id=1, number="0000003", balance=0),
        Credit(id=1, account_id=1, amount=5000, term_months=12,
               balance=-5000, created_at=now),
        Credit(id=2, account_id=3, amount=100, term_months=1,
               balance=-100, created_at=now),
        Transaction(id=1, from_account_id=1, to_account_id=2,
                    amount=500.75, transaction_type="transfer", created_at=now),
        Transaction(id=2, to_account_id=3, amount=100,
                    transaction_type="deposit", created_at=now),
    ])
    db.commit()
    crud = BankCrudDb(db)
    account = crud.get_account(1)
    credit = crud.get_credits(1)[0]
    assert account.balance == 1000.50
    assert credit.id == 1
    assert [row.id for row in crud.get_credits(1)] == [1]
    assert [row.id for row in crud.get_transactions(1)] == [1]
    assert [row.id for row in crud.get_transactions(2)] == [1]
    assert crud.get_account(999) is None
    assert crud.get_credits(999) == []
    assert crud.get_transactions(999) == []

    with db.bind.begin() as connection:
        connection.execute(update(Account).where(Account.id == 1).values(balance=499.75))
        connection.execute(update(Credit).where(Credit.id == 1).values(balance=0))
    assert crud.get_account(1).balance == 499.75
    assert crud.get_credits(1)[0].balance == 0
