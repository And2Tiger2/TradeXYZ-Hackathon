"""
Mean-variance portfolio optimization constrained by agent directional signals.
Uses scipy.optimize (no extra heavy deps).
"""
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from config import RISK_FREE_RATE


def fetch_multi_returns(symbols: list[str], period: str = "6mo") -> pd.DataFrame:
    """Fetch daily close-to-close returns for multiple symbols."""
    prices: dict[str, pd.Series] = {}
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(period=period)
            if not hist.empty:
                prices[sym] = hist["Close"]
        except Exception:
            pass
    if not prices:
        return pd.DataFrame()
    df = pd.DataFrame(prices).dropna()
    return df.pct_change().dropna()


def optimize_portfolio(
    returns: pd.DataFrame,
    agent_signals: dict[str, str],       # symbol → "long" | "short" | "hold"
    agent_confidences: dict[str, float], # symbol → 0.0–1.0
) -> dict:
    """
    Max-Sharpe and Min-Variance optimization over symbols with "long" signal.
    Confidence scores scale each symbol's expected return.

    Returns
    -------
    dict with:
      weights_max_sharpe, weights_min_variance  — {symbol: weight}
      portfolio_return, portfolio_volatility, sharpe_ratio
      eligible_symbols, expected_returns, correlation_matrix
    """
    symbols = list(returns.columns)
    eligible = [s for s in symbols if agent_signals.get(s) == "long"]

    zero_weights = {s: 0.0 for s in symbols}
    if not eligible:
        return {
            "weights_max_sharpe": zero_weights,
            "weights_min_variance": zero_weights,
            "portfolio_return": 0.0,
            "portfolio_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "eligible_symbols": [],
            "expected_returns": {},
            "correlation_matrix": {},
        }

    ret_e = returns[eligible]
    mu = ret_e.mean() * 252           # annualized expected returns
    cov = ret_e.cov() * 252           # annualized covariance

    # Scale expected returns by agent confidence
    for sym in eligible:
        mu[sym] *= 0.5 + agent_confidences.get(sym, 0.5)

    n = len(eligible)
    w0 = np.full(n, 1.0 / n)
    bounds = [(0.0, 1.0)] * n
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    cov_arr = cov.values

    if n == 1:
        w_sharpe = w_minvar = w0
    else:
        def neg_sharpe(w):
            r = float(np.dot(w, mu.values))
            v = float(np.sqrt(w @ cov_arr @ w))
            return -(r - RISK_FREE_RATE) / v if v > 1e-8 else 0.0

        def port_vol(w):
            return float(np.sqrt(w @ cov_arr @ w))

        res_sharpe = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)
        res_minvar = minimize(port_vol,   w0, method="SLSQP", bounds=bounds, constraints=constraints)
        w_sharpe = res_sharpe.x if res_sharpe.success else w0
        w_minvar = res_minvar.x if res_minvar.success else w0

    weights_sharpe = {s: float(w) for s, w in zip(eligible, w_sharpe)}
    weights_minvar = {s: float(w) for s, w in zip(eligible, w_minvar)}

    # Full dicts including non-eligible at 0
    all_sharpe = {**zero_weights, **weights_sharpe}
    all_minvar = {**zero_weights, **weights_minvar}

    port_ret = float(np.dot(w_sharpe, mu.values))
    port_vol_val = float(np.sqrt(w_sharpe @ cov_arr @ w_sharpe)) if n > 1 else float(np.sqrt(cov_arr[0, 0]))
    sharpe = (port_ret - RISK_FREE_RATE) / port_vol_val if port_vol_val > 1e-8 else 0.0

    return {
        "weights_max_sharpe": all_sharpe,
        "weights_min_variance": all_minvar,
        "portfolio_return": round(port_ret, 4),
        "portfolio_volatility": round(port_vol_val, 4),
        "sharpe_ratio": round(sharpe, 3),
        "eligible_symbols": eligible,
        "expected_returns": mu.to_dict(),
        "correlation_matrix": ret_e.corr(),  # DataFrame, used for sim + heatmap
    }
