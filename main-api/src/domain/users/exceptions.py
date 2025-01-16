from domain.common.exceptions import DomainException


class UserException(DomainException):
    """Base User exception class"""


class UserNotFound(UserException):
    pass
