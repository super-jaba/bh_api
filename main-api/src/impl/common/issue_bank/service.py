from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.wallet.exceptions import WalletNotFound
from infrastructure.database.issue_wallets import IssueLightningWalletDbModel, IssueLightningWalletRepo
from infrastructure.database.issue_wallets.dtos import IssueLightningWalletDTO
from infrastructure.database.lightning_wallet import LightningWalletDbModel, LightningWalletRepo
from infrastructure.lnbits import LNBitsClient

from .exceptions import IssueWalletNotFound


class IssueBank:

    def __init__(
        self,
        session: AsyncSession
    ):
        self._session = session

    async def _create_new_issue_wallet(
        self,
        issue_id: UUID
    ) -> IssueLightningWalletDbModel:
        lnbits_wallet = await LNBitsClient().create_headless_wallet(
            name=issue_id.hex
        )
        return await IssueLightningWalletRepo(self._session).create_wallet(
            IssueLightningWalletDTO(
                issue_id=issue_id,
                wallet_id=lnbits_wallet.id,
                adminkey=lnbits_wallet.adminkey,
                inkey=lnbits_wallet.inkey
            )
        )

    async def _get_issue_wallet(self, issue_id: UUID) -> IssueLightningWalletDbModel | None:
        wallet = await IssueLightningWalletRepo(self._session).get_wallet_by_issue_id(issue_id)
        if wallet is None:
            raise IssueWalletNotFound
        return wallet

    async def _get_or_create_issue_wallet(self, issue_id: UUID) -> IssueLightningWalletDbModel:
        try:
            wallet = await self._get_issue_wallet(issue_id)
        except IssueWalletNotFound:
            wallet = await self._create_new_issue_wallet(issue_id)
        return wallet

    async def _get_user_wallet(self, user_id: UUID) -> LightningWalletDbModel:
        wallet = await LightningWalletRepo(self._session).get_wallet_by_user_id(user_id)
        if wallet is None:
            raise WalletNotFound
        return wallet

    async def reserve_sats(
        self,
        from_user_id: UUID,
        to_issue_id: UUID,
        amount: int
    ) -> None:
        user_wallet = await self._get_user_wallet(from_user_id)
        issue_wallet = await self._get_or_create_issue_wallet(to_issue_id)

        await LNBitsClient().move_sats(
            from_wallet_adminkey=user_wallet.adminkey,
            to_wallet_inkey=issue_wallet.inkey,
            amount=amount
        )

    async def reward_user(
        self,
        user_id: UUID,
        for_issue_id: UUID
    ) -> int:
        """
        Moves sats from issue bank to a specific user.
        :param user_id:
        :param for_issue_id:
        :return: The amount of sats sent
        """
        user_wallet = await self._get_user_wallet(user_id)
        issue_wallet = await self._get_issue_wallet(issue_id=for_issue_id)

        lnbits_client = LNBitsClient()
        wallet_details = await lnbits_client.get_wallet(issue_wallet.inkey)
        reserved_balance = int(wallet_details.balance / 1000)
        await lnbits_client.move_sats(
            from_wallet_adminkey=issue_wallet.adminkey,
            to_wallet_inkey=user_wallet.inkey,
            amount=reserved_balance
        )

        return reserved_balance
