from pydantic import BaseModel, Field

from .._abstract.dtos import UpdateDTO


class CreateUserDTO(BaseModel):
    github_id: int
    github_username: str = Field(..., max_length=50)
    avatar_url: str | None = Field(None)


class UpdateUserDTO(UpdateDTO):
    github_username: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None)
