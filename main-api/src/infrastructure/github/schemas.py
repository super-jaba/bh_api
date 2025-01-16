from typing import Self, Any

from pydantic import BaseModel, Field


class GithubAPIIdentifiable(BaseModel):
    id: int

    @classmethod
    def from_api(cls, json_response: Any) -> Self:
        return cls(**json_response)


class GithubUserSchema(GithubAPIIdentifiable):
    login: str
    avatar_url: str


class GithubRepositorySchema(GithubAPIIdentifiable):
    full_name: str
    owner_id: int
    html_url: str
    default_branch: str

    @classmethod
    def from_api(cls, json_response: Any) -> Self:
        return cls(
            id=json_response["id"],
            full_name=json_response["full_name"],
            owner_id=json_response["owner"]["id"],
            html_url=json_response["html_url"],
            default_branch=json_response["default_branch"]
        )


class GithubIssueIdentifierSchema(BaseModel):
    repo_full_name: str
    issue_number: int


class GithubIssueSchema(GithubAPIIdentifiable):
    number: int
    title: str
    body: str | None = None
    html_url: str | None = None
    state: str
    state_reason: str | None = None


class PullRequestBaseModel(BaseModel):
    ref: str
    repo: GithubRepositorySchema


class GithubPullRequestSchema(GithubAPIIdentifiable):
    id: int
    number: int
    title: str
    body: str = Field("")
    updated_at: str | None = Field(None)
    merged_at: str | None = Field(None)
    state: str
    user: GithubUserSchema
    base: PullRequestBaseModel

    @classmethod
    def from_api(cls, json_response: Any) -> Self:
        pr_user = GithubUserSchema.from_api(json_response["user"])
        pr_repo = GithubRepositorySchema.from_api(json_response["base"]["repo"])
        pr_base = PullRequestBaseModel(ref=json_response["base"]["ref"], repo=pr_repo)

        return GithubPullRequestSchema(
            id=json_response["id"],
            number=json_response["number"],
            title=json_response["title"],
            body=json_response["body"] if json_response["body"] else "",
            merged_at=json_response["merged_at"],
            updated_at=json_response["updated_at"],
            state=json_response["state"],
            user=pr_user,
            base=pr_base
        )


class GithubCommitSchema(BaseModel):
    sha: str
    message: str
    author: GithubUserSchema
