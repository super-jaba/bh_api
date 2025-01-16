from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .._abstract.tables import IdentifiableDbModel, TimestampedDbModel


class LightningWalletDbModel(IdentifiableDbModel, TimestampedDbModel):
    __tablename__ = "lightning_wallets"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    wallet_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    adminkey: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    inkey: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
