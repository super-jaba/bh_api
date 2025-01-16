import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, Depends

from domain.rewards.exceptions import (
    RewardNotFound, 
    IssueDoesNotExist, 
    IssueIsClosed
)
from domain.rewards.schemas import (
    CreateRewardSchema,
    RewardSchema,
    RewardFiltersSchema,
    RewardExpandedSchema,
    ContributorSchema,
    IssueIdentifierSchema,
    RewardCompletionSchema
)
from infrastructure.github.exceptions import (
    GithubIssueIsAlreadyClosed,
    GithubPullRequestNotFound,
    CouldNotFetchPullRequest
)
from infrastructure.github.schemas import GithubIssueIdentifierSchema
from infrastructure.lnbits.exceptions import NotEnoughSats

from .dependencies import get_reward_filters, validate_issue_tracker_secret_wrapper
from .schemas import (
    CreateRewardRequest,
    CheckPullRequest,
    RewardForTrackedIssueRequest
)
from .utils import (
    pull_request_is_valid_for_reward,
    extract_issue_numbers_from_pull_request,
    reward_for_issue
)
from ..common.schemas import CountResponse
from ..dependencies.types import (
    GetAuthenticatedUserDep,
    GithubAPIServiceDep,
    RewardServiceDep,
    PaginationDep
)
from ..exceptions.http import (
    NotFoundException,
    BadRequestException,
    ServerErrorException
)
from ..exceptions.schemas import HTTPExceptionDetailSchema


router = APIRouter(tags=["Rewards"])


@router.post(
    "/",
    response_model=RewardSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionDetailSchema}
    }
)
async def post_reward(
    user: GetAuthenticatedUserDep,
    reward_service: RewardServiceDep,
    github_api_service: GithubAPIServiceDep,
    body: CreateRewardRequest
):
    if body.issue_lb_id is not None:
        try:
            return await reward_service.add_reward(user.id, body.issue_lb_id, amount_sats=body.reward_sats)
        except (IssueDoesNotExist, IssueIsClosed) as bad_issue:
            raise BadRequestException(HTTPExceptionDetailSchema.from_standard_exception(bad_issue))

    issue_identifier = github_api_service.parse_issue_html_url(body.issue_html_url)

    gh_repo, gh_issue = await asyncio.gather(
        github_api_service.fetch_repository(repo_full_name=issue_identifier.repo_full_name),
        github_api_service.fetch_issue(issue_identifier)
    )

    if gh_issue.state == "closed":
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(
                GithubIssueIsAlreadyClosed()
            )
        )

    try:
        reward = await reward_service.create_reward(
            author_id=user.id,
            schema=CreateRewardSchema(
                repo_github_id=gh_repo.id,
                repo_full_name=gh_repo.full_name,
                repo_owner_github_id=gh_repo.owner_id,
                repo_html_url=gh_repo.html_url,
                issue_github_id=gh_issue.id,
                issue_number=gh_issue.number,
                issue_title=gh_issue.title,
                issue_body=gh_issue.body,
                issue_html_url=gh_issue.html_url,
                reward_sats=body.reward_sats
            )
        )
    except NotEnoughSats as not_enough_sats:
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(not_enough_sats)
        )

    return reward


@router.get(
    "/",
    response_model=list[RewardExpandedSchema]
)
async def list_rewards(
    reward_service: RewardServiceDep,
    pagination: PaginationDep,
    filters: Annotated[RewardFiltersSchema, Depends(get_reward_filters)]
):
    return await reward_service.list_rewards_expanded(
        pagination=pagination,
        filters=filters
    )


@router.get(
    "/count",
    response_model=CountResponse
)
async def count_rewards(
    reward_service: RewardServiceDep,
    filters: Annotated[RewardFiltersSchema, Depends(get_reward_filters)]
):
    return CountResponse(
        count=await reward_service.count_rewards(filters=filters)
    )


@router.post(
    "/secret-route-for-issue-tracker",
    include_in_schema=False,  # Excluding from Docs!!!
    response_model=RewardCompletionSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema}
    }
)
async def reward_for_tracked_issue(
    body: RewardForTrackedIssueRequest,
    reward_service: RewardServiceDep,
    _=Depends(validate_issue_tracker_secret_wrapper(
        no_header_provided_err_code=1,
        invalid_secret_err_code=2
    ))
):
    return await reward_service.reward_contributor(
        contributor=ContributorSchema(
            github_id=body.winner.github_id,
            github_username=body.winner.login,
            avatar_url=body.winner.avatar_url
        ),
        issue_id=body.issue_id
    )



@router.get(
    "/{reward_id}",
    response_model=RewardExpandedSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_reward(
    reward_id: UUID,
    reward_service: RewardServiceDep
):
    """
    Fetches a reward by its ID.

    Throws:
    - **404** if the reward not found.
    """
    try:
        return await reward_service.get_reward_by_id_expanded(reward_id)
    except RewardNotFound as reward_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(reward_not_found)
        )


@router.post(
    "/check-pull",
    response_model=list[RewardCompletionSchema],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema}
    }
)
async def check_pull(
    body: CheckPullRequest,
    github_service: GithubAPIServiceDep,
    reward_service: RewardServiceDep
):
    identifier = GithubIssueIdentifierSchema(
        repo_full_name=body.repo_full_name,
        issue_number=body.pull_request_number
    )
    try:
        pull_request = await github_service.fetch_pull_request(identifier)
    except GithubPullRequestNotFound as pull_request_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(pull_request_not_found)
        )
    except CouldNotFetchPullRequest as could_not_fetch_pull_request:
        raise ServerErrorException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=HTTPExceptionDetailSchema.from_standard_exception(could_not_fetch_pull_request)
        )

    if not pull_request_is_valid_for_reward(pull_request):
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema(
                error_code=1,
                message="Invalid pull request. Make sure it is merged into default branch."
            )
        )

    commits = await github_service.fetch_pull_request_commits(identifier)

    issue_numbers = extract_issue_numbers_from_pull_request(pull_request, commits)

    reward_results = await asyncio.gather(
        *[
            reward_for_issue(
                reward_service=reward_service,
                contributor=ContributorSchema(
                    github_id=pull_request.user.id,
                    github_username=pull_request.user.login,
                    avatar_url=pull_request.user.avatar_url
                ),
                issue_identifier=IssueIdentifierSchema(
                    repo_full_name=pull_request.base.repo.full_name,
                    issue_number=issue_number
                )
            ) for issue_number in issue_numbers
        ]
    )

    return [
        result
        for result in reward_results
        if result is not None
    ]
