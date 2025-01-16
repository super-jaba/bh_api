from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .table import RewardDbModel
from ..issues import IssueDbModel
from ..users import UserDbModel


class CreateRewardDto(BaseModel):
    issue_id: UUID
    rewarder_id: UUID
    reward_sats: int


class RewardFiltersDto(BaseModel):
    issue_id: UUID | None = None
    is_closed: bool | None = None
    rewarder_id: UUID | None = None


class ExpandedRewardDto(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    reward: RewardDbModel
    rewarder: UserDbModel
    issue: IssueDbModel
