import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.common.schemas import PaginationSchema, UserData, IssueData
from domain.rewards import RewardServiceABC
from domain.rewards.exceptions import (
    RewardNotFound, 
    NothingToRewardFor, 
    IssueDoesNotExist, 
    IssueIsClosed
)
from domain.rewards.schemas import (
    CreateRewardSchema,
    RewardSchema,
    RewardFiltersSchema,
    RewardExpandedSchema,
    ContributorSchema,
    RewardCompletionSchema,
    IssueIdentifierSchema
)
from impl.common.issue_bank import IssueBank
from infrastructure.database import SessionScope
from infrastructure.database._abstract.dtos import Pagination
from infrastructure.database.issues import IssueRepo, IssueDbModel
from infrastructure.database.issues.dtos import CreateIssueDto, UpdateIssueDto
from infrastructure.database.lightning_wallet import LightningWalletDbModel, LightningWalletRepo
from infrastructure.database.lightning_wallet.dtos import LightningWalletDTO
from infrastructure.database.repositories import RepositoryRepo
from infrastructure.database.repositories.dto import CreateRepositoryDto
from infrastructure.database.rewards import RewardRepo, RewardDbModel
from infrastructure.database.rewards.dtos import (
    CreateRewardDto,
    RewardFiltersDto,
    ExpandedRewardDto
)
from infrastructure.database.users import UserRepo, UserDbModel
from infrastructure.database.users.dtos import CreateUserDTO
from infrastructure.lnbits import LNBitsClient


class ContributorRegisterer:

    @classmethod
    async def _get_or_register_contributor(
        cls,
        session: AsyncSession,
        contributor: ContributorSchema
    ) -> UserDbModel:
        return await UserRepo(session).get_user_by_github_id_or_create(
            github_id=contributor.github_id,
            user_dto=CreateUserDTO(
                github_id=contributor.github_id,
                github_username=contributor.github_username,
                avatar_url=contributor.avatar_url
            )
        )

    @classmethod
    async def _get_or_create_contributor_wallet(
        cls,
        session: AsyncSession,
        contributor_user_id: UUID
    ) -> LightningWalletDbModel:
        wallet_repo = LightningWalletRepo(session)
        wallet = await wallet_repo.get_wallet_by_user_id(contributor_user_id)
        if wallet is None:
            new_wallet = await LNBitsClient().create_headless_wallet(name=contributor_user_id.hex)

            wallet = await wallet_repo.create_wallet(
                LightningWalletDTO(
                    user_id=contributor_user_id,
                    wallet_id=new_wallet.id,
                    adminkey=new_wallet.adminkey,
                    inkey=new_wallet.inkey
                )
            )
        return wallet

    @classmethod
    async def get_contributor_wallet(
        cls,
        session: AsyncSession,
        contributor: ContributorSchema
    ) -> LightningWalletDbModel:
        contributor = await cls._get_or_register_contributor(session, contributor)
        return await cls._get_or_create_contributor_wallet(
            session,
            contributor_user_id=contributor.id
        )


