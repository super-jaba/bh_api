from pydantic import BaseModel, ConfigDict, Field


class APISchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class LightningAccountSchema(APISchema):
    id: str
    name: str
    adminkey: str

    # Other fields exist but are not used at the moment


class LightningWalletCredentialsSchema(APISchema):
    id: str = Field(..., max_length=32)
    adminkey: str = Field(..., max_length=32)
    inkey: str = Field(..., max_length=32)
    balance_msat: int = Field(..., ge=0)


class LightningWalletSchema(APISchema):
    """
    **name**: Name of the wallet

    **balance**: Balance in msat
    """
    name: str
    balance: float


class DecodedInvoice(APISchema):
    amount_msat: int = Field(..., gt=0)
