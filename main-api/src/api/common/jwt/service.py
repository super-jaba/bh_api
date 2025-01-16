import datetime

from jose import jwt

from .schemas import GetAccessTokenSchema, AccessTokenPayloadSchema


class JWTService:
    _algorithm: str
    _access_token_secret: str

    @classmethod
    def setup(cls, algorithm: str, access_token_secret: str):
        cls._algorithm = algorithm
        cls._access_token_secret = access_token_secret

    @classmethod
    def get_access_token(cls, data: GetAccessTokenSchema, exp_minutes: int = 60 * 7) -> str:
        """
        Generates a JWT token based on the data payload passed and returns it

        Parameters:
            data (AccessTokenInputModel): input for payload generation
            exp_minutes (int): number of minutes the token is expired after
        """
        exp_date = datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
        payload = AccessTokenPayloadSchema(**data.model_dump(), exp=exp_date)
        return jwt.encode(
            payload.model_dump(), cls._access_token_secret, cls._algorithm
        )

    @classmethod
    def parse_access_token(cls, token: str) -> AccessTokenPayloadSchema:
        data: dict = jwt.decode(token, key=cls._access_token_secret)
        return AccessTokenPayloadSchema.model_validate(data)
