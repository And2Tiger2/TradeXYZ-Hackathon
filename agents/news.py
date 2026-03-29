import json
from agents import call_llm
from schemas.outputs import NewsOutput

SYSTEM_PROMPT = """You are a financial news and market sentiment analyst.
You will be given a list of recent news headlines about an asset.
Summarize the overall sentiment and identify the key bullish and bearish drivers.
Use only what is provided. Do not invent facts or reference outside knowledge.
Provide 1-3 positive drivers and 1-3 negative drivers.

Return ONLY valid JSON with no additional text:
{
  "bias": "bullish" | "bearish" | "neutral",
  "confidence": <float 0.0-1.0>,
  "headline_summary": "<1-2 sentence summary>",
  "positive_drivers": ["<driver>", ...],
  "negative_drivers": ["<driver>", ...],
  "suggested_action": "long" | "short" | "hold"
}"""


def run(symbol: str, headlines: list[str]) -> NewsOutput:
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    user_message = f"Asset: {symbol}\n\nRecent headlines:\n{headlines_text}\n\nReturn your sentiment assessment."
    return call_llm(SYSTEM_PROMPT, user_message, NewsOutput)
