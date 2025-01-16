from uuid import UUID

from domain.users import UserServiceABC
from domain.users.exceptions import UserNotFound
from domain.users.schemas import (
    UserSchema,
    CreateUserSchema,
    UpdateUserSchema
)
from infrastructure.database import SessionScope
from infrastructure.database.users import UserRepo, UserDbModel
from infrastructure.database.users.dtos import CreateUserDTO, UpdateUserDTO


class UserService(UserServiceABC):
    """
    User service implements user operations done under a single transaction.
    Adjacent operations (logging, notifications, exception handling etc.) happen in wrapper functions
    """

    async def create_user(
        self,
        schema: CreateUserSchema
    ) -> UserSchema:
        async with SessionScope.get_session() as session:
            # TODO: Handle constraint exceptions
            new_user = await UserRepo(session).create_user(CreateUserDTO(**schema.model_dump(exclude_unset=True)))
            await session.commit()
            return UserSchema.model_validate(new_user)

    async def get_user_by_id(self, user_id: UUID) -> UserSchema:
        async with SessionScope.get_session() as session:
            fetched_user = await UserRepo(session).get_user_by_id(user_id)
            return self._validate_user(fetched_user)

    async def get_user_by_github_id(self, github_id: int) -> UserSchema:
        async with SessionScope.get_session() as session:
            fetched_user = await UserRepo(session).get_user_by_github_id(github_id)
            return self._validate_user(fetched_user)

    async def get_user_by_username(self, username: str) -> UserSchema:
        async with SessionScope.get_session() as session:
            fetched_user = await UserRepo(session).get_user_by_username(username)
            return self._validate_user(fetched_user)

    async def get_by_github_id_or_create(self, github_id: int, schema: CreateUserSchema) -> UserSchema:
        try:
            return await self.get_user_by_github_id(github_id)
        except UserNotFound:
            return await self.create_user(schema)

    async def update_user(self, user_id: UUID, schema: UpdateUserSchema) -> UserSchema:
        async with SessionScope.get_session() as session:
            updated_user = await UserRepo(session).update_user(user_id, UpdateUserDTO(**schema.model_dump()))
            await session.commit()
            return self._validate_user(updated_user)

    # UsersService._validate_user is specific only to this implementation
    # So no need to put it in the domain
    def _validate_user(self, user: UserDbModel | None) -> UserSchema:
        if user is None:
            raise UserNotFound
        return UserSchema.model_validate(user)
