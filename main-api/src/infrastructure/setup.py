from .config import DatabaseConfig, LNBitsConfig, GithubConfig, BrantaConfig
from .database import init_db
from .github import GithubAuthClient
from .lnbits.client import LNBitsClient
from .branta import BrantaClient


async def setup_infrastructure(
    database_config: DatabaseConfig,
    lnbits_config: LNBitsConfig,
    github_config: GithubConfig,
    branta_config: BrantaConfig
):
    await init_db(
        host=database_config.host,
        port=database_config.port,
        database=database_config.database,
        user=database_config.user,
        password=database_config.password
    )

    LNBitsClient.setup(lnbits_config.node_url)

    GithubAuthClient.setup(
        client_id=github_config.client_id,
        client_secret=github_config.client_secret
    )

    BrantaClient.setup(
        url_base=branta_config.url_base,
        api_key=branta_config.api_key
    )
