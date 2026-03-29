import json
from agents import call_llm
from schemas.outputs import TechnicalOutput, NewsOutput, RiskOutput

SYSTEM_PROMPT = """You are a senior trading risk manager. Capital preservation is your primary mandate.
You are given structured reports from a technical analyst and a news analyst, plus the user's risk constraints.
Your job: determine whether a trade is safe to execute, and at what maximum size and leverage.

Rules:
- You MAY veto the trade by setting approved=false and override_action="hold".
- When technical and news signals conflict or confidence is low, reduce size and leverage.
- When volatility is high (>0.5 annualized), reduce max_position_pct and max_leverage.
- Always set a stop_loss_pct. Typical range: 0.01-0.05 (1%-5%).
- Take profit should be at least 1.5x the stop loss distance.
- Provide 1-3 actionable warnings.

Return ONLY valid JSON with no additional text:
{
  "risk_rating": "low" | "medium" | "high",
  "approved": true | false,
  "max_position_pct": <float 0.0-1.0>,
  "max_leverage": <float>,
  "stop_loss_pct": <float or null>,
  "take_profit_pct": <float or null>,
  "warnings": ["<warning>", ...],
  "override_action": "hold" | null
}"""


def run(
    technical: TechnicalOutput,
    news: NewsOutput,
    risk_constraints: dict,
    market_context: dict,
) -> RiskOutput:
    payload = {
        "technical_analysis": technical.model_dump(),
        "news_analysis": news.model_dump(),
        "risk_constraints": risk_constraints,
        "market_volatility": market_context.get("technical", {}).get("volatility_20d_annualized"),
    }
    user_message = f"Assess the risk and approve or veto this trade:\n\n{json.dumps(payload, indent=2)}"
    return call_llm(SYSTEM_PROMPT, user_message, RiskOutput)
