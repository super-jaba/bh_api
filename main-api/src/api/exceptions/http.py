from typing import Any

from fastapi import HTTPException, status

from api.exceptions.schemas import HTTPExceptionDetailSchema


class BadRequestException(HTTPException):
    def __init__(
        self,
        detail: HTTPExceptionDetailSchema,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail.dict(), headers)


class UnauthorizedException(HTTPException):
    def __init__(
        self,
        detail: HTTPExceptionDetailSchema,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail.dict(), headers)


class ForbiddenException(HTTPException):
    def __init__(
        self,
        detail: HTTPExceptionDetailSchema,
        status_code: int = status.HTTP_403_FORBIDDEN,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail.dict(), headers)


class NotFoundException(HTTPException):
    def __init__(
        self,
        detail: HTTPExceptionDetailSchema,
        status_code: int = status.HTTP_404_NOT_FOUND,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail.dict(), headers)


class ServerErrorException(HTTPException):
    def __init__(
        self,
        detail: HTTPExceptionDetailSchema,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail.dict(), headers)
