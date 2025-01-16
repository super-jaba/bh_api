from domain.common.exceptions import DomainException


class IssueException(DomainException):
    """Base class for issue exceptions"""
    pass


class IssueNotFound(IssueException):
    pass
