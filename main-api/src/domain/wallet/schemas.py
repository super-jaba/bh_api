from uuid import UUID

from pydantic import BaseModel


class WalletDetailSchema(BaseModel):
    user_id: UUID
    total_sats: float


class LightningTransactionSchema(BaseModel):
    checking_id: str
    pending: bool
    amount: float
    memo: str | None = None
    time: int

class InvoiceCreationSchema(BaseModel):
    invoice: str
    checking_id: str