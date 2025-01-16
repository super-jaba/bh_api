from sqlalchemy import BIGINT, String
from sqlalchemy.orm import Mapped, mapped_column

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class UserDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "users"

    github_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True)
    github_username: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
