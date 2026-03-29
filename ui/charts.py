import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_DARK = "plotly_dark"
_MARGIN = dict(l=0, r=0, t=40, b=0)

# ── Colour palette ─────────────────────────────────────────────────────────────
C_PRICE   = "#00b4d8"
C_SMA20   = "#f77f00"
C_SMA50   = "#fcbf49"
C_BB_FILL = "rgba(120,120,200,0.15)"
C_BB_LINE = "rgba(150,150,220,0.6)"
C_VOL     = "rgba(80,80,200,0.4)"
C_BULL    = "#2dc653"
C_BEAR    = "#e63946"
C_NEUTRAL = "#8d99ae"
C_MACD    = "#00b4d8"
C_SIGNAL  = "#f77f00"


# ── 1. Enhanced price chart with Bollinger Bands ───────────────────────────────
def enhanced_price_chart(df: pd.DataFrame, symbol: str, bb_data: dict | None = None, time_horizon: str = "swing") -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.02,
    )

    # Bollinger Bands fill
    if bb_data:
        upper = bb_data["upper_series"].dropna()
        lower = bb_data["lower_series"].dropna()
        middle = bb_data["middle_series"].dropna()
        fig.add_trace(go.Scatter(x=upper.index, y=upper, line=dict(color=C_BB_LINE, width=1), name="BB Upper", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=lower.index, y=lower, line=dict(color=C_BB_LINE, width=1), fill="tonexty", fillcolor=C_BB_FILL, name="Bollinger Bands"), row=1, col=1)
        fig.add_trace(go.Scatter(x=middle.index, y=middle, line=dict(color=C_SMA20, width=1, dash="dot"), name="BB Mid / SMA 20"), row=1, col=1)

    # SMA 50
    sma50 = df["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(x=df.index, y=sma50, line=dict(color=C_SMA50, width=1, dash="dash"), name="SMA 50"), row=1, col=1)

    # Price line
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], line=dict(color=C_PRICE, width=2), name="Price"), row=1, col=1)

    # Volume bars
    if "Volume" in df.columns:
        colours = [C_BULL if df["Close"].iloc[i] >= df["Open"].iloc[i] else C_BEAR for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=colours, opacity=0.6, name="Volume", showlegend=False), row=2, col=1)

    period_label = "5d (1h bars)" if time_horizon == "intraday" else "3 Month"
    fig.update_layout(
        title=f"{symbol} — {period_label}",
        template=_DARK,
        height=380,
        margin=_MARGIN,
        legend=dict(orientation="h", y=1.08),
        xaxis_rangeslider_visible=False,
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


# ── 2. MACD chart ──────────────────────────────────────────────────────────────
def macd_chart(macd_data: dict, symbol: str) -> go.Figure:
    macd_s   = macd_data["macd_series"].dropna()
    signal_s = macd_data["signal_series"].dropna()
    hist_s   = macd_data["histogram_series"].dropna()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.55, 0.45], vertical_spacing=0.04)

    fig.add_trace(go.Scatter(x=macd_s.index, y=macd_s, line=dict(color=C_MACD, width=1.5), name="MACD"), row=1, col=1)
    fig.add_trace(go.Scatter(x=signal_s.index, y=signal_s, line=dict(color=C_SIGNAL, width=1.5), name="Signal"), row=1, col=1)

    bar_colours = [C_BULL if v >= 0 else C_BEAR for v in hist_s]
    fig.add_trace(go.Bar(x=hist_s.index, y=hist_s, marker_color=bar_colours, opacity=0.8, name="Histogram"), row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.3)", row=2, col=1)

    fig.update_layout(title=f"{symbol} — MACD (12/26/9)", template=_DARK, height=300, margin=_MARGIN, legend=dict(orientation="h", y=1.1))
    return fig


