import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, Select, func, text

from .._abstract.dtos import Pagination
from .._abstract.repo import SQLAAbstractRepo
from .table import RewardDbModel
from .dtos import (
    CreateRewardDto,
    RewardFiltersDto,
    ExpandedRewardDto
)
from ..issues import IssueDbModel
from ..users import UserDbModel


class RewardRepo(SQLAAbstractRepo):

    def _parse_row(self, row: Any) -> ExpandedRewardDto | None:
        if row is not None:
            return ExpandedRewardDto(
                reward=row[0],
                rewarder=row[1],
                issue=row[2]
            )

    def _apply_filters(self, stmt: Select, filters: RewardFiltersDto) -> Select:
        if filters.issue_id is not None:
            stmt = stmt.where(RewardDbModel.issue_id == filters.issue_id)
        if filters.is_closed is not None:
            stmt = stmt.join(
                IssueDbModel,
                RewardDbModel.issue_id == IssueDbModel.id
            ).where(IssueDbModel.is_closed == filters.is_closed)
        if filters.rewarder_id is not None:
            stmt = stmt.where(RewardDbModel.rewarder_id == filters.rewarder_id)

        return stmt

    async def create_reward(self, reward_dto: CreateRewardDto) -> RewardDbModel:
        new_reward = RewardDbModel(**reward_dto.model_dump())
        self._session.add(new_reward)
        logging.debug(f"New reward created: {new_reward}")
        return new_reward

    async def get_reward(self, reward_id: UUID) -> RewardDbModel | None:
        return await self._session.scalar(
            select(RewardDbModel).where(RewardDbModel.id == reward_id)
        )

    async def get_reward_expanded(self, reward_id: UUID) -> ExpandedRewardDto | None:
        stmt = select(
            RewardDbModel,
            UserDbModel,
            IssueDbModel
        ).join(
            UserDbModel,
            RewardDbModel.rewarder_id == UserDbModel.id
        ).join(
            IssueDbModel,
            RewardDbModel.issue_id == IssueDbModel.id
        ).where(RewardDbModel.id == reward_id)

        return self._parse_row(
            (await self._session.execute(stmt)).first()
        )

    async def list_rewards(
        self,
        pagination: Pagination | None = None,
        filters: RewardFiltersDto | None = None
    ) -> list[RewardDbModel]:
        stmt = self._apply_pagination(
            select(RewardDbModel),
            pagination
        )

        if filters is not None:
            stmt = self._apply_filters(stmt, filters)

        return await self._session.scalars(stmt)

    async def list_rewards_expanded(
        self,
        pagination: Pagination | None = None,
        filters: RewardFiltersDto | None = None
    ) -> list[ExpandedRewardDto]:
        stmt = select(
            RewardDbModel,
            UserDbModel,
            IssueDbModel
        ).join(
            UserDbModel,
            RewardDbModel.rewarder_id == UserDbModel.id
        ).join(
            IssueDbModel,
            RewardDbModel.issue_id == IssueDbModel.id
        )

        stmt = self._apply_pagination(stmt, pagination)

        if filters is not None:
            stmt = self._apply_filters(stmt, filters)

        return [
            self._parse_row(row)
            for row in (await self._session.execute(stmt)).all()
        ]

    async def count_rewards(
        self,
        filters: RewardFiltersDto | None = None
    ) -> int:
        """
        Counts the number of rewards satisfying the filters if passed
        :param filters:
        :return: int
        """
        stmt = select(func.count(RewardDbModel.id))
        if filters is not None:
            stmt = self._apply_filters(stmt, filters)
        return await self._session.scalar(stmt)

    async def calculate_total_reward(
        self,
        filters: RewardFiltersDto | None = None
    ) -> int:
        stmt = self._apply_filters(
            select(func.sum(RewardDbModel.reward_sats)),
            filters
        )

        result = await self._session.scalar(stmt)
        return int(result) if result is not None else 0

    async def lock_exclusively(self) -> None:
        await self._session.execute(text(f"LOCK TABLE {RewardDbModel.__tablename__} IN EXCLUSIVE MODE"))

    async def lock_in_share_mode(self) -> None:
        await self._session.execute(text(f"LOCK TABLE {RewardDbModel.__tablename__} IN SHARE MODE"))
