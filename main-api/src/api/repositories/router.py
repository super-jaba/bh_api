from uuid import UUID

from fastapi import APIRouter, status

from domain.repositories.exceptions import RepositoryNotFound
from domain.repositories.schemas import RepositorySchema

from api.dependencies.types import RepositoryServiceDep, PaginationDep
from api.exceptions.schemas import HTTPExceptionDetailSchema
from api.common.schemas import CountResponse
from api.exceptions.http import NotFoundException


router = APIRouter(tags=["Repositories"])


@router.get(
    "/",
    response_model=list[RepositorySchema]
)
async def list_repositories(
    pagination: PaginationDep,
    repository_service: RepositoryServiceDep
):
    return await repository_service.list_repositories(pagination)


@router.get(
    "/count",
    response_model=CountResponse
)
async def count_repositories(
    repository_service: RepositoryServiceDep
):
    return CountResponse(
        count=await repository_service.count_repositories()
    )


@router.get(
    "/{repository_id}",
    response_model=RepositorySchema,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_repository_by_id(
    repository_id: UUID,
    repository_service: RepositoryServiceDep
):
    """
    Fetches a repository by its ID

    Throws
    - **404** if the repository is not found
    """
    try:
        return await repository_service.get_repository_by_id(repository_id)
    except RepositoryNotFound as repo_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(repo_not_found)
        )
