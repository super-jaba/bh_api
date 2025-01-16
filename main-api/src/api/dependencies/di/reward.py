from fastapi import FastAPI

from domain.rewards import RewardServiceABC
from impl.rewards import RewardService


def get_service() -> RewardServiceABC:
    return RewardService()


def di_reward(app: FastAPI) -> None:
    app.dependency_overrides[RewardServiceABC] = get_service
