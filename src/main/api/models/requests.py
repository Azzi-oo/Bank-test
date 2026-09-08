from enum import StrEnum

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    USER = "ROLE_USER"
    ADMIN = "ROLE_ADMIN"
    CREDIT_SECRET = "ROLE_CREDIT_SECRET"


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=15)
    password: str
    role: UserRole


class CreditRequest(BaseModel):
    account_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    term_months: int = Field(ge=1, le=60)