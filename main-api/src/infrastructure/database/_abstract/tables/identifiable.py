from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID

from .base import SQLABase


class IdentifiableDbModel(SQLABase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
