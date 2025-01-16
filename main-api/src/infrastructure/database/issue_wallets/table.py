from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class IssueLightningWalletDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "issue_lightning_wallets"

    issue_id: Mapped[UUID] = mapped_column(ForeignKey("issues.id"), unique=True, nullable=False)

    wallet_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    adminkey: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    inkey: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
