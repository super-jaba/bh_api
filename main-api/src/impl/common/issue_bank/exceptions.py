from ..exceptions import ImplException


class IssueBankException(ImplException):
    """Base class for IssueBank exceptions."""


class IssueWalletNotFound(IssueBankException):
    pass
