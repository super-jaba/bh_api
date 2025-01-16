from uuid import UUID

from domain.common.schemas import PaginationSchema, RepositoryData, UserData
from domain.issues import IssueServiceABC
from domain.issues.exceptions import IssueNotFound
from domain.issues.schemas import IssueSchema, IssueFiltersSchema, IssueExpandedSchema
from infrastructure.database import SessionScope
from infrastructure.database._abstract.dtos import Pagination
from infrastructure.database.issues import IssueRepo
from infrastructure.database.issues.dtos import IssueFiltersDto, ExtendedIssueDto


class IssueService(IssueServiceABC):

    def _translate_filters(
        self,
        domain_filters: IssueFiltersSchema
    ) -> IssueFiltersDto:
        """
        Translates filters from domain class to database-specific class
        :param domain_filters:
        :return:
        """
        return IssueFiltersDto(
            repository_ids=domain_filters.repository_ids,
            is_closed=domain_filters.is_closed,
            winner_id=domain_filters.winner_id
        )

    def _expanded_issue_db_row_to_schema(
        self,
        row: ExtendedIssueDto
    ) -> IssueExpandedSchema:
        return IssueExpandedSchema(
            **row.issue.__dict__,
            repository_data=RepositoryData(
                **row.repository.__dict__
            ),
            winner_data=UserData(
                **row.winner.__dict__
            ) if row.winner is not None else None,
            last_rewarder_data=UserData(
                **row.last_rewarder.__dict__
            ) if row.last_rewarder is not None else None,
            second_last_rewarder_data=UserData(
                **row.second_last_rewarder.__dict__
            ) if row.second_last_rewarder is not None else None,
            third_last_rewarder_data=UserData(
                **row.third_last_rewarder.__dict__
            ) if row.third_last_rewarder is not None else None,
            total_rewards=row.rewards_count,
            total_reward_sats=row.rewards_sat_sum
        )

    async def list_issues(
        self,
        pagination: PaginationSchema,
        filters: IssueFiltersSchema | None = None
    ) -> list[IssueSchema]:
        async with SessionScope.get_session() as session:
            return [
                IssueSchema.model_validate(issue)
                for issue in await IssueRepo(session).list_issues(
                    pagination=Pagination(
                        skip=pagination.skip,
                        limit=pagination.limit
                    ),
                    filters=self._translate_filters(filters)
                )
            ]

    async def list_issues_expanded(
        self,
        pagination: PaginationSchema,
        filters: IssueFiltersSchema | None = None
    ) -> list[IssueExpandedSchema]:
        async with SessionScope.get_session() as session:
            return [
                self._expanded_issue_db_row_to_schema(record)
                for record in await IssueRepo(session).list_issues_extended(
                    pagination=Pagination(skip=pagination.skip, limit=pagination.limit),
                    filters=self._translate_filters(filters)
                )
            ]

    async def count_issues(
        self,
        filters: IssueFiltersSchema | None = None
    ) -> int:
        async with SessionScope.get_session() as session:
            return await IssueRepo(session).count_issues(
                filters=self._translate_filters(filters)
            )

    async def get_issue_by_id(self, issue_id: UUID) -> IssueSchema:
        async with SessionScope.get_session() as session:
            fetched_issue = await IssueRepo(session).get_issue_by_id(issue_id)
            if fetched_issue is None:
                raise IssueNotFound
            return IssueSchema.model_validate(fetched_issue)

    async def get_issue_by_id_expanded(self, issue_id: UUID) -> IssueExpandedSchema:
        async with SessionScope.get_session() as session:
            fetched_record = await IssueRepo(session).get_issue_by_id_expanded(issue_id)
            if fetched_record is None:
                raise IssueNotFound
            return self._expanded_issue_db_row_to_schema(
                await IssueRepo(session).get_issue_by_id_expanded(issue_id)
            )