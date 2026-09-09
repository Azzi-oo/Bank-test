from typing import cast

from src.main.api.foundation.endpoint import Endpoint
from src.main.api.models.account import AccountResponse, TransferResponse
from src.main.api.models.auth import LoginResponse
from src.main.api.models.credit import CreditHistoryResponse, CreditResponse, RepayCreditResponse
from src.main.api.models.requests import (
    CreditRequest, DepositRequest, LoginRequest, RepayCreditRequest, TransferRequest,
)
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def login(self, username: str, password: str) -> LoginResponse:
        return cast(LoginResponse, self.validated(Endpoint.AUTH_LOGIN).post(
            LoginRequest(username=username, password=password),
        ))

    def create_account(self) -> AccountResponse:
        return cast(AccountResponse, self.validated(Endpoint.ACCOUNT_CREATE).post())

    def deposit(self, account_id: int, amount: float) -> AccountResponse:
        return cast(AccountResponse, self.validated(Endpoint.ACCOUNT_DEPOSIT).post(
            DepositRequest(account_id=account_id, amount=amount),
        ))

    def transfer(self, from_account_id: int, to_account_id: int, amount: float) -> TransferResponse:
        return cast(TransferResponse, self.validated(Endpoint.ACCOUNT_TRANSFER).post(
            TransferRequest(from_account_id=from_account_id, to_account_id=to_account_id, amount=amount),
        ))

    def get_account(self, account_id: int) -> AccountResponse:
        return cast(AccountResponse, self.validated(Endpoint.ACCOUNT_TRANSACTIONS).get(account_id=account_id))

    def request_credit(self, account_id: int, amount: float, term_months: int) -> CreditResponse:
        return cast(CreditResponse, self.validated(Endpoint.CREDIT_REQUEST).post(
            CreditRequest(account_id=account_id, amount=amount, term_months=term_months),
        ))

    def get_credit_history(self) -> CreditHistoryResponse:
        return cast(CreditHistoryResponse, self.validated(Endpoint.CREDIT_HISTORY).get())

    def repay_credit(self, credit_id: int, account_id: int, amount: float) -> RepayCreditResponse:
        return cast(RepayCreditResponse, self.validated(Endpoint.CREDIT_REPAY).post(
            RepayCreditRequest(credit_id=credit_id, account_id=account_id, amount=amount),
        ))
