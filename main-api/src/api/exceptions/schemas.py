from typing import TypeVar

from pydantic import BaseModel, Field

from domain.common.exceptions import DomainException
from impl.common.exceptions import ImplException
from infrastructure.common.exceptions import InfrastructureException

from .exception_codes import DOMAIN_EXCEPTION_MAPPING, IMPL_EXCEPTION_MAPPING, API_EXCEPTION_MAPPING, \
    INFRASTRUCTURE_EXCEPTION_MAPPING
from .base import APIException

DerivedFromDomainException = TypeVar("DerivedFromDomainException", bound=DomainException)
DerivedFromImplException = TypeVar("DerivedFromImplException", bound=ImplException)
DerivedFromInfrastructureException = TypeVar("DerivedFromInfrastructureException", bound=InfrastructureException)
DerivedFromAPIException = TypeVar("DerivedFromAPIException", bound=APIException)


class HTTPExceptionDetailSchema(BaseModel):
    error_code: int | None = Field(None)
    message: str | None = Field(None)

    @staticmethod
    def from_standard_exception(
        exc: (DerivedFromImplException
              | DerivedFromImplException
              | DerivedFromAPIException
              | DerivedFromInfrastructureException)
    ) -> "HTTPExceptionDetailSchema":
        exception_description = None
        exc_type = type(exc)
        if issubclass(exc_type, DomainException):
            exception_description = DOMAIN_EXCEPTION_MAPPING.get(exc_type)
        elif issubclass(exc_type, ImplException):
            exception_description = IMPL_EXCEPTION_MAPPING.get(exc_type)
        elif issubclass(exc_type, InfrastructureException):
            exception_description = INFRASTRUCTURE_EXCEPTION_MAPPING.get(exc_type)
        elif issubclass(exc_type, APIException):
            exception_description = API_EXCEPTION_MAPPING.get(exc_type)

        if exception_description is not None:
            return HTTPExceptionDetailSchema(
                error_code=exception_description.code,
                message=exception_description.description
            )

        # TODO: Log undocumented exception
        return HTTPExceptionDetailSchema(
            error_code=0,
            message="Undocumented exception."
        )
