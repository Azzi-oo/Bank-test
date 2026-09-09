from decimal import Decimal

from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    id: int = Field(gt=0)
    balance: Decimal


class TransferResponse(BaseModel):
    from_account_id: int = Field(gt=0, alias="fromAccountId")
    to_account_id: int = Field(gt=0, alias="toAccountId")
    from_account_balance: Decimal = Field(alias="fromAccountIdBalance")
