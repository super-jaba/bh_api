from uuid import UUID

from sqlalchemy import ForeignKey, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class RewardDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "rewards"

    issue_id: Mapped[UUID] = mapped_column(ForeignKey("issues.id"), nullable=False)
    rewarder_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reward_sats: Mapped[int] = mapped_column(BIGINT, nullable=False)

    # TODO: expiration, lock
