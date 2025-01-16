from abc import ABC, abstractmethod
from uuid import UUID

from domain.common.schemas import PaginationSchema

from .schemas import RepositorySchema


class RepositoryServiceABC(ABC):

    @abstractmethod
    async def get_repository_by_id(
        self,
        repository_id: UUID
    ) -> RepositorySchema:
        raise NotImplementedError

    @abstractmethod
    async def list_repositories(
        self,
        pagination: PaginationSchema
    ) -> list[RepositorySchema]:
        raise NotImplementedError
    
    @abstractmethod
    async def count_repositories(self) -> int:
        raise NotImplementedError