# ── 3. RSI chart ───────────────────────────────────────────────────────────────
def rsi_chart(df: pd.DataFrame, symbol: str, window: int = 14) -> go.Figure:
    close = df["Close"]
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(window).mean()
    loss  = (-delta.clip(upper=0)).rolling(window).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = (100 - 100 / (1 + rs)).dropna()

    colours = [C_BULL if v < 30 else (C_BEAR if v > 70 else C_NEUTRAL) for v in rsi]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rsi.index, y=rsi, line=dict(color=C_PRICE, width=1.5), name="RSI"))
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(230,57,70,0.1)", line_width=0, annotation_text="Overbought")
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(45,198,83,0.1)",  line_width=0, annotation_text="Oversold")
    fig.add_hline(y=70, line_dash="dot", line_color=C_BEAR, line_width=1)
    fig.add_hline(y=30, line_dash="dot", line_color=C_BULL, line_width=1)
    fig.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.update_layout(title=f"{symbol} — RSI ({window})", template=_DARK, height=220, margin=_MARGIN, yaxis=dict(range=[0, 100]))
    return fig


# ── 4. Monte Carlo / GBM fan chart ────────────────────────────────────────────
def monte_carlo_chart(
    sim: dict,
    symbol: str,
    stop_pct: float | None = None,
    target_pct: float | None = None,
    time_horizon: str = "swing",
) -> go.Figure:
    pcts  = sim["percentiles"]
    steps = pcts.index.tolist()
    price = sim["current_price"]
    label = "Hours" if sim["is_intraday"] else "Days"

    fig = go.Figure()

    # Sample paths (faint)
    if "sample_paths" in sim:
        for col in sim["sample_paths"].columns[:15]:
            fig.add_trace(go.Scatter(
                x=steps, y=sim["sample_paths"][col],
                mode="lines", line=dict(color="rgba(255,255,255,0.06)", width=1),
                showlegend=False,
            ))

    # Percentile bands
    fig.add_trace(go.Scatter(x=steps, y=pcts["p95"], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p5"],  fill="tonexty", fillcolor="rgba(0,180,216,0.08)", line=dict(width=0), name="5–95th %ile"))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p75"], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p25"], fill="tonexty", fillcolor="rgba(0,180,216,0.18)", line=dict(width=0), name="25–75th %ile"))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p50"], line=dict(color=C_PRICE, width=2), name="Median path"))

    # Entry price
    fig.add_hline(y=price, line_dash="dot", line_color="rgba(255,255,255,0.5)", annotation_text="Entry")

    # Stop loss / take profit lines
    if stop_pct:
        fig.add_hline(y=price * (1 - stop_pct), line_dash="dash", line_color=C_BEAR, annotation_text=f"Stop −{stop_pct:.1%}")
    if target_pct:
        fig.add_hline(y=price * (1 + target_pct), line_dash="dash", line_color=C_BULL, annotation_text=f"Target +{target_pct:.1%}")

    horizon = sim["horizon"]
    prob_up  = sim["prob_up"]
    exp_ret  = sim["expected_return"]
    var95    = sim["var_95"]

    fig.update_layout(
        title=f"{symbol} — {horizon}{label[0]} GBM Simulation | P(up)={prob_up:.0%} | E[ret]={exp_ret:+.1%} | VaR95={var95:.1%}",
        xaxis_title=label + " forward",
        yaxis_title="Price (USD)",
        template=_DARK,
        height=340,
        margin=_MARGIN,
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# ── 5. Portfolio Monte Carlo fan chart (value-based) ──────────────────────────
def portfolio_sim_chart(sim: dict, horizon_label: str = "Days") -> go.Figure:
    pcts  = sim["percentiles"]
    steps = pcts.index.tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steps, y=pcts["p95"], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p5"],  fill="tonexty", fillcolor="rgba(0,180,216,0.08)", line=dict(width=0), name="5–95th %ile"))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p75"], line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p25"], fill="tonexty", fillcolor="rgba(0,180,216,0.18)", line=dict(width=0), name="25–75th %ile"))
    fig.add_trace(go.Scatter(x=steps, y=pcts["p50"], line=dict(color=C_PRICE, width=2), name="Median portfolio"))
    fig.add_hline(y=1.0, line_dash="dot", line_color="rgba(255,255,255,0.5)", annotation_text="Entry NAV=1")

    exp_ret = sim["expected_return"]
    var95   = sim["var_95"]
    fig.update_layout(
        title=f"Portfolio Simulation | E[ret]={exp_ret:+.1%} | VaR95={var95:.1%}",
        xaxis_title=horizon_label + " forward",
        yaxis_title="Portfolio Value (normalized)",
        template=_DARK,
        height=300,
        margin=_MARGIN,
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# ── 6. Macro indicators bar chart ─────────────────────────────────────────────
def macro_chart(macro_ctx: dict, vix: float | None = None) -> go.Figure:
    labels, values, colors, refs = [], [], [], []

    yc = macro_ctx.get("yield_curve_10y2y", {})
    if yc.get("latest_value") is not None:
        v = yc["latest_value"]
        labels.append("Yield Curve (10y-2y)")
        values.append(v)
        colors.append(C_BULL if v > 0 else C_BEAR)
        refs.append(0)

    ffr = macro_ctx.get("fed_funds_rate", {})
    if ffr.get("latest_value") is not None:
        labels.append("Fed Funds Rate (%)")
        values.append(ffr["latest_value"])
        colors.append(C_NEUTRAL)
        refs.append(None)

    cpi = macro_ctx.get("cpi", {})
    if cpi.get("yoy_pct") is not None:
        v = cpi["yoy_pct"]
        labels.append("CPI YoY (%)")
        values.append(v)
        colors.append(C_BEAR if v > 4 else (C_NEUTRAL if v > 2 else C_BULL))
        refs.append(2)

    unrate = macro_ctx.get("unemployment", {})
    if unrate.get("latest_value") is not None:
        v = unrate["latest_value"]
        labels.append("Unemployment (%)")
        values.append(v)
        colors.append(C_BEAR if v > 5 else C_NEUTRAL)
        refs.append(None)

    bei = macro_ctx.get("breakeven_inflation", {})
    if bei.get("latest_value") is not None:
        labels.append("10y Breakeven Inflation")
        values.append(bei["latest_value"])
        colors.append(C_NEUTRAL)
        refs.append(None)

    if vix is not None:
        labels.append("VIX")
        values.append(vix)
        colors.append(C_BEAR if vix > 25 else (C_NEUTRAL if vix > 15 else C_BULL))
        refs.append(20)

    if not labels:
        return go.Figure()

    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors, text=[f"{v:.2f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="US Macro Indicators (FRED + VIX)",
        template=_DARK,
        height=280,
        margin=dict(l=0, r=0, t=40, b=60),
        showlegend=False,
        yaxis_title="Value",
    )
    return fig


# ── 7. Portfolio allocation donut charts ──────────────────────────────────────
def portfolio_allocation_chart(
    weights_sharpe: dict[str, float],
    weights_minvar: dict[str, float],
) -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=["Max Sharpe", "Min Variance"],
    )

    def _donut(weights: dict) -> tuple[list, list]:
        items = [(s, w) for s, w in weights.items() if w > 0.005]
        return [s for s, _ in items], [w for _, w in items]

    labels_s, vals_s = _donut(weights_sharpe)
    labels_m, vals_m = _donut(weights_minvar)

    fig.add_trace(go.Pie(labels=labels_s, values=vals_s, hole=0.45, name="Max Sharpe"), row=1, col=1)
    fig.add_trace(go.Pie(labels=labels_m, values=vals_m, hole=0.45, name="Min Variance"), row=1, col=2)

    fig.update_layout(template=_DARK, height=280, margin=_MARGIN)
    return fig


# ── 8. Correlation heatmap ─────────────────────────────────────────────────────
def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    symbols = list(corr.columns)
    z = corr.values.round(2)

    fig = go.Figure(go.Heatmap(
        z=z, x=symbols, y=symbols,
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        text=z, texttemplate="%{text:.2f}",
        showscale=True,
    ))
    fig.update_layout(title="Asset Correlation Matrix", template=_DARK, height=300, margin=_MARGIN)
    return fig


# ── Legacy alias ──────────────────────────────────────────────────────────────
def price_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    return enhanced_price_chart(df, symbol)
