from pydantic import BaseModel


class CORSSettings(BaseModel):
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["GET", "POST"]
    allow_headers: list[str] = ["*"]  # TODO: Refactor when routes are done.


class JWTSettings(BaseModel):
    algorithm: str = "HS256"
    access_token_secret: str


class IssueTrackerSettings(BaseModel):
    secret: str


class APIConfig(BaseModel):
    title: str = "Lightning Bounties API"
    version: str | None = None
    enable_docs: bool = False

    cors_settings: CORSSettings = CORSSettings()
    jwt_settings: JWTSettings
    issue_tracker_settings: IssueTrackerSettings
