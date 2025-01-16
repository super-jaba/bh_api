from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CreateRewardRequest(BaseModel):
    issue_html_url: str | None = None
    issue_lb_id: UUID | None = None
    reward_sats: int = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_issue(self) -> None:
        if not any([self.issue_html_url, self.issue_lb_id]):
            raise ValueError("Could not identify the issue. Either 'issue_html_url' or 'issue_lb_id' should be passed.")
        return self


class CheckPullRequest(BaseModel):
    repo_full_name: str
    pull_request_number: int


class Winner(BaseModel):
    github_id: int
    login: str
    avatar_url: str | None = None


class RewardForTrackedIssueRequest(BaseModel):
    issue_id: UUID
    winner: Winner
