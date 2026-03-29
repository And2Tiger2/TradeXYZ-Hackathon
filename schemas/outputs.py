from pydantic import BaseModel, Field
from typing import Optional, Literal


class TechnicalOutput(BaseModel):
    bias: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0)
    signals: list[str]
    risks: list[str]
    suggested_action: Literal["long", "short", "hold"]


class NewsOutput(BaseModel):
    bias: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(ge=0.0, le=1.0)
    headline_summary: str
    positive_drivers: list[str]
    negative_drivers: list[str]
    suggested_action: Literal["long", "short", "hold"]


class RiskOutput(BaseModel):
    risk_rating: Literal["low", "medium", "high"]
    approved: bool
    max_position_pct: float = Field(ge=0.0, le=1.0)
    max_leverage: float = Field(ge=0.0)
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    warnings: list[str]
    override_action: Optional[Literal["hold"]] = None


class MacroOutput(BaseModel):
    macro_regime: Literal[
        "expansion", "tightening", "easing",
        "high_inflation", "stagflation", "inversion_risk", "unknown"
    ]
    regime_confidence: float = Field(ge=0.0, le=1.0)
    risk_appetite: Literal["risk-on", "risk-off", "neutral"]
    implications_for_asset: str
    macro_tailwinds: list[str]
    macro_headwinds: list[str]
    macro_risk_adjustment: float = Field(ge=-0.3, le=0.3)


class PortfolioOutput(BaseModel):
    final_action: Literal["long", "short", "hold"]
    confidence: float = Field(ge=0.0, le=1.0)
    position_size_pct: float = Field(ge=0.0, le=1.0)
    max_leverage: float = Field(ge=0.0)
    entry_rationale: list[str]
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    key_risks: list[str]
    why_not_hold: Optional[str] = None
