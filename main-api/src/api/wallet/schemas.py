from uuid import UUID

from pydantic import BaseModel, Field


class DepositRequestSchema(BaseModel):
    amount_sats: int = Field(..., gt=0)


class DepositResponseSchema(BaseModel):
    invoice: str
    checking_id: str


class WithdrawRequestSchema(BaseModel):
    invoice: str


class WithdrawResponseSchema(BaseModel):
    success: bool


class WalletDetailResponse(BaseModel):
    user_id: UUID
    free_sats: int
    in_rewards: int
