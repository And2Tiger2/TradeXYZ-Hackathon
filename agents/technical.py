import json
from agents import call_llm
from schemas.outputs import TechnicalOutput

SYSTEM_PROMPT = """You are a quantitative technical analyst.
Given current market statistics for a single asset, determine the short-term directional bias.
Consider only: price trend relative to SMAs, momentum (recent returns), overbought/oversold (RSI), and volatility.
Do not reference fundamentals or news.
Be concise and objective. Provide 2-4 signals and 1-3 risks.

Return ONLY valid JSON with no additional text:
{
  "bias": "bullish" | "bearish" | "neutral",
  "confidence": <float 0.0-1.0>,
  "signals": ["<signal>", ...],
  "risks": ["<risk>", ...],
  "suggested_action": "long" | "short" | "hold"
}"""


def run(market_context: dict) -> TechnicalOutput:
    user_message = f"Analyze the following market data and return your technical assessment:\n\n{json.dumps(market_context, indent=2)}"
    return call_llm(SYSTEM_PROMPT, user_message, TechnicalOutput)
