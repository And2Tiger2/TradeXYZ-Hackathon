"""
Finnhub API integration for real-time quotes and company fundamentals.
All calls are optional — returns None gracefully if key is missing or request fails.
"""
import requests
from config import FINNHUB_API_KEY, CRYPTO_SYMBOLS

_BASE = "https://finnhub.io/api/v1"

_SYMBOL_MAP = {
    "BTC-USD": "BINANCE:BTCUSDT",
    "ETH-USD": "BINANCE:ETHUSDT",
}


def _fh_symbol(symbol: str) -> str:
    return _SYMBOL_MAP.get(symbol, symbol)


def get_realtime_quote(symbol: str) -> dict | None:
    """
    Real-time quote from Finnhub.
    Returns dict with current, open, high, low, prev_close, change_pct — or None.
    """
    if not FINNHUB_API_KEY:
        return None
    try:
        resp = requests.get(
            f"{_BASE}/quote",
            params={"symbol": _fh_symbol(symbol), "token": FINNHUB_API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        d = resp.json()
        if not d.get("c"):
            return None
        pc = d.get("pc") or d.get("c")
        return {
            "current": d["c"],
            "open": d.get("o"),
            "high": d.get("h"),
            "low": d.get("l"),
            "prev_close": pc,
            "change_pct": (d["c"] - pc) / pc if pc else 0.0,
        }
    except Exception:
        return None


def get_company_profile(symbol: str) -> dict | None:
    """Company fundamentals for equities (market cap, PE, industry, etc.)."""
    if not FINNHUB_API_KEY or symbol in CRYPTO_SYMBOLS:
        return None
    try:
        resp = requests.get(
            f"{_BASE}/stock/profile2",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        d = resp.json()
        return d if d.get("name") else None
    except Exception:
        return None


def get_earnings_surprise(symbol: str) -> list | None:
    """Last 4 earnings surprises for individual stocks (not ETFs or crypto)."""
    if not FINNHUB_API_KEY or symbol in CRYPTO_SYMBOLS or symbol == "SPY":
        return None
    try:
        resp = requests.get(
            f"{_BASE}/stock/earnings",
            params={"symbol": symbol, "token": FINNHUB_API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        return data[:4] if data else None
    except Exception:
        return None
