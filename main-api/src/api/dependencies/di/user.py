from fastapi import FastAPI

from domain.users import UserServiceABC
from impl.users import UserService


def get_service() -> UserServiceABC:
    return UserService()


def di_user(app: FastAPI) -> None:
    app.dependency_overrides[UserServiceABC] = get_service
