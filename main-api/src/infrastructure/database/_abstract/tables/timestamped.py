from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import SQLABase


class CreatedAtTimestamp(SQLABase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), nullable=False)


class ModifiedAtTimestamp(SQLABase):
    __abstract__ = True

    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=func.now(), onupdate=func.now())


class TimestampedDbModel(CreatedAtTimestamp, ModifiedAtTimestamp):
    __abstract__ = True
