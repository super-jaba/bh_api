from api.exceptions.base import APIException


class JWTAPIException(APIException):
    """Base class for JWT related exceptions."""


class TokenIsNotPresented(JWTAPIException):
    pass


class InvalidHeaderFormat(JWTAPIException):
    pass


class TokenIsExpired(JWTAPIException):
    pass


class TokenIsInvalid(JWTAPIException):
    pass
