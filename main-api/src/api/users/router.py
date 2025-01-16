from uuid import UUID

from fastapi import APIRouter, status, Query

from domain.users.exceptions import UserNotFound
from domain.users.schemas import UserSchema

from ..dependencies.types import GetAuthenticatedUserDep, UserServiceDep
from ..exceptions.http import NotFoundException, BadRequestException
from ..exceptions.schemas import HTTPExceptionDetailSchema


router = APIRouter(tags=["Users"])


@router.get(
    "/me",
    response_model=UserSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_authenticated_user(
    user: GetAuthenticatedUserDep
):
    return user


@router.get(
    "/",
    response_model=UserSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_user(
    user_service: UserServiceDep,
    user_id: UUID | None = Query(None),
    username: str | None = Query(None)
):
    """
    Fetches a user by its ID or GitHub username.

    Throws
    - **400** if none parameters were provided.
    - **404** if the user does not exist.
    """

    if not any([user_id, username]):
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema(
                error_code=1,
                message="Neither user_id nor username was provided."
            )
        )

    try:
        if user_id is not None:
            return await user_service.get_user_by_id(user_id)
        return await user_service.get_user_by_username(username)
    except UserNotFound as user_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(user_not_found)
        )
