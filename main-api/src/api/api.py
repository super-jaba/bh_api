from fastapi import APIRouter

from . import auth, users, wallet, issues, repositories, rewards


router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(users.router, prefix="/users")
router.include_router(wallet.router, prefix="/wallet")
router.include_router(issues.router, prefix="/issues")
router.include_router(repositories.router, prefix="/repositories")
router.include_router(rewards.router, prefix="/rewards")
