from uuid import UUID

from pydantic import BaseModel, Field


class IssueLightningWalletDTO(BaseModel):
    issue_id: UUID
    wallet_id: str = Field(..., max_length=32)
    adminkey: str = Field(..., max_length=32)
    inkey: str = Field(..., max_length=32)
