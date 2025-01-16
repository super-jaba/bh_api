from typing import Annotated, Callable
from uuid import UUID

from fastapi import Query, Header

from api.exceptions.http import BadRequestException, UnauthorizedException
from api.exceptions.schemas import HTTPExceptionDetailSchema
from api.rewards.issue_tracker import IssueTrackerService
from domain.rewards.schemas import RewardFiltersSchema


def get_reward_filters(
    issue_id: UUID | None = Query(None),
    is_closed: bool | None = Query(None),
    rewarder_id: UUID | None = Query(None)
) -> RewardFiltersSchema:
    return RewardFiltersSchema(
        issue_id=issue_id,
        is_closed=is_closed,
        rewarder_id=rewarder_id
    )


def validate_issue_tracker_secret_wrapper(
    no_header_provided_err_code: int = 1,
    invalid_secret_err_code: int = 2
) -> Callable[[str | None], None]:
    def validate_issue_tracker_secret(
        issue_tracker_secret: Annotated[str | None, Header()] = None
    ) -> None:
        if issue_tracker_secret is None:
            raise UnauthorizedException(detail=HTTPExceptionDetailSchema(
                error_code=no_header_provided_err_code,
                message="No Issue Tracker Secret provided."
            ))

        if not IssueTrackerService.validate(issue_tracker_secret):
            raise UnauthorizedException(detail=HTTPExceptionDetailSchema(
                error_code=invalid_secret_err_code,
                message="Invalid Issue Tracker Secret."
            ))

    return validate_issue_tracker_secret
