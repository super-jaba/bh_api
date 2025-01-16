import asyncio

import config
from api import run_api, APIConfig, JWTSettings
from api.config import IssueTrackerSettings
from infrastructure import setup_infrastructure
from infrastructure.config import (
    DatabaseConfig, 
    LNBitsConfig, 
    GithubConfig, 
    BrantaConfig
)


async def main():

    await setup_infrastructure(
        database_config=DatabaseConfig(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_DATABASE,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        ),

        lnbits_config=LNBitsConfig(
            node_url=config.LIGHTNING_BASE_URL
        ),

        github_config=GithubConfig(
            client_id=config.GITHUB_CLIENT_ID,
            client_secret=config.GITHUB_CLIENT_SECRET
        ),

        branta_config=BrantaConfig(
            url_base=config.BRANTA_BASE_URL,
            api_key=config.BRANTA_API_KEY
        )
    )

    await run_api(
        host=config.APP_HOST,
        port=config.APP_PORT,
        config=APIConfig(
            enable_docs=config.DEBUG,
            jwt_settings=JWTSettings(
                access_token_secret=config.JWT_ACCESS_TOKEN_SECRET
            ),
            issue_tracker_settings=IssueTrackerSettings(
                secret=config.ISSUE_TRACKER_SECRET
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
