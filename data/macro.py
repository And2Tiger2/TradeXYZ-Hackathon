"""
FRED macro data + VIX. All fetches are optional — returns gracefully if keys are missing.
"""
import requests
import yfinance as yf
from config import FRED_API_KEY

_FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def _fetch_series(series_id: str, limit: int = 13) -> list[tuple[str, float]]:
    resp = requests.get(
        _FRED_BASE,
        params={
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        },
        timeout=8,
    )
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    return [
        (o["date"], float(o["value"]))
        for o in obs
        if o.get("value") not in (".", "", None)
    ]


def fetch_vix() -> float | None:
    try:
        hist = yf.Ticker("^VIX").history(period="2d")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 2)
    except Exception:
        pass
    return None


def fetch_macro_context() -> dict:
    """
    Fetch key US macro indicators from FRED.
    Returns {"available": False} if FRED_API_KEY is not set or all requests fail.
    """
    if not FRED_API_KEY:
        return {"available": False}

    result: dict = {"available": False}

    try:
        # ── Yield curve (10yr – 2yr) ─────────────────────────────────────────
        yc = _fetch_series("T10Y2Y", 3)
        if yc:
            result["yield_curve_10y2y"] = {
                "latest_date": yc[0][0],
                "latest_value": round(yc[0][1], 3),
                "prev_value": round(yc[1][1], 3) if len(yc) > 1 else None,
                "inverted": yc[0][1] < 0,
            }
    except Exception:
        pass

    try:
        # ── Fed Funds Rate ───────────────────────────────────────────────────
        ffr = _fetch_series("FEDFUNDS", 3)
        if ffr:
            trend = "flat"
            if len(ffr) > 1:
                trend = "rising" if ffr[0][1] > ffr[1][1] else ("falling" if ffr[0][1] < ffr[1][1] else "flat")
            result["fed_funds_rate"] = {
                "latest_date": ffr[0][0],
                "latest_value": round(ffr[0][1], 3),
                "prev_value": round(ffr[1][1], 3) if len(ffr) > 1 else None,
                "trend": trend,
            }
    except Exception:
        pass

    try:
        # ── CPI — compute YoY from 13 monthly observations ──────────────────
        cpi = _fetch_series("CPIAUCSL", 13)
        if len(cpi) >= 13:
            yoy = (cpi[0][1] - cpi[12][1]) / cpi[12][1] * 100
            result["cpi"] = {
                "latest_date": cpi[0][0],
                "latest_value": round(cpi[0][1], 2),
                "yoy_pct": round(yoy, 2),
            }
    except Exception:
        pass

    try:
        # ── Unemployment Rate ────────────────────────────────────────────────
        unrate = _fetch_series("UNRATE", 3)
        if unrate:
            trend = "flat"
            if len(unrate) > 1:
                trend = "rising" if unrate[0][1] > unrate[1][1] else ("falling" if unrate[0][1] < unrate[1][1] else "flat")
            result["unemployment"] = {
                "latest_date": unrate[0][0],
                "latest_value": round(unrate[0][1], 2),
                "prev_value": round(unrate[1][1], 2) if len(unrate) > 1 else None,
                "trend": trend,
            }
    except Exception:
        pass

    try:
        # ── 10yr Breakeven Inflation ─────────────────────────────────────────
        bei = _fetch_series("T10YIE", 2)
        if bei:
            result["breakeven_inflation"] = {
                "latest_date": bei[0][0],
                "latest_value": round(bei[0][1], 3),
            }
    except Exception:
        pass

    result["available"] = any(
        k in result for k in ("yield_curve_10y2y", "fed_funds_rate", "cpi", "unemployment")
    )
    if result["available"]:
        result["regime"] = _detect_regime(result)

    return result


def _detect_regime(ctx: dict) -> str:
    yc_val = ctx.get("yield_curve_10y2y", {}).get("latest_value")
    ffr_trend = ctx.get("fed_funds_rate", {}).get("trend")
    cpi_yoy = ctx.get("cpi", {}).get("yoy_pct")
    unrate = ctx.get("unemployment", {}).get("latest_value")

    if yc_val is not None and yc_val < -0.3:
        return "inversion_risk"
    if ffr_trend == "rising":
        return "tightening"
    if ffr_trend == "falling":
        return "easing"
    if cpi_yoy is not None and cpi_yoy > 4.0:
        if unrate is not None and unrate > 5.0:
            return "stagflation"
        return "high_inflation"
    return "expansion"