class RewardService(RewardServiceABC):

    def _translate_filters(
        self,
        domain_filters: RewardFiltersSchema
    ) -> RewardFiltersDto:
        """
        Translates filters from domain class to database-specific class
        :param domain_filters:
        :return:
        """
        return RewardFiltersDto(
            issue_id=domain_filters.issue_id,
            is_closed=domain_filters.is_closed,
            rewarder_id=domain_filters.rewarder_id
        )

    def _db_row_to_schema(self, row: ExpandedRewardDto) -> RewardExpandedSchema:
        return RewardExpandedSchema(
            **row.reward.__dict__,
            rewarder_data=UserData(
                **row.rewarder.__dict__
            ),
            issue_data=IssueData(
                **row.issue.__dict__
            )
        )

    async def _create_reward_object(
        self,
        session: AsyncSession,
        author_id: UUID,
        schema: CreateRewardSchema
    ) -> RewardDbModel:
        """
        Creates the reward ORM object along with all the corresponding objects - Repository and Issue.
        Updates Repository and Issue if there are differences found
        :param session: ORM session
        :param author_id: Author of the reward
        :param schema: Fields used to create the reward
        :return: RewardDbModel
        """
        gh_repo, _, _ = await RepositoryRepo(session).get_update_or_create_repository(
            repository_dto=CreateRepositoryDto(
                github_id=schema.repo_github_id,
                full_name=schema.repo_full_name,
                owner_github_id=schema.repo_owner_github_id,
                html_url=schema.repo_html_url
            )
        )
        await session.flush()

        issue_repo = IssueRepo(session)
        gh_issue, _, _ = await issue_repo.get_update_or_create_issue(
            issue_dto=CreateIssueDto(
                github_id=schema.issue_github_id,
                repository_id=gh_repo.id,
                issue_number=schema.issue_number,
                title=schema.issue_title,
                body=schema.issue_body,
                html_url=schema.issue_html_url,
                is_closed=False
            )
        )
        issue_repo.update_top_rewarders(gh_issue, author_id)

        await session.flush()

        return await RewardRepo(session).create_reward(
            reward_dto=CreateRewardDto(
                issue_id=gh_issue.id,
                rewarder_id=author_id,
                reward_sats=schema.reward_sats
            )
        )

    async def create_reward(self, author_id: UUID, schema: CreateRewardSchema) -> RewardSchema:
        async with SessionScope.get_session() as session:
            reward = await self._create_reward_object(
                session=session,
                author_id=author_id,
                schema=schema
            )

            await IssueBank(session).reserve_sats(
                from_user_id=author_id,
                to_issue_id=reward.issue_id,
                amount=schema.reward_sats
            )

            await session.commit()

            return RewardSchema.model_validate(reward)

    async def add_reward(self, author_id: UUID, issue_id: UUID, amount_sats: int) -> RewardSchema:
        async with SessionScope.get_session() as session:
            issue_repo = IssueRepo(session)
            issue = await issue_repo.get_issue_by_id(issue_id, lock=True)
            if issue is None:
                raise IssueDoesNotExist

            if issue.is_closed:
                raise IssueIsClosed

            reward = await RewardRepo(session).create_reward(
                reward_dto=CreateRewardDto(
                    issue_id=issue.id,
                    rewarder_id=author_id,
                    reward_sats=amount_sats
                )
            )

            await IssueBank(session).reserve_sats(
                from_user_id=author_id,
                to_issue_id=reward.issue_id,
                amount=amount_sats
            )

            issue_repo.update_top_rewarders(issue, author_id)

            await session.commit()

            return RewardSchema.model_validate(reward)

    async def list_rewards(
        self,
        pagination: PaginationSchema | None = None,
        filters: RewardFiltersSchema | None = None
    ) -> list[RewardSchema]:
        async with SessionScope.get_session() as session:
            return [
                RewardSchema.model_validate(reward)
                for reward in await RewardRepo(session).list_rewards(
                    pagination=Pagination(skip=pagination.skip, limit=pagination.limit),
                    filters=self._translate_filters(filters)
                )
            ]

    async def list_rewards_expanded(
            self,
            pagination: PaginationSchema | None = None,
            filters: RewardFiltersSchema | None = None
    ) -> list[RewardExpandedSchema]:
        async with SessionScope.get_session() as session:
            return [
                self._db_row_to_schema(row)
                for row in await RewardRepo(session).list_rewards_expanded(
                    pagination=Pagination(skip=pagination.skip, limit=pagination.limit),
                    filters=self._translate_filters(filters)
                )
            ]

    async def count_rewards(
        self,
        pagination: PaginationSchema | None = None,
        filters: RewardFiltersSchema | None = None
    ) -> int:
        async with SessionScope.get_session() as session:
            return await RewardRepo(session).count_rewards(
                filters=self._translate_filters(filters)
            )

    async def get_reward_by_id(self, reward_id: UUID) -> RewardSchema:
        async with SessionScope.get_session() as session:
            fetched_reward = await RewardRepo(session).get_reward(reward_id)
            if fetched_reward is None:
                raise RewardNotFound
            return RewardSchema.model_validate(fetched_reward)

    async def get_reward_by_id_expanded(self, reward_id: UUID) -> RewardExpandedSchema:
        async with SessionScope.get_session() as session:
            res = await RewardRepo(session).get_reward_expanded(reward_id)
            if res is None:
                raise RewardNotFound
            return self._db_row_to_schema(res)

    async def reward_contributor(
        self,
        contributor: ContributorSchema,
        issue_id: UUID | None = None,
        issue_identifier: IssueIdentifierSchema | None = None
    ) -> RewardCompletionSchema:


        # TODO: Cleanup!!!

        if not any([issue_id, issue_identifier]):
            raise ValueError("Issue not passed.")

        async with SessionScope.get_session() as session:
            contributor_wallet = await ContributorRegisterer.get_contributor_wallet(
                session=session,
                contributor=contributor
            )
            issue_repo = IssueRepo(session)

            issue: IssueDbModel | None = None
            if issue_id is not None:
                issue = await issue_repo.get_issue_by_id(issue_id, lock=True)
            else:  # issue_identifier is not None
                issue = await issue_repo.get_issue_by_repo_fullname(
                    fullname=issue_identifier.repo_full_name,
                    issue_number=issue_identifier.issue_number,
                    lock=True
                )

            if issue is None:
                raise NothingToRewardFor

            total_sats_job = IssueBank(session).reward_user(
                user_id=contributor_wallet.user_id,
                for_issue_id=issue.id
            )
            update_issue_job = issue_repo.update_issue(
                issue_id=issue.id,
                update_fields=UpdateIssueDto(
                    is_closed=True,
                    winner_id=contributor_wallet.user_id,
                    claimed_at=datetime.datetime.utcnow()
                )
            )

            total_sats = await total_sats_job
            _updated_issue = await update_issue_job

            await session.commit()

            return RewardCompletionSchema(
                issue_id=issue.id,
                winner_id=contributor_wallet.user_id,
                total_sats=total_sats
            )

    async def get_total_reward(
        self,
        filters: RewardFiltersSchema | None = None
    ) -> int:
        async with SessionScope.get_session() as session:
            return await RewardRepo(session).calculate_total_reward(
                filters=self._translate_filters(filters)
            )
