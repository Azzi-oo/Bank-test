from collections.abc import Iterator
from sqlalchemy.engine import Engine
import pytest
from sqlalchemy.orm import Session

from src.main.api.db.engine import create_db_engine
from src.main.api.db.models.crud.user_crud import UserCrudDb
from src.main.api.db.models.crud.bank_crud import BankCrudDb
from src.main.api.steps.bank_db_steps import BankDbSteps


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    engine = create_db_engine()
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    with db_engine.connect() as connection:
        transaction = connection.begin()
        try:
            with Session(bind=connection) as session:
                yield session
        finally:
            if transaction.is_active:
                transaction.rollback()


@pytest.fixture
def user_db(db_session: Session) -> UserCrudDb:
    return UserCrudDb(db_session)


@pytest.fixture
def bank_db(db_session: Session) -> BankCrudDb:
    return BankCrudDb(db_session)


@pytest.fixture
def bank_db_steps(bank_db: BankCrudDb) -> BankDbSteps:
    return BankDbSteps(bank_db)
