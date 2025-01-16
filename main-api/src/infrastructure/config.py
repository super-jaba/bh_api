from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    user: str = "postgres"
    password: str = "postgres"
    database: str = "postgres"


class LNBitsConfig(BaseModel):
    node_url: str


class GithubConfig(BaseModel):
    client_id: str
    client_secret: str


class BrantaConfig(BaseModel):
    url_base: str
    api_key: str



