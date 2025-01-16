from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, BIGINT, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import Mapped

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class IssueDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "issues"

    github_id: Mapped[int] = Column(BIGINT, unique=True, nullable=False)

    repository_id: Mapped[UUID] = Column(ForeignKey("repositories.id"), nullable=False)
    issue_number: Mapped[int] = Column(BIGINT, unique=False, nullable=False)

    title: Mapped[str] = Column(String, nullable=False)
    body: Mapped[str | None] = Column(String, nullable=True)
    html_url: Mapped[str | None] = Column(String, nullable=True)
    is_closed: Mapped[bool] = Column(Boolean, nullable=False, server_default="t")

    winner_id: Mapped[UUID | None] = Column(ForeignKey("users.id"), nullable=True)
    claimed_at: Mapped[datetime | None] = Column(DateTime(timezone=False), nullable=True)

    last_rewarder_id: Mapped[UUID | None] = Column(ForeignKey("users.id"), nullable=True)
    second_last_rewarder_id: Mapped[UUID | None] = Column(ForeignKey("users.id"), nullable=True)
    third_last_rewarder_id: Mapped[UUID | None] = Column(ForeignKey("users.id"), nullable=True)
