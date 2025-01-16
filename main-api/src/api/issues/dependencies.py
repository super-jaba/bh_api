from uuid import UUID

from fastapi import Query

from domain.issues.schemas import IssueFiltersSchema


def get_issue_filters(
    repository_ids: list[UUID] = Query([]),
    is_closed: bool | None = Query(None),
    winner_id: UUID | None = Query(None)
):
    return IssueFiltersSchema(
            repository_ids=repository_ids,
            is_closed=is_closed,
            winner_id=winner_id
    )