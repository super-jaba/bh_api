from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator, Field


class IdentifiableSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class TimestampedSchema(BaseModel):
    created_at: datetime
    modified_at: datetime


class UpdateSchema(BaseModel):
    @model_validator(mode="after")
    def check_if_not_all_fields_are_none(self) -> Self:
        if self.model_dump(exclude_unset=True) == {}:
            msg = "At least one updatable field has to be passed."
            raise ValueError(msg)
        return self


class PaginationSchema(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int | None = Field(None, ge=1)


class RepositoryData(BaseModel):
    """
    Used for joined repository data.
    """
    id: UUID
    full_name: str


class IssueData(BaseModel):
    id: UUID
    issue_number: int
    title: str
    is_closed: bool


class UserData(BaseModel):
    """
    Used for joined user data.
    """
    id: UUID
    github_username: str
    avatar_url: str | None = None
