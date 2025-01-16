from abc import ABC, abstractmethod
from uuid import UUID

from .schemas import (
    RewardSchema,
    CreateRewardSchema,
    RewardFiltersSchema,
    RewardExpandedSchema,
    ContributorSchema,
    RewardCompletionSchema,
    IssueIdentifierSchema
)
from ..common.schemas import PaginationSchema


class RewardServiceABC(ABC):

    @abstractmethod
    async def create_reward(self, author_id: UUID, schema: CreateRewardSchema) -> RewardSchema:
        """
        Adds a reward to a newly created issue.
        :param author_id: Rewarder user id.
        :param schema: Schema containing all the necessary data regarding the issue and the reward.
        :return: Reward data
        """
        raise NotImplementedError

    @abstractmethod
    async def add_reward(self, author_id: UUID, issue_id: UUID, amount_sats: int) -> RewardSchema:
        """
        Adds a reward to an already existing and open issue.
        :param author_id:
        :param issue_id:
        :param amount_sats:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def list_rewards(
        self,
        pagination: PaginationSchema | None = None,
        filters: RewardFiltersSchema | None = None
    ) -> list[RewardSchema]:
        raise NotImplementedError

    @abstractmethod
    async def list_rewards_expanded(
            self,
            pagination: PaginationSchema | None = None,
            filters: RewardFiltersSchema | None = None
    ) -> list[RewardExpandedSchema]:
        raise NotImplementedError

    @abstractmethod
    async def count_rewards(
        self,
        pagination: PaginationSchema | None = None,
        filters: RewardFiltersSchema | None = None
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_reward_by_id(self, reward_id: UUID) -> RewardSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_reward_by_id_expanded(self, reward_id: UUID) -> RewardExpandedSchema:
        raise NotImplementedError

    @abstractmethod
    async def reward_contributor(
        self,
        contributor: ContributorSchema,
        issue_id: UUID | None = None,
        issue_identifier: IssueIdentifierSchema | None = None
    ) -> RewardCompletionSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_total_reward(
        self,
        filters: RewardFiltersSchema | None = None
    ) -> int:
        raise NotImplementedError
