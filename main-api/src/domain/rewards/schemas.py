from uuid import UUID

from pydantic import Field, BaseModel

from domain.common.schemas import (
    IdentifiableSchema,
    TimestampedSchema,
    UserData,
    IssueData
)


class RewardFiltersSchema(BaseModel):
    issue_id: UUID | None = None
    is_closed: bool | None = None
    rewarder_id: UUID | None = None


class RewardSchema(IdentifiableSchema, TimestampedSchema):
    issue_id: UUID
    rewarder_id: UUID
    reward_sats: int = Field(..., gt=0)


class RewardExpandedSchema(RewardSchema):
    rewarder_data: UserData
    issue_data: IssueData


class CreateRewardSchema(BaseModel):
    repo_github_id: int
    repo_full_name: str
    repo_owner_github_id: int
    repo_html_url: str

    issue_github_id: int
    issue_number: int

    issue_title: str
    issue_body: str | None = None
    issue_html_url: str | None = None

    reward_sats: int = Field(..., gt=0)


class ContributorSchema(BaseModel):
    github_id: int
    github_username: str = Field(..., max_length=50)
    avatar_url: str | None = Field(None)


class IssueIdentifierSchema(BaseModel):
    repo_full_name: str
    issue_number: int


class RewardCompletionSchema(BaseModel):
    issue_id: UUID
    winner_id: UUID
    total_sats: float
