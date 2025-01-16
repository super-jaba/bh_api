from pydantic import BaseModel

from domain.common.exceptions import DomainException
from domain.issues.exceptions import IssueException, IssueNotFound
from domain.repositories.exceptions import RepositoryException, RepositoryNotFound
from domain.rewards.exceptions import (
    RewardException, 
    RewardNotFound, 
    NothingToRewardFor,
    IssueDoesNotExist,
    IssueIsClosed
)
from domain.users.exceptions import UserException, UserNotFound
from domain.wallet.exceptions import (
    WalletException,
    CouldNotCreateWallet,
    WalletNotFound,
    CouldNotCreateInvoice,
    CouldNotPayInvoice,
    InsufficientFunds,
)
from impl.common.exceptions import ImplException
from infrastructure.common.exceptions import InfrastructureException
from infrastructure.github.exceptions import (
    GithubException,
    LoginFailed,
    CouldNotFetchGithubUser,
    GithubIssueIsAlreadyClosed,
    GithubPullRequestNotFound,
    CouldNotFetchPullRequest
)
from infrastructure.lnbits.exceptions import (
    WalletAPIException,
    WalletCreationFailure,
    WalletFetchFailure,
    CreateInvoiceFailure,
    PayInvoiceFailure,
    InvoiceIsAlreadyPaid, NotEnoughSats
)

from .base import APIException
from ..common.jwt.exceptions import (
    JWTAPIException,
    TokenIsNotPresented,
    InvalidHeaderFormat,
    TokenIsExpired,
    TokenIsInvalid
)


class ExceptionDescription(BaseModel):
    code: int
    description: str


DOMAIN_EXCEPTION_MAPPING = {
    # Example:
    DomainException: ExceptionDescription(code=10000, description="Undocumented domain exception."),

    # Continue from here, group by subdomains
    UserException: ExceptionDescription(code=11000, description="User exception."),
    UserNotFound: ExceptionDescription(code=11001, description="User not found."),

    WalletException: ExceptionDescription(code=12000, description="Wallet exception."),
    CouldNotCreateWallet: ExceptionDescription(code=12001,
                                               description="Couldn't create wallet. Please try again later."),
    WalletNotFound: ExceptionDescription(code=12002, description="Wallet not found."),
    CouldNotCreateInvoice: ExceptionDescription(code=12003, description="Couldn't create invoice."),
    CouldNotPayInvoice: ExceptionDescription(code=12004, description="Couldn't pay invoice."),
    InsufficientFunds: ExceptionDescription(code=12005, description="Insufficient funds."),

    RewardException: ExceptionDescription(code=13000, description="Reward exception."),
    RewardNotFound: ExceptionDescription(code=13001, description="Reward not found."),
    NothingToRewardFor: ExceptionDescription(code=13002, description="Issue not found."),
    IssueDoesNotExist: ExceptionDescription(code=13003, description="Issue does not exist."),
    IssueIsClosed: ExceptionDescription(code=13004, description="Issue is already closed."),

    IssueException: ExceptionDescription(code=14000, description="Issue exception."),
    IssueNotFound: ExceptionDescription(code=14001, description="Issue not found."),

    RepositoryException: ExceptionDescription(code=15000, description="Repository exception."),
    RepositoryNotFound: ExceptionDescription(code=15001, description="Repository not found."),
}

IMPL_EXCEPTION_MAPPING = {
    # Example:
    ImplException: ExceptionDescription(code=20000, description="Undocumented implementation exception."),

    # Continue from here, group by subdomains
}

INFRASTRUCTURE_EXCEPTION_MAPPING = {
    # Example:
    InfrastructureException: ExceptionDescription(code=40000, description="Undocumented infrastructure exception."),

    GithubException: ExceptionDescription(code=41000, description="Github exception."),
    LoginFailed: ExceptionDescription(code=41001, description="Login failed."),
    CouldNotFetchGithubUser: ExceptionDescription(code=41002, description="Could not fetch Github user."),
    GithubIssueIsAlreadyClosed: ExceptionDescription(code=41003, description="GitHub issue is already closed."),
    GithubPullRequestNotFound: ExceptionDescription(code=41004, description="Github pull request not found."),
    CouldNotFetchPullRequest: ExceptionDescription(code=41005, description="Couldn't fetch pull request."),

    WalletAPIException: ExceptionDescription(code=42000, description="Wallet API exception."),
    WalletCreationFailure: ExceptionDescription(
        code=42001,
        description="Wallet creation failed. Please try again later."
    ),
    WalletFetchFailure: ExceptionDescription(
        code=42002,
        description="Wallet fetch failed. Please try again later."
    ),
    CreateInvoiceFailure: ExceptionDescription(
        code=42003,
        description="Could not create invoice. Please try again later."
    ),
    # skipping BadResponseBody
    PayInvoiceFailure: ExceptionDescription(
        code=42004,
        description="Could not pay invoice. Please try again later."
    ),
    InvoiceIsAlreadyPaid: ExceptionDescription(
        code=42005,
        description="Invoice is already paid. Please create a new invoice."
    ),
    NotEnoughSats: ExceptionDescription(
        code=42006,
        description="Not enough sats to perform the operation."
    )
}

API_EXCEPTION_MAPPING = {
    # Example:
    APIException: ExceptionDescription(code=30000, description="Undocumented API exception."),

    # Continue from here, group by subdomains
    JWTAPIException: ExceptionDescription(code=31000, description="JWT API exception."),
    TokenIsNotPresented: ExceptionDescription(
        code=31001,
        description="Token header is not presented. Please add Authorization header to your request."
    ),
    InvalidHeaderFormat: ExceptionDescription(
        code=31002,
        description="Invalid header format. The proper format is 'Bearer {your_token}'"
    ),
    TokenIsExpired: ExceptionDescription(
        code=31003,
        description="Token is expired. Please re-login and try again."
    ),
    TokenIsInvalid: ExceptionDescription(
        code=31004,
        description="Token is invalid. Please re-login and try again."
    )
}
