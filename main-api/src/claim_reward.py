import sys
import asyncio

import config
from infrastructure import setup_infrastructure
from infrastructure.config import DatabaseConfig, LNBitsConfig, GithubConfig

from impl.rewards.service import RewardService
from domain.rewards.schemas import ContributorSchema

"""
Run this script with args: <issue_id> (UUID) <winner_github_id> (int)
    > python src/claim_reward.py '05b130ae-1f9e-4683-ba81-74efdb5659e2' 171499163 
"""


async def main(issue_id, contributor_github_id):


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
        )
    )
    
    contributor = ContributorSchema(
        github_id=contributor_github_id,
        github_username="dummy-value",
    )

    reward_service = RewardService()
    
    result = await reward_service.reward_contributor(
        contributor=contributor,
        issue_id=issue_id,
    )
    
    print("Success calling reward_contributor(). Completion schema:")
    print(result.model_dump())
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception("supply the script two args: <issue_id> <contributor_github_id>")
    issue_id = sys.argv[1]
    contributor_github_id = int(sys.argv[2])
    asyncio.run(main(issue_id, contributor_github_id))
