from domain.common.exceptions import DomainException


class RewardException(DomainException):
    """Base class for reward exceptions"""
    pass


class RewardNotFound(RewardException):
    pass


class NothingToRewardFor(RewardException):
    pass


class IssueDoesNotExist(RewardException):
    pass


class IssueIsClosed(RewardException):
    pass
