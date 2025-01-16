import logging
from uuid import UUID

from sqlalchemy import select

from . import LightningWalletDbModel
from .._abstract.repo import SQLAAbstractRepo
from .dtos import LightningWalletDTO


class LightningWalletRepo(SQLAAbstractRepo):
    async def create_wallet(self, wallet_dto: LightningWalletDTO) -> LightningWalletDbModel:
        new_wallet = LightningWalletDbModel(**wallet_dto.model_dump())
        self._session.add(new_wallet)
        logging.debug(f"New wallet created: {new_wallet}")
        return new_wallet

    async def get_wallet_by_id(self, wallet_id: UUID) -> LightningWalletDbModel | None:
        return await self._session.scalar(
            select(LightningWalletDbModel).where(LightningWalletDbModel.id == wallet_id)
        )

    async def get_wallet_by_user_id(self, user_id: UUID) -> LightningWalletDbModel | None:
        return await self._session.scalar(
            select(LightningWalletDbModel).where(LightningWalletDbModel.user_id == user_id)
        )

    async def get_wallet_by_user_id_or_create(
        self,
        user_id: UUID,
        wallet_dto: LightningWalletDTO
    ) -> LightningWalletDbModel:
        fetched_wallet = await self.get_wallet_by_user_id(user_id)
        if fetched_wallet is None:
            fetched_wallet = await self.create_wallet(wallet_dto)
        return fetched_wallet
