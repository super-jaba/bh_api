from fastapi import FastAPI

from domain.wallet import WalletServiceABC
from impl.wallet import WalletService


def get_service() -> WalletServiceABC:
    return WalletService()


def di_wallet(app: FastAPI) -> None:
    app.dependency_overrides[WalletServiceABC] = get_service
