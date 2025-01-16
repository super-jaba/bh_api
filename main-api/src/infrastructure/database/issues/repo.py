import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, update, Select, func
from sqlalchemy.orm import aliased

from .table import IssueDbModel
from .._abstract.dtos import Pagination
from .._abstract.repo import SQLAAbstractRepo
from .dtos import (
    CreateIssueDto,
    UpdateIssueDto,
    IssueFiltersDto, ExtendedIssueDto
)
from ..repositories import RepositoryDbModel
from ..rewards import RewardDbModel
from ..users import UserDbModel


class IssueRepo(SQLAAbstractRepo):

    def _apply_filters(
        self,
        stmt: Select,
        filters: IssueFiltersDto
    ) -> Select:
        if len(filters.repository_ids):
            stmt = stmt.where(IssueDbModel.repository_id.in_(filters.repository_ids))
        if filters.is_closed is not None:
            stmt = stmt.where(IssueDbModel.is_closed == filters.is_closed)
        if filters.winner_id is not None:
            stmt = stmt.where(IssueDbModel.winner_id == filters.winner_id)

        return stmt

    def _parse_row(self, row: Any) -> ExtendedIssueDto:
        return ExtendedIssueDto(
            issue=row[0],
            repository=row[1],
            winner=row[2],
            last_rewarder=row[3],
            second_last_rewarder=row[4],
            third_last_rewarder=row[5],
            rewards_count=row[6] if row[6] is not None else 0,
            rewards_sat_sum=row[7] if row[7] is not None else 0
        )

    async def create_issue(self, issue_dto: CreateIssueDto) -> IssueDbModel:
        new_issue = IssueDbModel(**issue_dto.model_dump())
        self._session.add(new_issue)
        logging.debug(f"New issue created: {new_issue}")
        return new_issue

    async def get_issue_by_id(self, issue_id: UUID, lock: bool = False) -> IssueDbModel | None:
        stmt = select(IssueDbModel).where(IssueDbModel.id == issue_id)
        if lock:
            stmt = self.lock_rows(stmt)

        return await self._session.scalar(
            stmt
        )

    async def get_issue_by_id_expanded(
        self,
        issue_id: UUID
    ) -> tuple[IssueDbModel, RepositoryDbModel, UserDbModel, int, int | None]:
        WinnerDbModel = aliased(UserDbModel)
        LastRewarderDbModel = aliased(UserDbModel)
        SecondLastRewarderDbModel = aliased(UserDbModel)
        ThirdLastRewarderDbModel = aliased(UserDbModel)

        # Subquery to count rewards per issue
        reward_count_subquery = select(
            RewardDbModel.issue_id,
            func.count(RewardDbModel.id).label("reward_count")
        ).group_by(RewardDbModel.issue_id).subquery()

        # Subquery to sum reward amounts per issue
        reward_sum_subquery = select(
            RewardDbModel.issue_id,
            func.sum(RewardDbModel.reward_sats).label("total_reward_sats")
        ).group_by(RewardDbModel.issue_id).subquery()

        stmt = select(
            IssueDbModel,
            RepositoryDbModel,
            WinnerDbModel,
            LastRewarderDbModel,
            SecondLastRewarderDbModel,
            ThirdLastRewarderDbModel,
            reward_count_subquery.c.reward_count,
            reward_sum_subquery.c.total_reward_sats
        ).outerjoin(
            RepositoryDbModel,
            IssueDbModel.repository_id == RepositoryDbModel.id
        ).outerjoin(
            WinnerDbModel,
            IssueDbModel.winner_id == WinnerDbModel.id
        ).outerjoin(
            LastRewarderDbModel,
            IssueDbModel.last_rewarder_id == LastRewarderDbModel.id
        ).outerjoin(
            SecondLastRewarderDbModel,
            IssueDbModel.second_last_rewarder_id == SecondLastRewarderDbModel.id
        ).outerjoin(
            ThirdLastRewarderDbModel,
            IssueDbModel.third_last_rewarder_id == ThirdLastRewarderDbModel.id
        ).outerjoin(
            reward_count_subquery,
            IssueDbModel.id == reward_count_subquery.c.issue_id
        ).outerjoin(
            reward_sum_subquery,
            IssueDbModel.id == reward_sum_subquery.c.issue_id
        ).where(
            IssueDbModel.id == issue_id
        )

        res = (await self._session.execute(stmt)).first()
        return self._parse_row(res)

    async def get_issue_by_github_id(self, issue_github_id: int, lock: bool = False) -> IssueDbModel | None:
        stmt = select(IssueDbModel).where(IssueDbModel.github_id == issue_github_id)
        if lock:
            stmt = self.lock_rows(stmt)

        return await self._session.scalar(
            stmt
        )

    async def get_issue_by_repo_fullname(self, fullname: str, issue_number: int, lock: bool = False) -> IssueDbModel | None:
        stmt = select(
            IssueDbModel
        ).join(
            RepositoryDbModel, IssueDbModel.repository_id == RepositoryDbModel.id
        ).where(
            RepositoryDbModel.full_name == fullname
        ).where(
            IssueDbModel.issue_number == issue_number
        )
        if lock:
            stmt = self.lock_rows(stmt)

        return await self._session.scalar(stmt)

    async def list_issues(
            self,
            pagination: Pagination | None = None,
            filters: IssueFiltersDto | None = None
    ) -> list[IssueDbModel]:
        stmt = self._apply_pagination(
            select(IssueDbModel).order_by(IssueDbModel.created_at.desc()),
            pagination
        )

        if filters is not None:
            stmt = self._apply_filters(stmt, filters)

        return await self._session.scalars(stmt)

    async def list_issues_extended(
        self,
        pagination: Pagination | None = None,
        filters: IssueFiltersDto | None = None
    ) -> list[ExtendedIssueDto]:
        """
        Lists the issues based on the pagination and filters passed.
        Sorts descending by **created_at**

        Joins
        - Repository
        - Winner user data
        - Last rewarder user data
        - Second last rewarder user data
        - Third last rewarder user data

        Counts
        - Total rewards for each issue
        - Sum of reward amounts for each issue
        :param pagination:
        :param filters:
        :return:
        """
        WinnerDbModel = aliased(UserDbModel)
        LastRewarderDbModel = aliased(UserDbModel)
        SecondLastRewarderDbModel = aliased(UserDbModel)
        ThirdLastRewarderDbModel = aliased(UserDbModel)

        # Subquery to count rewards per issue
        reward_count_subquery = select(
            RewardDbModel.issue_id,
            func.count(RewardDbModel.id).label("reward_count")
        ).group_by(RewardDbModel.issue_id).subquery()

        # Subquery to sum reward amounts per issue
        reward_sum_subquery = select(
            RewardDbModel.issue_id,
            func.sum(RewardDbModel.reward_sats).label("total_reward_sats")
        ).group_by(RewardDbModel.issue_id).subquery()

        stmt = select(
            IssueDbModel,
            RepositoryDbModel,
            WinnerDbModel,
            LastRewarderDbModel,
            SecondLastRewarderDbModel,
            ThirdLastRewarderDbModel,
            reward_count_subquery.c.reward_count,
            reward_sum_subquery.c.total_reward_sats
        ).outerjoin(
            RepositoryDbModel,
            IssueDbModel.repository_id == RepositoryDbModel.id
        ).outerjoin(
            WinnerDbModel,
            IssueDbModel.winner_id == WinnerDbModel.id
        ).outerjoin(
            LastRewarderDbModel,
            IssueDbModel.last_rewarder_id == LastRewarderDbModel.id
        ).outerjoin(
            SecondLastRewarderDbModel,
            IssueDbModel.second_last_rewarder_id == SecondLastRewarderDbModel.id
        ).outerjoin(
            ThirdLastRewarderDbModel,
            IssueDbModel.third_last_rewarder_id == ThirdLastRewarderDbModel.id
        ).outerjoin(
            reward_count_subquery,
            IssueDbModel.id == reward_count_subquery.c.issue_id
        ).outerjoin(
            reward_sum_subquery,
            IssueDbModel.id == reward_sum_subquery.c.issue_id
        ).order_by(
            IssueDbModel.created_at.desc()
        )

        stmt = self._apply_pagination(
            stmt,
            pagination
        )

        if filters is not None:
            stmt = self._apply_filters(stmt, filters)

        rows = (await self._session.execute(stmt)).all()
        return [
            self._parse_row(row)
            for row in rows
        ]

    async def count_issues(
        self,
        filters: IssueFiltersDto | None = None
    ) -> int:
        """
        Counts the number of issues satisfying the filters if passed
        :param filters:
        :return: int
        """

        stmt = select(func.count(IssueDbModel.id))
        if filters is not None:
            stmt = self._apply_filters(stmt, filters)

        return await self._session.scalar(stmt)

    async def update_issue(self, issue_id: UUID, update_fields: UpdateIssueDto) -> IssueDbModel | None:
        stmt = (
            update(IssueDbModel).where(IssueDbModel.id == issue_id)
            .values(**update_fields.model_dump(exclude_unset=True))
            .returning(IssueDbModel)

        )
        logging.debug(f"Issue updated with fields: {update_fields.model_dump(exclude_unset=True)}")
        return await self._session.scalar(stmt)

    def update_top_rewarders(
        self,
        issue_obj: IssueDbModel,
        new_rewarder_id: UUID
    ) -> IssueDbModel:
        issue_obj.third_last_rewarder_id = issue_obj.second_last_rewarder_id
        issue_obj.second_last_rewarder_id = issue_obj.last_rewarder_id
        issue_obj.last_rewarder_id = new_rewarder_id
        return issue_obj

    async def get_or_create_issue(self, issue_dto: CreateIssueDto) -> tuple[IssueDbModel, bool]:
        """
        Fetches an issue by its GitHub ID, creates a new issue if it"s not found.
        :param issue_dto: DTO to create the issue if not found.
        :return: Issue, [True if the issue was created, False otherwise]
        """
        issue_was_created = False
        issue = await self.get_issue_by_github_id(issue_github_id=issue_dto.github_id)
        if issue is None:
            issue = await self.create_issue(issue_dto)
            issue_was_created = True
        return issue, issue_was_created

    async def get_update_or_create_issue(self, issue_dto: CreateIssueDto) -> tuple[IssueDbModel, bool, bool]:
        """
        Fetches an issue by its GitHub ID,
        updates it if it"s different from issue_dto
        and creates a new issue if not found.
        :param issue_dto: DTO to create the issue if not found.
        :return: A tuple containing:
            - IssueDbModel: The issue Model (updated or newly created).
            - bool #1: True if the issue was created, False otherwise.
            - bool #2: True if the issue was updated, False otherwise.
        """
        issue, created = await self.get_or_create_issue(issue_dto)
        if created:
            return issue, created, False

        updated = False
        if self._issue_has_differences(issue, issue_dto):
            issue = await self.update_issue(
                issue_id=issue.id,
                update_fields=UpdateIssueDto(
                    title=issue_dto.title,
                    body=issue_dto.body,
                    is_closed=issue_dto.is_closed,
                    repository_id=issue_dto.repository_id
                )
            )

        return issue, created, updated

    def _issue_has_differences(self, issue: IssueDbModel, expected_dto: CreateIssueDto) -> bool:
        """
        Checks if there are differences between the existing issue and the DTO of the expected values.
        :param issue: The existing issue.
        :param expected_dto: Expected values
        :return: True if there are differences, False otherwise
        """

        return (
            issue.issue_number != expected_dto.issue_number
            or issue.title != expected_dto.title
            or issue.body != expected_dto.body
            or issue.is_closed != expected_dto.is_closed
            or issue.repository_id != expected_dto.repository_id
        )
