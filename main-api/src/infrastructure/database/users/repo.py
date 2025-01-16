import logging
from uuid import UUID

from sqlalchemy import select, update

from .dtos import UpdateUserDTO, CreateUserDTO
from .table import UserDbModel
from .._abstract.dtos import Pagination
from .._abstract.repo import SQLAAbstractRepo


class UserRepo(SQLAAbstractRepo):

    async def create_user(self, user_dto: CreateUserDTO) -> UserDbModel:
        logging.debug(f"Start creating new issue with data: {user_dto.model_dump()}")
        new_user_obj = UserDbModel(**user_dto.model_dump())
        logging.debug(f"New user created: {new_user_obj}")
        self._session.add(new_user_obj)
        return new_user_obj

    async def get_user_by_id(self, user_id: UUID) -> UserDbModel | None:
        return await self._session.scalar(
            select(UserDbModel).where(UserDbModel.id == user_id)
        )

    async def get_user_by_github_id(self, github_id: int) -> UserDbModel | None:
        return await self._session.scalar(
            select(UserDbModel).where(UserDbModel.github_id == github_id)
        )

    async def get_user_by_github_id_or_create(
        self,
        github_id: int,
        user_dto: CreateUserDTO
    ) -> UserDbModel:
        fetched_user = await self.get_user_by_github_id(github_id)
        if fetched_user is None:
            fetched_user = await self.create_user(user_dto)
        return fetched_user

    async def get_user_by_username(self, username: str) -> UserDbModel | None:
        return await self._session.scalar(
            select(UserDbModel).where(UserDbModel.github_username == username)
        )

    async def list_users(self, pagination: Pagination | None = None) -> list[UserDbModel]:
        stmt = self._apply_pagination(
            select(UserDbModel),
            pagination
        )
        return await self._session.scalars(stmt)

    async def update_user(self, user_id: UUID, update_fields: UpdateUserDTO) -> UserDbModel | None:
        logging.debug(
            f"Start updating user {user_id}, new fields: {update_fields.model_dump(exclude_unset=True)}"
        )
        stmt = update(
            UserDbModel
        ).where(
            UserDbModel.id == user_id
        ).values(
            **update_fields.model_dump(exclude_unset=True)
        ).returning(UserDbModel)
        logging.debug(f"Updated user created")
        return await self._session.scalar(stmt)
