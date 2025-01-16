from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, Depends

from api.common.schemas import CountResponse
from api.dependencies.types import IssueServiceDep, PaginationDep
from api.exceptions.http import NotFoundException
from api.exceptions.schemas import HTTPExceptionDetailSchema
from domain.issues.exceptions import IssueNotFound
from domain.issues.schemas import IssueFiltersSchema, IssueExpandedSchema

from .dependencies import get_issue_filters


router = APIRouter(tags=["Issues"])


@router.get(
    "/",
    response_model=list[IssueExpandedSchema]
)
async def list_issues(
    issue_service: IssueServiceDep,
    pagination: PaginationDep,
    filters: Annotated[IssueFiltersSchema, Depends(get_issue_filters)]
):
    return await issue_service.list_issues_expanded(
        pagination=pagination,
        filters=filters
    )


@router.get(
    "/count",
    response_model=CountResponse
)
async def count_issues(
    issue_service: IssueServiceDep,
    filters: Annotated[IssueFiltersSchema, Depends(get_issue_filters)]
):
    issue_count = await issue_service.count_issues(
        filters=filters
    )

    return CountResponse(count=issue_count)


@router.get(
    "/{issue_id}",
    response_model=IssueExpandedSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_issue_by_id(
    issue_id: UUID,
    issue_service: IssueServiceDep
):
    """
    Fetches an issue by its ID.

    Throws:
    - **404** if issue not found.
    """
    try:
        return await issue_service.get_issue_by_id_expanded(issue_id)
    except IssueNotFound as issue_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(issue_not_found)
        )
