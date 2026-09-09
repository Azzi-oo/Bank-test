from decimal import Decimal

from pydantic import BaseModel, Field

from src.main.api.models.account import AccountResponse


class CreditResponse(AccountResponse):
    credit_id: int = Field(gt=0, alias="creditId")
    amount: Decimal


class CreditHistoryItem(BaseModel):
    credit_id: int = Field(gt=0, alias="creditId")
    account_id: int = Field(gt=0, alias="accountId")
    amount: Decimal
    balance: Decimal
    term_months: int = Field(alias="termMonths")


class CreditHistoryResponse(BaseModel):
    credits: list[CreditHistoryItem]


class RepayCreditResponse(BaseModel):
    credit_id: int = Field(gt=0, alias="creditId")
    amount_deposited: Decimal = Field(alias="amountDeposited")
