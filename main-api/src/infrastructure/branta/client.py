import httpx

class BrantaClient:
    _url_base: str = ""
    _api_key:  str = ""

    @classmethod
    def setup(cls, url_base: str, api_key: str) -> None:
        cls._url_base = url_base
        cls._api_key = api_key

    @classmethod
    async def verify_invoice(cls, invoice: str) -> bool:
        if cls._url_base == "" or cls._api_key == "":
            raise Exception("Branta client not set up")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://{cls._url_base}/v1/payments",
                    headers={
                        "API_KEY": cls._api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "payment": {
                            "description": "Account Deposit",
                            "merchant": "Lightning Bounties",
                            "payment": invoice,
                            "ttl": "86400",
                        }
                    }
                )
            if response.status_code != 201:
                raise Exception("Branta did not return 201")
            return True
        except Exception as e:
            raise Exception(f"Branta API call failed: {e}")
        