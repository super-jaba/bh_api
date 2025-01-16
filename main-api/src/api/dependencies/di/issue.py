from fastapi import FastAPI

from domain.issues import IssueServiceABC
from impl.issues import IssueService


def get_service() -> IssueServiceABC:
    return IssueService()


def di_issue(app: FastAPI) -> None:
    app.dependency_overrides[IssueServiceABC] = get_service
