from uuid import UUID

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from domain.common.schemas import PaginationSchema
from domain.wallet import WalletServiceABC
from domain.wallet.exceptions import (
    CouldNotCreateWallet,
    WalletNotFound,
    CouldNotCreateInvoice,
    InsufficientFunds,
    CouldNotPayInvoice
)
from domain.wallet.schemas import WalletDetailSchema, LightningTransactionSchema, InvoiceCreationSchema
from infrastructure.database import SessionScope
from infrastructure.database.lightning_wallet import LightningWalletRepo, LightningWalletDbModel
from infrastructure.database.lightning_wallet.dtos import LightningWalletDTO
from infrastructure.lnbits import LNBitsClient
from infrastructure.branta import BrantaClient

from infrastructure.lnbits.exceptions import (
    WalletCreationFailure,
    WalletFetchFailure,
    WalletAPIException,
    NotEnoughSats,
    PayInvoiceFailure
)


class WalletService(WalletServiceABC):

    async def _create_wallet(
            self,
            session: AsyncSession,
            user_id: UUID
    ) -> WalletDetailSchema:
        try:
            wallet_from_api = await LNBitsClient().create_headless_wallet(user_id.hex)
        except WalletCreationFailure:
            raise CouldNotCreateWallet

        saved_details = await LightningWalletRepo(session).create_wallet(
            LightningWalletDTO(
                user_id=user_id,
                wallet_id=wallet_from_api.id,
                adminkey=wallet_from_api.adminkey,
                inkey=wallet_from_api.inkey
            )
        )

        await session.commit()

        # If it's just created, no need to fetch its balance
        return WalletDetailSchema(
            user_id=user_id,
            total_sats=0
        )

    async def _get_wallet(self, session: AsyncSession, user_id: UUID) -> LightningWalletDbModel:
        """
        Fetches wallet on under-transaction level

        Throws **WalletNotFound** if wallet not found.
        :param session:
        :param user_id:
        :return:
        """
        fetched_wallet = await LightningWalletRepo(session).get_wallet_by_user_id(user_id)
        if fetched_wallet is None:
            raise WalletNotFound
        return fetched_wallet

    async def _get_wallet_details(
            self,
            wallet_model: LightningWalletDbModel,
    ) -> WalletDetailSchema:
        """
        Calculates the total and the reserved balance of the wallet passed.
        :param wallet_model: The wallet object used to query the wallet API to get the total balance
        :param session: Database session used to calculate the amount of reserved funds
        :return: WalletDetailSchema
        """
        try:
            wallet_api_details = await LNBitsClient().get_wallet(wallet_model.inkey)
        except WalletFetchFailure:
            raise WalletNotFound

        return WalletDetailSchema(
            user_id=wallet_model.user_id,
            total_sats=wallet_api_details.balance / 1000,
        )

    async def _get_requested_amount(self, invoice: str) -> float:
        return (await LNBitsClient().decode_invoice(invoice)).amount_msat / 1000

    async def create_wallet(self, user_id: UUID) -> WalletDetailSchema:
        async with SessionScope.get_session() as session:
            return await self._create_wallet(session, user_id)

    async def get_wallet(self, user_id: UUID) -> WalletDetailSchema:
        async with SessionScope.get_session() as session:
            fetched_wallet = await self._get_wallet(session, user_id)
            return await self._get_wallet_details(fetched_wallet)

    async def get_or_create_wallet(self, user_id: UUID) -> WalletDetailSchema:
        async with SessionScope.get_session() as session:
            wallet_repo = LightningWalletRepo(session)
            wallet = await wallet_repo.get_wallet_by_user_id(user_id)
            if wallet is None:
                return await self._create_wallet(session, user_id)

            return await self._get_wallet_details(wallet)

    async def create_incoming_invoice(self, wallet_owner_id: UUID, amount_sats: int) -> InvoiceCreationSchema:
        # No need to lock DB for deposits
        async with SessionScope.get_session() as session:
            wallet = await self._get_wallet(session, wallet_owner_id)

            try:
                invoice = await LNBitsClient().create_invoice(
                    inkey=wallet.inkey,
                    amount_sats=amount_sats
                )
            except WalletAPIException:
                raise CouldNotCreateInvoice
            
            asyncio.create_task(BrantaClient().verify_invoice(invoice.invoice))
            
            return invoice

    async def pay_invoice(self, payer_id: UUID, invoice: str) -> None:
        async with SessionScope.get_session() as session:

            payer_wallet = await self._get_wallet(session, payer_id)
            try:
                await LNBitsClient().pay_invoice(
                    adminkey=payer_wallet.adminkey,
                    invoice=invoice
                )
            except NotEnoughSats:
                raise InsufficientFunds
            except PayInvoiceFailure:
                raise CouldNotPayInvoice

    async def get_wallet_history(
        self,
        user_id: UUID,
        pagination: PaginationSchema
    ) -> list[LightningTransactionSchema]:
        async with SessionScope.get_session() as session:
            wallet = await self._get_wallet(session, user_id)
            return await LNBitsClient().get_wallet_history(wallet.inkey, pagination)
