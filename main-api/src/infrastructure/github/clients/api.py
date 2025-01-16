import httpx

from ..exceptions import (
    CouldNotFetchGithubUser,
    GithubPullRequestNotFound,
    CouldNotFetchPullRequest
)
from ..schemas import (
    GithubUserSchema,
    GithubRepositorySchema,
    GithubIssueSchema,
    GithubIssueIdentifierSchema,
    GithubPullRequestSchema,
    GithubCommitSchema
)


class GithubAPIClient:
    """
    GithubAPIService is responsible for working with GitHub API.
    """

    _api_token: str
    _request_headers: dict[str, str]

    def __init__(self, api_token: str):
        self._api_token = api_token
        self._request_headers = {"Authorization": f"Bearer {self._api_token}"}

    async def get_authenticated_user(self) -> GithubUserSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers=self._request_headers
            )

            if response.status_code != 200:
                raise CouldNotFetchGithubUser

            return GithubUserSchema.from_api(response.json())

    async def fetch_repository(self, repo_full_name: str) -> GithubRepositorySchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/repos/" + repo_full_name,
                headers=self._request_headers
            )

            # TODO: Handle exceptions
            # Refer to the GitHub API documentation
            # 301 - Moved permanently
            # 403 - Forbidden
            # 404 - Not Found

            return GithubRepositorySchema.from_api(response.json())

    async def fetch_issue(self, identifier: GithubIssueIdentifierSchema) -> GithubIssueSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/repos/" + identifier.repo_full_name + "/issues/" + str(identifier.issue_number),
                headers=self._request_headers
            )

            # TODO: Handle exceptions
            # Refer to the GitHub API documentation
            # 301 - Moved permanently
            # 404 - Not found

            return GithubIssueSchema.from_api(response.json())

    def parse_issue_html_url(self, url: str) -> GithubIssueIdentifierSchema:
        url_components = url.split("/")
        if len(url_components) != 7:
            raise ValueError("Invalid url format.")

        repo_full_name = f"{url_components[3]}/{url_components[4]}"
        issue_number = int(url_components[-1])

        return GithubIssueIdentifierSchema(
            repo_full_name=repo_full_name,
            issue_number=issue_number
        )

    async def fetch_issue_html_url(self, html_url: str) -> GithubIssueSchema:
        identifier = self.parse_issue_html_url(html_url)
        return await self.fetch_issue(identifier)

    async def fetch_pull_request(
        self,
        identifier: GithubIssueIdentifierSchema
    ) -> GithubPullRequestSchema:
        async with httpx.AsyncClient() as client:
            url = (f"https://api.github.com/repos/"
                   f"{identifier.repo_full_name}/pulls/{identifier.issue_number}")
            params = {"state": "closed"}

            resp = await client.get(url, headers=self._request_headers, params=params)

            if resp.status_code != 200:
                if resp.status_code == 404:
                    raise GithubPullRequestNotFound
                else:
                    raise CouldNotFetchPullRequest

            return GithubPullRequestSchema.from_api(resp.json())

    async def fetch_pull_request_commits(
        self,
        identifier: GithubIssueIdentifierSchema
    ) -> list[GithubCommitSchema]:
        url = f"https://api.github.com/repos/{identifier.repo_full_name}/pulls/{identifier.issue_number}/commits"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._request_headers)
            return [
                GithubCommitSchema(
                    sha=commit["sha"],
                    message=commit["commit"]["message"],
                    author=GithubUserSchema.from_api(commit["author"]),
                )
                for commit in resp.json()
            ]
