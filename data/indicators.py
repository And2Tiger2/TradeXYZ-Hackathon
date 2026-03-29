import pandas as pd
import numpy as np
from config import CRYPTO_SYMBOLS


def compute_sma(df: pd.DataFrame, window: int) -> float:
    close = df["Close"]
    if len(close) < window:
        return float(close.mean())
    return float(close.rolling(window).mean().iloc[-1])


def compute_rsi(df: pd.DataFrame, window: int = 14) -> float:
    close = df["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean().iloc[-1]
    avg_loss = loss.rolling(window).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))


def compute_volatility(
    df: pd.DataFrame, window: int = 20, symbol: str = "", time_horizon: str = "swing"
) -> float:
    """Annualized historical volatility. Uses correct annualization for intraday/crypto."""
    close = df["Close"]
    log_returns = np.log(close / close.shift(1)).dropna()
    if len(log_returns) < window:
        std = float(log_returns.std())
    else:
        std = float(log_returns.rolling(window).std().iloc[-1])

    if time_horizon == "intraday":
        # Hourly bars
        ann_factor = np.sqrt(365 * 24) if symbol in CRYPTO_SYMBOLS else np.sqrt(252 * 6.5)
    else:
        ann_factor = np.sqrt(252)

    return std * ann_factor


def compute_drift(df: pd.DataFrame, symbol: str = "", time_horizon: str = "swing") -> float:
    """Annualized drift (mu) from historical log returns."""
    close = df["Close"]
    log_returns = np.log(close / close.shift(1)).dropna()
    if time_horizon == "intraday":
        factor = 365 * 24 if symbol in CRYPTO_SYMBOLS else 252 * 6.5
    else:
        factor = 252
    return float(log_returns.mean() * factor)


def compute_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """MACD indicator. Returns scalar summary values + full pandas Series for charting."""
    close = df["Close"]
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": round(float(macd_line.iloc[-1]), 6),
        "signal": round(float(signal_line.iloc[-1]), 6),
        "histogram": round(float(histogram.iloc[-1]), 6),
        "crossover": "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish",
        # Full series for charts (not included in JSON context sent to LLM)
        "macd_series": macd_line,
        "signal_series": signal_line,
        "histogram_series": histogram,
    }


def compute_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> dict:
    """Bollinger Bands. Returns scalar summary values + full pandas Series for charting."""
    close = df["Close"]
    sma = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    pct_b = (close - lower) / (upper - lower)
    bandwidth = (upper - lower) / sma
    long_bw = bandwidth.rolling(min(50, len(bandwidth))).mean()

    return {
        "upper": round(float(upper.iloc[-1]), 4),
        "lower": round(float(lower.iloc[-1]), 4),
        "middle": round(float(sma.iloc[-1]), 4),
        "pct_b": round(float(pct_b.iloc[-1]), 4),      # 0 = at lower band, 1 = at upper band
        "bandwidth": round(float(bandwidth.iloc[-1]), 4),
        "squeeze": bool(float(bandwidth.iloc[-1]) < float(long_bw.iloc[-1]) * 0.8),
        # Full series for charts
        "upper_series": upper,
        "lower_series": lower,
        "middle_series": sma,
        "pct_b_series": pct_b,
    }


def build_market_context(
    symbol: str, df: pd.DataFrame, returns: dict, time_horizon: str = "swing"
) -> dict:
    """Build the JSON-serializable market context sent to the LLM agents."""
    macd = compute_macd(df)
    bb = compute_bollinger_bands(df)

    return {
        "symbol": symbol,
        "time_horizon": time_horizon,
        "current_price": round(float(df["Close"].iloc[-1]), 4),
        "returns": {k: round(v, 4) for k, v in returns.items()},
        "technical": {
            "sma_20": round(compute_sma(df, 20), 4),
            "sma_50": round(compute_sma(df, 50), 4),
            "rsi_14": round(compute_rsi(df), 2),
            "volatility_20d_annualized": round(
                compute_volatility(df, symbol=symbol, time_horizon=time_horizon), 4
            ),
            "macd": {
                "macd": macd["macd"],
                "signal": macd["signal"],
                "histogram": macd["histogram"],
                "crossover": macd["crossover"],
            },
            "bollinger_bands": {
                "upper": bb["upper"],
                "lower": bb["lower"],
                "middle": bb["middle"],
                "pct_b": bb["pct_b"],
                "bandwidth": bb["bandwidth"],
                "squeeze": bb["squeeze"],
            },
        },
    }
