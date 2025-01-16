from ..common.exceptions import DomainException


class WalletException(DomainException):
    """Base class for wallet exceptions"""


class CouldNotCreateWallet(WalletException):
    pass


class WalletNotFound(WalletException):
    pass


class CouldNotCreateInvoice(WalletException):
    pass


class CouldNotPayInvoice(WalletException):
    pass


class InsufficientFunds(WalletException):
    pass


# No need to add InvoiceIsAlready paid since it's not specific to the domain but only to Lightning
