from pydantic import BaseModel

from ..common.schemas import (
    IdentifiableSchema,
    TimestampedSchema,
    UpdateSchema
)


class UserSchema(IdentifiableSchema, TimestampedSchema):
    github_id: int
    github_username: str
    avatar_url: str | None = None


class CreateUserSchema(BaseModel):
    github_id: int
    github_username: str
    avatar_url: str | None = None


class UpdateUserSchema(UpdateSchema):
    github_username: str
    avatar_url: str | None = None
