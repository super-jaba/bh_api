import datetime

from pydantic import BaseModel, field_validator


class GetAccessTokenSchema(BaseModel):
    user_id: str
    github_username: str
    github_token: str

    @field_validator("user_id", mode="before")
    @classmethod
    def transform_id_to_str(cls, value) -> str:
        return str(value)


class AccessTokenPayloadSchema(BaseModel):
    user_id: str
    github_username: str
    github_token: str
    exp: datetime.datetime
