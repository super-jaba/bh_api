from typing import Annotated

from fastapi import Depends

from domain.common.schemas import PaginationSchema
from domain.issues import IssueServiceABC
from domain.repositories.service import RepositoryServiceABC
from domain.rewards import RewardServiceABC
from domain.users import UserServiceABC
from domain.users.schemas import UserSchema
from domain.wallet import WalletServiceABC
from infrastructure.github import GithubAPIClient

from .jwt import get_authenticated_user, get_github_api_service
from .pagination import read_pagination


PaginationDep = Annotated[PaginationSchema, Depends(read_pagination)]

GithubAPIServiceDep = Annotated[GithubAPIClient, Depends(get_github_api_service)]
GetAuthenticatedUserDep = Annotated[UserSchema, Depends(get_authenticated_user)]

UserServiceDep = Annotated[UserServiceABC, Depends()]

WalletServiceDep = Annotated[WalletServiceABC, Depends()]

IssueServiceDep = Annotated[IssueServiceABC, Depends()]

RepositoryServiceDep = Annotated[RepositoryServiceABC, Depends()]

RewardServiceDep = Annotated[RewardServiceABC, Depends()]
