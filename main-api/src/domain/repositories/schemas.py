from domain.common.schemas import IdentifiableSchema, TimestampedSchema


class RepositorySchema(IdentifiableSchema, TimestampedSchema):
    github_id: int
    
    full_name: str
    owner_github_id: int
    html_url: str
