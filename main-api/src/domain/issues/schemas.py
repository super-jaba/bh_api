from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.common.schemas import IdentifiableSchema, TimestampedSchema, RepositoryData, UserData


class IssueFiltersSchema(BaseModel):
    repository_ids: list[UUID] = Field(default_factory=list)
    is_closed: bool | None = None
    winner_id: UUID | None = None


class IssueSchema(IdentifiableSchema, TimestampedSchema):
    repository_id: UUID

    github_id: int
    issue_number: int
    title: str
    body: str | None = None
    html_url: str | None = None
    is_closed: bool

    winner_id: UUID | None = None
    claimed_at: datetime | None = None

    last_rewarder_id: UUID | None = None
    second_last_rewarder_id: UUID | None = None
    third_last_rewarder_id: UUID | None = None


class IssueExpandedSchema(IssueSchema):
    repository_data: RepositoryData

    winner_data: UserData | None
    last_rewarder_data: UserData | None
    second_last_rewarder_data: UserData | None
    third_last_rewarder_data: UserData | None

    total_rewards: int
    total_reward_sats: int
