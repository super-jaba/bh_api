from pydantic import BaseModel, Field

from .._abstract.dtos import UpdateDTO


class CreateRepositoryDto(BaseModel):
    github_id: int
    full_name: str
    owner_github_id: int
    html_url: str


class UpdateRepositoryDto(UpdateDTO):
    fullname: str | None = Field(None)
    owner_github_id: int
    html_url: str | None = Field(None)
