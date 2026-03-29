import yfinance as yf
import pandas as pd
from config import SWING_PERIOD, INTRADAY_PERIOD, INTRADAY_INTERVAL


def fetch_ohlcv(symbol: str, time_horizon: str = "swing") -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    if time_horizon == "intraday":
        df = ticker.history(period=INTRADAY_PERIOD, interval=INTRADAY_INTERVAL)
    else:
        df = ticker.history(period=SWING_PERIOD)
    if df.empty:
        raise ValueError(f"No price data returned for {symbol}")
    return df


def get_latest_price(df: pd.DataFrame) -> float:
    return float(df["Close"].iloc[-1])


def get_returns(df: pd.DataFrame, time_horizon: str = "swing") -> dict[str, float]:
    close = df["Close"]
    latest = close.iloc[-1]

    def pct(n_bars: int) -> float:
        if len(close) < n_bars + 1:
            return 0.0
        past = close.iloc[-(n_bars + 1)]
        return float((latest - past) / past)

    if time_horizon == "intraday":
        return {"1h": pct(1), "4h": pct(4), "1d": pct(min(24, len(close) - 1))}
    else:
        return {"1d": pct(1), "5d": pct(5), "1mo": pct(min(21, len(close) - 1))}
