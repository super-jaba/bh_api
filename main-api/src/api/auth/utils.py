from domain.users import UserServiceABC
from domain.users.schemas import UserSchema, UpdateUserSchema, CreateUserSchema
from infrastructure.github.schemas import GithubUserSchema


def get_user_difference(github_user: GithubUserSchema, registered_user: UserSchema) -> UpdateUserSchema | None:
    # Avatar is not considered as a difference because it can be different in the user's profile
    if github_user.login != registered_user.github_username:
        return UpdateUserSchema(github_username=github_user.login)


async def get_registered_user(user_service: UserServiceABC, github_user: GithubUserSchema) -> UserSchema:
    registered_user = await user_service.get_by_github_id_or_create(
        github_user.id,
        schema=CreateUserSchema(
            github_id=github_user.id,
            github_username=github_user.login,
            avatar_url=github_user.avatar_url
        )
    )

    differences = get_user_difference(github_user, registered_user)
    if differences:
        registered_user = await user_service.update_user(registered_user.id, differences)

    return registered_user
