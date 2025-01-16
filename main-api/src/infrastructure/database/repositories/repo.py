import logging

from uuid import UUID
from sqlalchemy import func, select, update

from .._abstract.repo import SQLAAbstractRepo
from .._abstract.dtos import Pagination
from .table import RepositoryDbModel
from .dto import CreateRepositoryDto, UpdateRepositoryDto


class RepositoryRepo(SQLAAbstractRepo):
    async def create_repository(self, repository_dto: CreateRepositoryDto) -> RepositoryDbModel:
        new_repository = RepositoryDbModel(**repository_dto.model_dump())
        self._session.add(new_repository)
        logging.debug(f"New repository created: {new_repository}")
        return new_repository

    async def get_repository_by_id(self, repository_id: UUID) -> RepositoryDbModel:
        return await self._session.scalar(
            select(RepositoryDbModel).where(RepositoryDbModel.id == repository_id)
        )

    async def get_repository_by_github_id(self, repository_github_id: int) -> RepositoryDbModel:
        return await self._session.scalar(
            select(RepositoryDbModel).where(RepositoryDbModel.github_id == repository_github_id)
        )

    async def get_repository_by_fullname(self, repository_fullname: str) -> RepositoryDbModel:
        return await self._session.scalar(
            select(RepositoryDbModel).where(RepositoryDbModel.full_name == repository_fullname)
        )

    async def get_or_create(self, repository_dto: CreateRepositoryDto) -> tuple[RepositoryDbModel, bool]:
        """
        Fetches a repository by its GitHub ID or creates a new one if not found.
        :param repository_dto: DTO to create the repository if not found.
        :return: Repository, [True if the repo was created, False otherwise].
        """

        repo_was_created = False
        repository = await self.get_repository_by_github_id(repository_dto.github_id)
        if repository is None:
            repository = await self.create_repository(repository_dto)
            repo_was_created = True
        return repository, repo_was_created

    async def get_update_or_create_repository(
        self,
        repository_dto: CreateRepositoryDto
    ) -> tuple[RepositoryDbModel, bool, bool]:
        """
        Fetches a repository by its GitHub ID, updates it if there are differences from the expected values,
        or creates a new one if it is not found.

        :param repository_dto: Data Transfer Object containing repository details.
        :return: A tuple containing:
            - RepositoryDbModel: The repository model (updated or newly created).
            - bool #1: True if the repository was created, False otherwise.
            - bool #2: True if the repository was updated, False otherwise.
        """

        repository, created = await self.get_or_create(repository_dto)
        if created:
            return repository, created, False

        updated = False
        if self._repository_has_differences(repository, repository_dto):
            repository = await self.update_repository(
                repository_id=repository.id,
                update_fields=UpdateRepositoryDto(
                    fullname=repository_dto.full_name,
                    owner_github_id=repository_dto.owner_github_id,
                    html_url=repository_dto.html_url
                )
            )
            updated = True

        return repository, created, updated

    def _repository_has_differences(self, repository: RepositoryDbModel, repository_dto: CreateRepositoryDto) -> bool:
        """
        Checks if there are differences between the existing repository and the provided DTO.

        :param repository: The existing repository.
        :param repository_dto: The Data Transfer Object containing the expected repository details.
        :return: True if there are differences, False otherwise.
        """
        return (
            repository.full_name != repository_dto.full_name
            or repository.owner_github_id != repository_dto.owner_github_id
            or repository.html_url != repository_dto.html_url
        )

    async def list_repositories(
        self,
        pagination: Pagination | None = None,
        owner_github_id: int | None = None
    ) -> list[RepositoryDbModel]:
        stmt = self._apply_pagination(
            select(RepositoryDbModel),
            pagination
        )

        if owner_github_id is not None:
            stmt = stmt.where(RepositoryDbModel.owner_github_id == owner_github_id)

        return await self._session.scalars(stmt)
    
    async def count_repositories(
        self
    ) -> int:
        return await self._session.scalar(
            select(func.count(RepositoryDbModel.id))
        )

    async def update_repository(self, repository_id: UUID, update_fields: UpdateRepositoryDto) -> RepositoryDbModel:
        stmt = update(
            RepositoryDbModel
        ).where(
            RepositoryDbModel.id == repository_id
        ).values(
            **update_fields.model_dump(exclude_unset=True)
        ).returning(RepositoryDbModel)
        logging.debug(f"Repository updated with fields: {update_fields.model_dump(exclude_unset=True)}")
        return await self._session.scalar(stmt)
