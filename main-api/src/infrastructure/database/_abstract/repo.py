import abc

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import Pagination


class SQLAAbstractRepo(abc.ABC):
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _apply_pagination(
        statement: Select,
        pagination: Pagination | None = None
    ) -> Select:
        if pagination is not None:
            statement = statement.offset(pagination.skip)
            if pagination.limit is not None:
                statement = statement.limit(pagination.limit)
        return statement
    
    @staticmethod
    def lock_rows(statement: Select) -> Select:
        return statement.with_for_update()
