from pydantic import BaseModel, validator, root_validator
from typing import Literal


QUOTE_LITERAL = Literal[
    "USDT", "USDT.P", "USDTPERP", "BUSD", "BUSD.P", "BUSDPERP", "KRW", "USD", "USD.P"
]

class HedgeData(BaseModel):
    user_name: str
    base: str
    split_level: int
    split_value: float | None = None
    amount: float | None = None
    hedge: str

    @root_validator(pre=True)
    def root_validate(cls, values):
        for key, value in values.items():
            if key in ("base", "quote", "hedge"):
                values[key] = value.upper()
        return values
