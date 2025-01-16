from infrastructure.common.exceptions import InfrastructureException


class WalletAPIException(InfrastructureException):
    """Base class for exceptions related to the wallet API"""
    pass


class AccountCreationFailure(WalletAPIException):
    pass


class WalletCreationFailure(WalletAPIException):
    pass


class WalletFetchFailure(WalletAPIException):
    pass


class CreateInvoiceFailure(WalletAPIException):
    pass


class BadResponseBody(WalletAPIException):
    pass


class PayInvoiceFailure(WalletAPIException):
    pass


class NotEnoughSats(WalletAPIException):
    pass


class InvoiceIsAlreadyPaid(WalletAPIException):
    pass


class CouldNotDecodeInvoiceException(WalletAPIException):
    pass


class LNBitsTransactionFailure(WalletAPIException):
    """
    Composite exception raised when there is
    either **CreateInvoiceFailure** or **PayInvoiceFailure**
    """
