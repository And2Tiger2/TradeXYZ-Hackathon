"""
Monte Carlo simulation using Geometric Brownian Motion (GBM).
Supports single-asset and correlated multi-asset (Cholesky) portfolio simulation.
"""
import numpy as np
import pandas as pd
from config import MC_N_PATHS, CRYPTO_SYMBOLS


def _dt(symbol: str, time_horizon: str) -> float:
    """Time step size in years for one bar."""
    if time_horizon == "intraday":
        return 1 / (365 * 24) if symbol in CRYPTO_SYMBOLS else 1 / (252 * 6.5)
    return 1 / 252


def run_gbm_simulation(
    current_price: float,
    mu: float,
    sigma: float,
    horizon: int,
    symbol: str = "",
    time_horizon: str = "swing",
    n_paths: int = MC_N_PATHS,
) -> dict:
    """
    Single-asset GBM Monte Carlo.

    Parameters
    ----------
    current_price : current asset price
    mu            : annualized drift
    sigma         : annualized volatility
    horizon       : steps forward (hours for intraday, days for swing)
    """
    dt = _dt(symbol, time_horizon)
    drift = (mu - 0.5 * sigma ** 2) * dt
    diffusion = sigma * np.sqrt(dt)

    rng = np.random.default_rng(seed=42)
    Z = rng.standard_normal((horizon, n_paths))
    log_ret = drift + diffusion * Z
    paths = current_price * np.exp(np.cumsum(log_ret, axis=0))
    paths = np.vstack([np.full(n_paths, current_price), paths])

    steps = np.arange(horizon + 1)
    pcts = pd.DataFrame(
        {
            "p5": np.percentile(paths, 5, axis=1),
            "p25": np.percentile(paths, 25, axis=1),
            "p50": np.percentile(paths, 50, axis=1),
            "p75": np.percentile(paths, 75, axis=1),
            "p95": np.percentile(paths, 95, axis=1),
        },
        index=steps,
    )

    final = paths[-1]
    rng2 = np.random.default_rng(seed=99)
    sample_idx = rng2.choice(n_paths, size=min(25, n_paths), replace=False)

    return {
        "percentiles": pcts,
        "sample_paths": pd.DataFrame(paths[:, sample_idx], index=steps),
        "prob_up": float(np.mean(final > current_price)),
        "expected_return": float((np.median(final) - current_price) / current_price),
        "var_95": float((np.percentile(final, 5) - current_price) / current_price),
        "final_prices": final,
        "is_intraday": time_horizon == "intraday",
        "horizon": horizon,
        "current_price": current_price,
    }


def simulate_portfolio(
    prices: dict[str, float],
    mus: dict[str, float],
    sigmas: dict[str, float],
    weights: dict[str, float],
    corr_matrix: pd.DataFrame,
    horizon: int,
    time_horizon: str = "swing",
    n_paths: int = 300,
) -> dict:
    """
    Correlated multi-asset portfolio GBM using Cholesky decomposition.

    Returns portfolio value paths expressed as multiples of initial portfolio value (starts at 1.0).
    """
    symbols = [s for s in weights if weights[s] > 0]
    if not symbols:
        return {}

    n_assets = len(symbols)
    w = np.array([weights[s] for s in symbols])
    mu_arr = np.array([mus[s] for s in symbols])
    sig_arr = np.array([sigmas[s] for s in symbols])

    # Build ordered correlation matrix; add small jitter for numerical stability
    corr = corr_matrix.loc[symbols, symbols].values.astype(float)
    corr += np.eye(n_assets) * 1e-6
    L = np.linalg.cholesky(corr)

    dt = _dt(symbols[0], time_horizon)
    drifts = (mu_arr - 0.5 * sig_arr ** 2) * dt     # (n_assets,)
    diffusions = sig_arr * np.sqrt(dt)               # (n_assets,)

    rng = np.random.default_rng(seed=42)
    Z_raw = rng.standard_normal((horizon, n_assets, n_paths))
    # Apply Cholesky: Z_corr[t, i, p] = sum_j L[i,j] * Z_raw[t, j, p]
    Z_corr = np.einsum("ij,tjp->tip", L, Z_raw)

    # Log returns per asset per step per path
    log_ret = drifts[None, :, None] + diffusions[None, :, None] * Z_corr  # (horizon, n_assets, n_paths)

    # Cumulative price relatives (normalized to 1 at t=0)
    cum = np.exp(np.cumsum(log_ret, axis=0))            # (horizon, n_assets, n_paths)
    ones = np.ones((1, n_assets, n_paths))
    price_rel = np.concatenate([ones, cum], axis=0)     # (horizon+1, n_assets, n_paths)

    # Portfolio value = weighted sum of price relatives
    portfolio_value = np.einsum("tap,a->tp", price_rel, w)  # (horizon+1, n_paths)

    steps = np.arange(horizon + 1)
    pcts = pd.DataFrame(
        {
            "p5": np.percentile(portfolio_value, 5, axis=1),
            "p25": np.percentile(portfolio_value, 25, axis=1),
            "p50": np.percentile(portfolio_value, 50, axis=1),
            "p75": np.percentile(portfolio_value, 75, axis=1),
            "p95": np.percentile(portfolio_value, 95, axis=1),
        },
        index=steps,
    )

    final = portfolio_value[-1]
    return {
        "percentiles": pcts,
        "prob_up": float(np.mean(final > 1.0)),
        "expected_return": float(np.median(final) - 1.0),
        "var_95": float(np.percentile(final, 5) - 1.0),
        "is_portfolio": True,
        "horizon": horizon,
    }
