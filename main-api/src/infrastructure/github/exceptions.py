from infrastructure.common.exceptions import InfrastructureException


class GithubException(InfrastructureException):
    """Base class for GitHub related exceptions"""
    pass


class LoginFailed(GithubException):
    pass


class CouldNotFetchGithubUser(GithubException):
    pass


class GithubIssueIsAlreadyClosed(GithubException):
    pass


class GithubPullRequestNotFound(GithubException):
    pass


class CouldNotFetchPullRequest(GithubException):
    pass
