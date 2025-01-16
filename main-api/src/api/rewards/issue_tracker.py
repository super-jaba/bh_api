class IssueTrackerService:

    @classmethod
    def setup(
        cls,
        secret: str
    ) -> None:
        cls._secret = secret

    @classmethod
    def validate(
        cls,
        secret: str
    ) -> bool:
        return cls._secret == secret