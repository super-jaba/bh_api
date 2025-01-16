from typing import Self

from pydantic import BaseModel, model_validator, Field


class Pagination(BaseModel):
    skip: int = Field(0)
    limit: int | None = Field(None)


class UpdateDTO(BaseModel):
    @model_validator(mode="after")
    def check_if_not_all_fields_are_none(self) -> Self:
        if self.model_dump(exclude_unset=True) == {}:
            msg = "At least one updatable field has to be passed."
            raise ValueError(msg)
        return self
