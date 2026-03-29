import json
from typing import Optional
from agents import call_llm
from schemas.outputs import TechnicalOutput, NewsOutput, RiskOutput, MacroOutput, PortfolioOutput

SYSTEM_PROMPT = """You are the portfolio manager and final decision maker on a trading desk.
You receive structured reports from a technical analyst, news analyst, risk manager, and optionally a macro analyst.
Your job: synthesize these into one final trade recommendation.

Hard rules you must follow:
- If risk_manager.approved is false, you MUST set final_action="hold" and position_size_pct=0.
- If risk_manager.override_action is "hold", you MUST output final_action="hold".
- Never recommend position_size_pct larger than risk_manager.max_position_pct.
- Never recommend max_leverage larger than risk_manager.max_leverage.
- Default to "hold" when agent signals are mixed or average confidence is below 0.55.
- If macro analyst is present and risk_appetite is "risk-off", reduce position size and be more cautious.
- Be honest about uncertainty. Do not force bullish conviction.

Provide 2-4 entry_rationale bullets and 2-3 key_risks bullets.
Set why_not_hold only when final_action is long or short — explain why acting beats waiting.

Return ONLY valid JSON:
{
  "final_action": "long" | "short" | "hold",
  "confidence": <float 0.0-1.0>,
  "position_size_pct": <float 0.0-1.0>,
  "max_leverage": <float>,
  "entry_rationale": ["<reason>", ...],
  "stop_loss_pct": <float or null>,
  "take_profit_pct": <float or null>,
  "key_risks": ["<risk>", ...],
  "why_not_hold": "<reason>" | null
}"""


def run(
    technical: TechnicalOutput,
    news: NewsOutput,
    risk: RiskOutput,
    user_constraints: dict,
    macro: Optional[MacroOutput] = None,
) -> PortfolioOutput:
    payload = {
        "technical_analyst": technical.model_dump(),
        "news_analyst": news.model_dump(),
        "risk_manager": risk.model_dump(),
        "user_constraints": user_constraints,
    }
    if macro is not None:
        payload["macro_analyst"] = macro.model_dump()

    user_message = f"Make the final trade decision:\n\n{json.dumps(payload, indent=2)}"
    return call_llm(SYSTEM_PROMPT, user_message, PortfolioOutput)


def enforce_constraints(
    output: PortfolioOutput,
    max_risk_per_trade_pct: float,
    max_leverage: float,
) -> PortfolioOutput:
    """Hard code-enforced constraints — the LLM cannot override these."""
    output.position_size_pct = min(output.position_size_pct, max_risk_per_trade_pct * 10)
    output.max_leverage = min(output.max_leverage, max_leverage)
    if output.confidence < 0.50:
        output.final_action = "hold"
        output.position_size_pct = 0.0
        output.max_leverage = 0.0
    return output
