from fastapi import FastAPI

from .issue import di_issue
from .repository import di_repository
from .reward import di_reward
from .user import di_user
from .wallet import di_wallet


def setup_dependencies(app: FastAPI) -> None:
    di_user(app)
    di_wallet(app)
    di_issue(app)
    di_repository(app)
    di_reward(app)
