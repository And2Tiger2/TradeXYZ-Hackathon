import requests
from config import NEWS_API_KEY, SYMBOL_MAP, NEWS_HEADLINE_COUNT


def fetch_headlines(symbol: str, n: int = NEWS_HEADLINE_COUNT) -> list[str]:
    """Fetch recent news headlines for a symbol. Returns list of headline strings."""
    query = SYMBOL_MAP.get(symbol, symbol)

    if NEWS_API_KEY:
        headlines = _fetch_from_newsapi(query, n)
        if headlines:
            return headlines

    # Fallback: return placeholder so news agent still runs
    return [f"No live headlines available for {symbol}. Analysis based on technical data only."]


def _fetch_from_newsapi(query: str, n: int) -> list[str]:
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": n,
            "apiKey": NEWS_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        headlines = []
        for a in articles:
            title = a.get("title", "").strip()
            description = a.get("description", "")
            if title and title != "[Removed]":
                text = title
                if description:
                    text += f" — {description[:120]}"
                headlines.append(text)
        return headlines[:n]
    except Exception:
        return []
