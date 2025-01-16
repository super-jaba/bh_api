from domain.common.exceptions import DomainException


class RepositoryException(DomainException):
    """Base class for repository exceptions"""
    pass


class RepositoryNotFound(RepositoryException):
    pass
