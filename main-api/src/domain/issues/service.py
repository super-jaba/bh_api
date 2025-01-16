from abc import ABC, abstractmethod
from uuid import UUID

from domain.common.schemas import PaginationSchema

from .schemas import IssueSchema, IssueFiltersSchema, IssueExpandedSchema


class IssueServiceABC(ABC):

    @abstractmethod
    async def list_issues(
        self,
        pagination: PaginationSchema,
        filters: IssueFiltersSchema | None = None
    ) -> list[IssueSchema]:
        raise NotImplementedError

    @abstractmethod
    async def list_issues_expanded(
        self,
        pagination: PaginationSchema,
        filters: IssueFiltersSchema | None = None
    ) -> list[IssueExpandedSchema]:
        raise NotImplementedError

    @abstractmethod
    async def count_issues(
        self,
        filters: IssueFiltersSchema | None = None
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_issue_by_id(self, issue_id: UUID) -> IssueSchema:
        """
        Fetches an issue by its ID. Throws **IssueNotFound** if no issue found.
        :param issue_id: The ID of the issue.
        :return: IssueSchema
        """
        raise NotImplementedError

    @abstractmethod
    async def get_issue_by_id_expanded(self, issue_id: UUID) -> IssueExpandedSchema:
        """
        Fetches an issue by its ID. Throws **IssueNotFound** if no issue found.
        :param issue_id:
        :return: IssueSchema
        """
        raise NotImplementedError
