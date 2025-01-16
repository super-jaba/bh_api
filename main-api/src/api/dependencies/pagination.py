from fastapi import Query

from domain.common.schemas import PaginationSchema


def read_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=200)
) -> PaginationSchema:
    return PaginationSchema(skip=skip, limit=limit)
