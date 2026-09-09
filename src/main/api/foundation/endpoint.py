from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel

from src.main.api.models.account import AccountResponse, TransferResponse
from src.main.api.models.auth import LoginResponse
from src.main.api.models.credit import (
    CreditHistoryResponse, CreditResponse, RepayCreditResponse,
)
from src.main.api.models.requests import (
    CreateUserRequest, CreditRequest, DepositRequest, LoginRequest,
    RepayCreditRequest, TransferRequest,
)
from src.main.api.models.user import CreateUserResponse


@dataclass(frozen=True)
class EndpointConfiguration:
    url: str
    method: str
    success_status: int
    request_model: type[BaseModel] | None = None
    response_model: type[BaseModel] | None = None


class Endpoint(Enum):
    AUTH_LOGIN = EndpointConfiguration(
        "/api/auth/token/login", "POST", 200, LoginRequest, LoginResponse,
    )
    ADMIN_CREATE_USER = EndpointConfiguration(
        "/api/admin/create", "POST", 200, CreateUserRequest, CreateUserResponse,
    )
    ADMIN_DELETE_USER = EndpointConfiguration("/api/admin/users/{user_id}", "DELETE", 200)
    ACCOUNT_CREATE = EndpointConfiguration(
        "/api/account/create", "POST", 201, response_model=AccountResponse,
    )
    ACCOUNT_DEPOSIT = EndpointConfiguration(
        "/api/account/deposit", "POST", 200, DepositRequest, AccountResponse,
    )
    ACCOUNT_TRANSFER = EndpointConfiguration(
        "/api/account/transfer", "POST", 200, TransferRequest, TransferResponse,
    )
    ACCOUNT_TRANSACTIONS = EndpointConfiguration(
        "/api/account/transactions/{account_id}", "GET", 200,
        response_model=AccountResponse,
    )
    CREDIT_REQUEST = EndpointConfiguration(
        "/api/credit/request", "POST", 201, CreditRequest, CreditResponse,
    )
    CREDIT_HISTORY = EndpointConfiguration(
        "/api/credit/history", "GET", 200, response_model=CreditHistoryResponse,
    )
    CREDIT_REPAY = EndpointConfiguration(
        "/api/credit/repay", "POST", 200, RepayCreditRequest, RepayCreditResponse,
    )
    CREATE_ACCOUNT = ACCOUNT_CREATE
