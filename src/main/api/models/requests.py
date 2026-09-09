from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


from src.main.api.generators.creation_rule import CreationRule


class UserRole(StrEnum):
    USER = "ROLE_USER"
    ADMIN = "ROLE_ADMIN"
    CREDIT_SECRET = "ROLE_CREDIT_SECRET"


class ApiRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class LoginRequest(ApiRequest):
    username: str
    password: str


class CreateUserRequest(ApiRequest):
    username: Annotated[str, CreationRule(regex=r"^[A-Za-z0-9]{15}$")] = Field(
        min_length=3, max_length=15,
    )
    password: Annotated[str, CreationRule(regex=r"^[A-Z]{3}[a-z][0-9]{2}[!$_]{4}$")]
    role: Annotated[UserRole, CreationRule(regex=r"^ROLE_USER$")]


class DepositRequest(ApiRequest):
    account_id: int = Field(gt=0, alias="accountId")
    amount: float = Field(gt=0)


class TransferRequest(ApiRequest):
    from_account_id: int = Field(gt=0, alias="fromAccountId")
    to_account_id: int = Field(gt=0, alias="toAccountId")
    amount: float = Field(gt=0)


class CreditRequest(ApiRequest):
    account_id: int = Field(gt=0, alias="accountId")
    amount: float = Field(gt=0)
    term_months: int = Field(ge=1, le=60, alias="termMonths")


class RepayCreditRequest(ApiRequest):
    credit_id: int = Field(gt=0, alias="creditId")
    account_id: int = Field(gt=0, alias="accountId")
    amount: float = Field(gt=0)
