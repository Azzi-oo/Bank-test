from collections.abc import Callable
from dataclasses import dataclass

import pytest

from src.main.api.generators.bank_data_generator import BankTestData
from src.main.api.models.account import AccountResponse
from src.main.api.models.credit import CreditHistoryResponse, CreditResponse
from src.main.api.models.requests import UserRole
from src.main.api.steps.bank_db_steps import BankDbSteps, CreditSnapshot, TransactionSnapshot
from src.main.api.steps.user_steps import UserSteps

UserFactory = Callable[[UserRole], UserSteps]


@dataclass(frozen=True)
class AccountContext:
    user: UserSteps
    account: AccountResponse


@dataclass(frozen=True)
class TransferContext:
    user: UserSteps
    source: AccountResponse
    target: AccountResponse
    before: list[TransactionSnapshot]


@dataclass(frozen=True)
class CreditContext:
    user: UserSteps
    account: AccountResponse
    credit: CreditResponse
    before_credit: CreditSnapshot
    before_transactions: list[TransactionSnapshot]


@pytest.fixture
def deposit_context(make_user: UserFactory, bank_db_steps: BankDbSteps) -> AccountContext:
    user = make_user(UserRole.USER)
    account = user.create_account()
    bank_db_steps.check_empty_account(account.id)
    return AccountContext(user, account)


@pytest.fixture
def credit_context(make_user: UserFactory, bank_db_steps: BankDbSteps) -> AccountContext:
    user = make_user(UserRole.CREDIT_SECRET)
    account = user.create_account()
    bank_db_steps.check_empty_account(account.id)
    return AccountContext(user, account)


@pytest.fixture
def transfer_context(
    make_user: UserFactory, bank_data: BankTestData, bank_db_steps: BankDbSteps,
) -> TransferContext:
    user = make_user(UserRole.USER)
    source = user.create_account()
    target = user.create_account()
    user.deposit(source.id, bank_data.deposit_amount)
    before = bank_db_steps.snapshot_before_transfer(
        source.id, target.id, balance=bank_data.deposit_amount,
    )
    return TransferContext(user, source, target, before)


@pytest.fixture
def repayment_context(
    credit_context: AccountContext, bank_data: BankTestData, bank_db_steps: BankDbSteps,
) -> CreditContext:
    user, account = credit_context.user, credit_context.account
    credit = user.request_credit(account.id, bank_data.credit_amount, bank_data.term_months)
    before_credit, before_transactions = bank_db_steps.snapshot_before_repayment(
        account.id, amount=bank_data.credit_amount,
    )
    return CreditContext(user, account, credit, before_credit, before_transactions)


@dataclass(frozen=True)
class ApiTransferContext:
    user: UserSteps
    source: AccountResponse
    target: AccountResponse


@dataclass(frozen=True)
class ApiRepaymentContext:
    user: UserSteps
    account: AccountResponse
    credit: CreditResponse
    before_account: AccountResponse
    before_history: CreditHistoryResponse


@pytest.fixture
def regular_user(make_user: UserFactory) -> UserSteps:
    return make_user(UserRole.USER)


@pytest.fixture
def regular_account(regular_user: UserSteps) -> AccountContext:
    return AccountContext(regular_user, regular_user.create_account())


@pytest.fixture
def credit_account(make_user: UserFactory) -> AccountContext:
    user = make_user(UserRole.CREDIT_SECRET)
    return AccountContext(user, user.create_account())


@pytest.fixture
def api_transfer_context(
    regular_account: AccountContext, bank_data: BankTestData,
) -> ApiTransferContext:
    user, source = regular_account.user, regular_account.account
    target = user.create_account()
    user.deposit(source.id, bank_data.deposit_amount)
    return ApiTransferContext(user, source, target)


@pytest.fixture
def api_repayment_context(
    credit_account: AccountContext, bank_data: BankTestData,
) -> ApiRepaymentContext:
    user, account = credit_account.user, credit_account.account
    credit = user.request_credit(account.id, bank_data.credit_amount, bank_data.term_months)
    return ApiRepaymentContext(
        user, account, credit, user.get_account(account.id), user.get_credit_history(),
    )
