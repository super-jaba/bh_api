from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from . import IssueDbModel
from .._abstract.dtos import UpdateDTO
from ..repositories import RepositoryDbModel
from ..users import UserDbModel


class IssueFiltersDto(BaseModel):
    repository_ids: list[UUID] = Field(default_factory=list)
    is_closed: bool | None = None
    winner_id: UUID | None = None


class CreateIssueDto(BaseModel):
    github_id: int

    repository_id: UUID
    issue_number: int

    title: str
    body: str | None = None
    html_url: str | None = None
    is_closed: bool = Field(default=False)

    last_rewarder_id: UUID | None = None
    second_last_rewarder_id: UUID | None = None
    third_last_rewarder_id: UUID | None = None


class UpdateIssueDto(UpdateDTO):
    title: str | None = None
    body: str | None = None
    html_url: str | None = None
    is_closed: bool | None = None
    winner_id: UUID | None = None
    claimed_at: datetime | None = None
    repository_id: UUID | None = None
    last_rewarder_id: UUID | None = None
    second_last_rewarder_id: UUID | None = None
    third_last_rewarder_id: UUID | None = None


class ExtendedIssueDto(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    issue: IssueDbModel
    repository: RepositoryDbModel
    winner: UserDbModel | None = None
    last_rewarder: UserDbModel | None = None
    second_last_rewarder: UserDbModel | None = None
    third_last_rewarder: UserDbModel | None = None
    rewards_count: int
    rewards_sat_sum: int
