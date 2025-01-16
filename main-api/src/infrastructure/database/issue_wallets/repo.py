from uuid import UUID

from sqlalchemy import select

from .dtos import IssueLightningWalletDTO
from .table import IssueLightningWalletDbModel
from .._abstract.repo import SQLAAbstractRepo


class IssueLightningWalletRepo(SQLAAbstractRepo):

    async def create_wallet(self, wallet_dto: IssueLightningWalletDTO) -> IssueLightningWalletDbModel:
        new_wallet = IssueLightningWalletDbModel(**wallet_dto.model_dump())
        self._session.add(new_wallet)

        # TODO: Add logging

        return new_wallet

    async def get_wallet_by_id(self, wallet_id: UUID) -> IssueLightningWalletDbModel | None:
        return await self._session.scalar(
            select(IssueLightningWalletDbModel).where(IssueLightningWalletDbModel.id == wallet_id)
        )

    async def get_wallet_by_issue_id(self, issue_id: UUID) -> IssueLightningWalletDbModel | None:
        return await self._session.scalar(
            select(IssueLightningWalletDbModel).where(IssueLightningWalletDbModel.issue_id == issue_id)
        )
