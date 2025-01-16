from urllib.parse import urlencode

import httpx

from infrastructure.github.exceptions import LoginFailed


class GithubAuthClient:
    """
    GithubAuthService is responsible for authenticating with GitHub.
    Since it doesn't work with the GitHub's API and has different approach,
    the service is separated from the GithubAPIService.
    """

    _client_id: str | None = None
    _client_secret: str | None = None

    _auth_link: str | None = None

    @classmethod
    def setup(cls, client_id: str, client_secret: str) -> None:
        cls._client_id = client_id
        cls._client_secret = client_secret

        auth_params = {"client_id": cls._client_id}
        cls._auth_link = f"https://github.com/login/oauth/authorize/?{urlencode(auth_params)}"

    @classmethod
    def get_auth_link(cls, redirect_uri: str | None = None) -> str:
        if redirect_uri:
            return f"{cls._auth_link}&{urlencode({'redirect_uri': redirect_uri})}"
        return cls._auth_link

    @classmethod
    async def get_auth_token(cls, code: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": cls._client_id,
                    "client_secret": cls._client_secret,
                    "code": code
                }
            )

            if response.status_code != 200:
                raise LoginFailed

            # TODO: Handle key error (happens seldom)
            return response.json()["access_token"]
