import json
import anthropic
from pydantic import BaseModel
from config import ANTHROPIC_API_KEY, LLM_MODEL

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_llm(system_prompt: str, user_message: str, schema: type[BaseModel]) -> BaseModel:
    """Call Claude, parse JSON response, validate with Pydantic schema."""
    client = _get_client()
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    parsed = json.loads(raw_text)
    return schema(**parsed)
