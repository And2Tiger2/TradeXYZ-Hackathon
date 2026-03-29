import json
from agents import call_llm
from schemas.outputs import MacroOutput

SYSTEM_PROMPT = """You are a macro-economic analyst on a trading desk.
You are given key US macroeconomic indicators sourced from the Federal Reserve (FRED).
Your job: assess the current macro regime and its implications for the specific asset being analyzed.

Guidelines:
- Yield curve (T10Y-T2Y): deeply negative (< -0.3) signals recession risk; positive = expansion
- Fed Funds Rate trend: rising = tightening (risk-off for risk assets), falling = easing (risk-on)
- CPI YoY > 4%: high inflation; if also unemployment > 5%, stagflation
- Unemployment trending up: economic weakening
- For crypto (BTC/ETH): macro regime matters but crypto also has its own cycle; note when crypto may diverge
- For SPY: macro regime is highly direct
- For AAPL: mid-ground — sensitive to rates and consumer sentiment

Return ONLY valid JSON:
{
  "macro_regime": "expansion" | "tightening" | "easing" | "high_inflation" | "stagflation" | "inversion_risk" | "unknown",
  "regime_confidence": <float 0.0-1.0>,
  "risk_appetite": "risk-on" | "risk-off" | "neutral",
  "implications_for_asset": "<1-2 sentence assessment specific to this asset>",
  "macro_tailwinds": ["<tailwind>", ...],
  "macro_headwinds": ["<headwind>", ...],
  "macro_risk_adjustment": <float -0.3 to +0.3>
}

macro_risk_adjustment: positive = macro favors a position, negative = macro is a headwind."""


def run(macro_context: dict, symbol: str, time_horizon: str) -> MacroOutput:
    payload = {
        "symbol": symbol,
        "time_horizon": time_horizon,
        "macro_indicators": macro_context,
    }
    user_message = (
        f"Analyze macro conditions and their implications for {symbol}:\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
    return call_llm(SYSTEM_PROMPT, user_message, MacroOutput)
