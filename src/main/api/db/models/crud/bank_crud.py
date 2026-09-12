import allure
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.main.api.db.models.bank_tables import Account, Credit, Transaction
from src.main.api.reporting import attach_json


class BankCrudDb:
    def __init__(self, db: Session):
        self.db = db

    def _read(self, statement):
        rows = self.db.scalars(statement.execution_options(populate_existing=True)).all()
        attach_json("Записи БД", [
            {column.name: getattr(row, column.name) for column in row.__table__.columns}
            for row in rows
        ])
        return rows

    @allure.step("БД: получить счёт {account_id}")
    def get_account(self, account_id: int) -> Account | None:
        rows = self._read(select(Account).where(Account.id == account_id))
        return rows[0] if rows else None

    @allure.step("БД: получить кредиты счёта {account_id}")
    def get_credits(self, account_id: int) -> list[Credit]:
        return self._read(select(Credit).where(Credit.account_id == account_id).order_by(Credit.id))

    @allure.step("БД: получить транзакции счёта {account_id}")
    def get_transactions(self, account_id: int) -> list[Transaction]:
        return self._read(select(Transaction).where(or_(
            Transaction.from_account_id == account_id,
            Transaction.to_account_id == account_id,
        )).order_by(Transaction.id))
