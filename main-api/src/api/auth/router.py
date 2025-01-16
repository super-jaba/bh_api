from fastapi import APIRouter, status, Query
from starlette.responses import RedirectResponse

from infrastructure.github.exceptions import LoginFailed, CouldNotFetchGithubUser
from infrastructure.github import GithubAuthClient, GithubAPIClient

from .schemas import TokenResponse
from .utils import get_registered_user
from ..common.jwt import JWTService, GetAccessTokenSchema
from ..dependencies.types import UserServiceDep
from ..exceptions.http import UnauthorizedException, ServerErrorException
from ..exceptions.schemas import HTTPExceptionDetailSchema


router = APIRouter(tags=["Auth"])


@router.get(
    "/github",
    status_code=status.HTTP_308_PERMANENT_REDIRECT
)
async def github_auth(
    redirect_uri: str | None = Query(None)
):
    return RedirectResponse(GithubAuthClient.get_auth_link(redirect_uri))


@router.get(
    "/github/callback",
    response_model=TokenResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema}
    }
)
async def github_callback(
    user_service: UserServiceDep,
    code: str = Query()
):
    try:
        github_auth_token = await GithubAuthClient.get_auth_token(code)
    except LoginFailed as login_failed:
        return UnauthorizedException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(login_failed)
        )

    try:
        github_user = await GithubAPIClient(github_auth_token).get_authenticated_user()
    except CouldNotFetchGithubUser as could_not_fetch_user:
        return ServerErrorException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(could_not_fetch_user)
        )

    registered_user = await get_registered_user(user_service, github_user)

    return TokenResponse(
        access_token=JWTService.get_access_token(
            GetAccessTokenSchema(
                user_id=registered_user.id,
                github_username=registered_user.github_username,
                github_token=github_auth_token
            )
        )
    )
