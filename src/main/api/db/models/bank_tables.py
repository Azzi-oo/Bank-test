from sqlalchemy import Column, DateTime, Float, Integer, String

from src.main.api.db.base import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    number = Column(String(7), nullable=False)
    balance = Column(Float, nullable=False)


class Credit(Base):
    __tablename__ = "credit"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    to_account_id = Column(Integer)
    from_account_id = Column(Integer)
    credit_id = Column(Integer)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
