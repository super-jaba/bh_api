from abc import ABC, abstractmethod
from uuid import UUID

from .schemas import WalletDetailSchema, LightningTransactionSchema, InvoiceCreationSchema
from ..common.schemas import PaginationSchema


class WalletServiceABC(ABC):

    @abstractmethod
    async def create_wallet(self, user_id: UUID) -> WalletDetailSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_wallet(self, user_id: UUID) -> WalletDetailSchema:
        """
        Returns wallet details of the user specified.
        If no wallet found, raises **WalletNotFound**.
        :param user_id: Internal ID of the user
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def get_or_create_wallet(self, user_id: UUID) -> WalletDetailSchema:
        """
        Fetches the wallet details of the user specified.
        If no wallet found, creates a new wallet for the user.
        :param user_id: Internal ID of the user
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def create_incoming_invoice(self, wallet_owner_id: UUID, amount_sats: int) -> InvoiceCreationSchema:
        """
        Creates an incoming invoice for the wallet.
        :param wallet_owner_id: The user ID associated with the wallet to send funds to.
        :param amount_sats: Amount of satoshis to be deposited
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def pay_invoice(self, payer_id: UUID, invoice: str) -> None:
        """
        Pays the other wallet invoice.
        :param payer_id: The user ID associated with the wallet to send funds from.
        :param invoice: Invoice string to pay
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def get_wallet_history(
        self,
        user_id: UUID,
        pagination: PaginationSchema
    ) -> list[LightningTransactionSchema]:
        raise NotImplementedError
