from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError

from domain.users import UserServiceABC
from domain.users.exceptions import UserNotFound
from domain.users.schemas import UserSchema
from infrastructure.github import GithubAPIClient
from ..common.jwt import JWTService, AccessTokenPayloadSchema
from ..common.jwt.exceptions import (
    JWTAPIException,
    TokenIsNotPresented,
    InvalidHeaderFormat,
    TokenIsExpired,
    TokenIsInvalid
)
from ..exceptions.http import UnauthorizedException
from ..exceptions.schemas import HTTPExceptionDetailSchema


def get_jwt_token(authorization: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())] = None) -> str:
    try:
        if not authorization:
            raise TokenIsNotPresented

        try:
            return authorization.credentials
        except IndexError:
            raise InvalidHeaderFormat
    except JWTAPIException as jwt_exception:
        raise UnauthorizedException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(jwt_exception)
        )


def get_jwt_payload(token: Annotated[str, Depends(get_jwt_token)]) -> AccessTokenPayloadSchema:
    try:
        try:
            return JWTService.parse_access_token(token)
        except ExpiredSignatureError:
            raise TokenIsExpired
        except JWTError:
            raise TokenIsInvalid
    except JWTAPIException as jwt_exception:
        raise UnauthorizedException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(jwt_exception)
        )


async def get_authenticated_user(
    user_service: Annotated[UserServiceABC, Depends()],
    jwt_payload: Annotated[AccessTokenPayloadSchema, Depends(get_jwt_payload)]
) -> UserSchema:
    try:
        return await user_service.get_user_by_id(UUID(jwt_payload.user_id))
    except UserNotFound as user_not_found:
        raise UnauthorizedException(detail=HTTPExceptionDetailSchema.from_standard_exception(user_not_found))


def get_github_api_service(
    payload: Annotated[AccessTokenPayloadSchema, Depends(get_jwt_payload)],
) -> GithubAPIClient:
    return GithubAPIClient(payload.github_token)
