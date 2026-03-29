from pydantic import BaseModel, Field
from typing import Literal


class UserInput(BaseModel):
    symbol: str
    time_horizon: Literal["intraday", "swing"]
    account_size: float = Field(gt=0)
    risk_mode: Literal["aggressive", "balanced", "conservative"]
    max_risk_per_trade_pct: float = Field(gt=0, le=0.20)  # e.g. 0.01 = 1%
    max_leverage: float = Field(ge=1.0, le=20.0)
