from uuid import UUID

from domain.common.schemas import PaginationSchema
from domain.repositories import RepositoryServiceABC
from domain.repositories.exceptions import RepositoryNotFound
from domain.repositories.schemas import RepositorySchema

from infrastructure.database import SessionScope
from infrastructure.database._abstract.dtos import Pagination
from infrastructure.database.repositories import RepositoryRepo


class RepositoryService(RepositoryServiceABC):

    async def get_repository_by_id(self, repository_id: UUID) -> RepositorySchema:
        async with SessionScope.get_session() as session:
            found = await RepositoryRepo(session).get_repository_by_id(repository_id)
            if not found:
                raise RepositoryNotFound
            return RepositorySchema.model_validate(found)
        
    async def list_repositories(self, pagination: PaginationSchema) -> list[RepositorySchema]:
        async with SessionScope.get_session() as session:
            return [
                RepositorySchema.model_validate(repo)
                for repo in await RepositoryRepo(session).list_repositories(
                    pagination=Pagination(
                        skip=pagination.skip,
                        limit=pagination.limit
                    )
                )
            ]
        
    async def count_repositories(self) -> int:
        async with SessionScope.get_session() as session:
            return await RepositoryRepo(session).count_repositories()
