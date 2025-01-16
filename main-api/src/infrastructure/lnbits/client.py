import httpx

from domain.common.schemas import PaginationSchema
from domain.wallet.schemas import LightningTransactionSchema, InvoiceCreationSchema
from infrastructure.lnbits.exceptions import (
    AccountCreationFailure,
    WalletCreationFailure,
    WalletFetchFailure,
    CreateInvoiceFailure,
    BadResponseBody,
    PayInvoiceFailure,
    NotEnoughSats,
    InvoiceIsAlreadyPaid,
    CouldNotDecodeInvoiceException
)
from infrastructure.lnbits.schemas import (
    LightningAccountSchema,
    LightningWalletCredentialsSchema,
    LightningWalletSchema,
    DecodedInvoice
)


class LNBitsClient:
    _url_base: str
    
    @classmethod
    def setup(cls, url_base: str) -> None:
        cls._url_base = url_base

    def _get_header(self, auth_key: str) -> dict:
        """
        Builds a proper header for LNBits API requests
        :param auth_key: Either in- or admin-key of the wallet
        :return: dict
        """
        return {
            "X-Api-Key": auth_key
        }

    async def create_account(self, name: str) -> LightningAccountSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self._url_base}/api/v1/account",
                json={
                    "name": name
                }
            )
            if response.status_code != 200:
                raise AccountCreationFailure
            return LightningAccountSchema.model_validate(response.json())

    async def create_wallet(self, account_api_key: str, name: str) -> LightningWalletCredentialsSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self._url_base}/api/v1/wallet",
                headers=self._get_header(account_api_key),
                json={
                    "name": name
                }
            )
            if response.status_code != 200:
                raise WalletCreationFailure
            return LightningWalletCredentialsSchema.model_validate(response.json())

    async def create_headless_wallet(self, name: str) -> LightningWalletCredentialsSchema:
        """
        Works the same as **create_wallet** method but instead of creating a wallet for a specified account,
        it creates a new account, creates new wallet for it and then disregards the account details
        so the wallet is accessible only through its keys
        :param name: Wallet name
        :return:
        """
        try:
            api_key = (await self.create_account("ghost")).adminkey
        except AccountCreationFailure:
            raise WalletCreationFailure

        return await self.create_wallet(api_key, name)

    async def get_wallet(self, inkey: str) -> LightningWalletSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self._url_base}/api/v1/wallet",
                headers=self._get_header(inkey)
            )
            if response.status_code != 200:
                raise WalletFetchFailure

            return LightningWalletSchema.model_validate(response.json())

    async def create_invoice(self, inkey: str, amount_sats: int, memo: str = "") -> InvoiceCreationSchema:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self._url_base}/api/v1/payments",
                headers=self._get_header(inkey),
                json={
                    "out": False,
                    "amount": amount_sats,
                    "memo": memo
                }
            )

            if response.status_code != 201:
                raise CreateInvoiceFailure

            try:
                data = response.json()
                return InvoiceCreationSchema(
                    invoice=data["payment_request"],
                    checking_id=data["checking_id"]
                )
            except KeyError:
                raise BadResponseBody

    async def pay_invoice(self, adminkey: str, invoice: str) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self._url_base}/api/v1/payments",
                headers=self._get_header(adminkey),
                json={
                    "out": True,
                    "bolt11": invoice
                }
            )

            if response.status_code == 403:
                raise NotEnoughSats

            if response.status_code == 520:
                raise InvoiceIsAlreadyPaid

            if response.status_code != 201:
                raise PayInvoiceFailure

    async def decode_invoice(self, invoice: str) -> DecodedInvoice:
        async with httpx.AsyncClient() as client:
            body = {
                "data": invoice
            }
            response = await client.post(
                f"https://{self._url_base}/api/v1/payments/decode",
                json=body
            )
            if response.status_code != 200:
                raise CouldNotDecodeInvoiceException
            return DecodedInvoice(**response.json())

    async def get_wallet_history(
        self,
        inkey: str,
        pagination: PaginationSchema
    ) -> list[LightningTransactionSchema]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self._url_base}/api/v1/payments",
                headers=self._get_header(inkey),
                params={
                    "offset": pagination.skip,
                    "limit": pagination.limit
                }
            )
            return [
                LightningTransactionSchema(
                    checking_id=entry["checking_id"],
                    pending=entry["pending"],
                    amount=entry["amount"] / 1000,  # In sats, not msats
                    memo=entry["memo"],
                    time=entry["time"]
                )
                for entry in response.json()
            ]

    async def move_sats(
        self,
        from_wallet_adminkey: str,
        to_wallet_inkey: str,
        amount: int
    ):
        """
        Transfers sats from one wallet to another.
        :param from_wallet_adminkey: Adminkey of the wallet to move sats from
        :param to_wallet_inkey: Inkey of the wallet to send sats to
        :param amount: Amount of sats to transfer
        :return: None
        """

        # TODO: Handle exceptions

        invoice = await self.create_invoice(inkey=to_wallet_inkey, amount_sats=amount)
        await self.pay_invoice(
            adminkey=from_wallet_adminkey,
            invoice=invoice.invoice
        )
