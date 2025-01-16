from fastapi import FastAPI

from domain.repositories import RepositoryServiceABC
from impl.repositories import RepositoryService


def get_service() -> RepositoryServiceABC:
    return RepositoryService()


def di_repository(app: FastAPI) -> None:
    app.dependency_overrides[RepositoryServiceABC] = get_service
