from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class RepositoryDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "repositories"

    github_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    owner_github_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    html_url: Mapped[str] = mapped_column(String, nullable=False)
