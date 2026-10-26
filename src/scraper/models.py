from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    computed_field,
    model_validator,
)
import re


class Listing(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    id_raw: str
    price_raw: str
    title_raw: str
    detail_raw: list[str] = []
    tags_raw: list[str] = []
    freguesia_raw: str

    @field_validator("id_raw", "title_raw")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v:
            raise ValueError("id and title must not be blank")
        return v

    @computed_field
    @property
    def price(self) -> int | None:
        digits = re.sub(r"\D", "", self.price_raw)
        return int(digits) if digits else None

    @computed_field
    @property
    def rooms(self) -> int | None:
        match = re.search(
            r"T(\d+)", " ".join(self.detail_raw)
        )  # number of rooms is always te first entry in details
        return int(match.group(1)) if match else None  # only the () capture

    @computed_field
    @property
    def sqm(self) -> int | None:
        match = re.search(r"(\d+)\s*m²", " ".join(self.detail_raw))
        return int(match.group(1)) if match else None

    @model_validator(mode="after")
    def price_in_range(self):
        if self.price is not None and not 100 <= self.price <= 50_000:
            raise ValueError("price out of range")
        return self
