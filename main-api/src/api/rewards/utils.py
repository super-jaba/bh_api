import re

from domain.rewards import RewardServiceABC
from domain.rewards.schemas import IssueIdentifierSchema, RewardCompletionSchema, ContributorSchema
from infrastructure.github.schemas import GithubPullRequestSchema, GithubCommitSchema


def pull_request_is_valid_for_reward(pull_request: GithubPullRequestSchema) -> bool:
    if not pull_request.merged_at:
        return False

    if pull_request.merged_at < pull_request.updated_at:
        return False

    if pull_request.base.ref != pull_request.base.repo.default_branch:
        return False

    return True


def _find_issue_numbers(text: str) -> set[int]:
    # Define the regex pattern to match linked issues
    pattern = r"(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)"

    # Find all matches in the commit message
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Extract issue numbers from the matches
    linked_issues = set([int(match[1]) for match in matches])

    return linked_issues


def extract_issue_numbers_from_pull_request(
    pull_request: GithubPullRequestSchema,
    commits: list[GithubCommitSchema]
) -> list[int]:
    issue_numbers = set()
    issue_numbers = issue_numbers.union(_find_issue_numbers(pull_request.body))
    for commit in commits:
        issue_numbers = issue_numbers.union(_find_issue_numbers(commit.message))

    return list(set(issue_numbers))


async def reward_for_issue(
    reward_service: RewardServiceABC,
    contributor: ContributorSchema,
    issue_identifier: IssueIdentifierSchema
) -> RewardCompletionSchema | None:
    try:
        return await reward_service.reward_contributor(
            contributor=contributor,
            issue_identifier=issue_identifier
        )
    except Exception as e:
        print(e)
