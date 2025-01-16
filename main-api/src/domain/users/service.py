from abc import ABC, abstractmethod
from uuid import UUID

from domain.users.schemas import (
    CreateUserSchema,
    UserSchema,
    UpdateUserSchema
)


class UserServiceABC(ABC):

    @abstractmethod
    async def create_user(self, schema: CreateUserSchema) -> UserSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> UserSchema:
        """
        Fetches a user by its ID.

        Throws UserNotFound if the user not found.
        :param user_id:
        :return: UserSchema
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_github_id(self, github_id: int) -> UserSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_username(self, username: str) -> UserSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_by_github_id_or_create(self, github_id: int, schema: CreateUserSchema) -> UserSchema:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, user_id: UUID, schema: UpdateUserSchema) -> UserSchema:
        raise NotImplementedError
