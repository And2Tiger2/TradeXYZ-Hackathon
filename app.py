import streamlit as st
import numpy as np
import pandas as pd

from config import SUPPORTED_SYMBOLS, SYMBOL_DISPLAY, MC_SWING_DAYS, MC_INTRADAY_HOURS
from schemas.inputs import UserInput

# Data
from data.market import fetch_ohlcv, get_latest_price, get_returns
from data.indicators import (
    compute_rsi, compute_volatility, compute_sma,
    compute_macd, compute_bollinger_bands, compute_drift,
    build_market_context,
)
from data.news import fetch_headlines
from data.macro import fetch_macro_context, fetch_vix
from data.finnhub_data import get_realtime_quote, get_company_profile, get_earnings_surprise
from data.simulation import run_gbm_simulation, simulate_portfolio
from data.portfolio_optimizer import fetch_multi_returns, optimize_portfolio

# Agents
import agents.technical as technical_agent
import agents.news as news_agent
import agents.risk as risk_agent
import agents.portfolio as portfolio_agent
import agents.macro as macro_agent
from agents.portfolio import enforce_constraints

# UI
from ui.charts import (
    enhanced_price_chart, macd_chart, rsi_chart,
    monte_carlo_chart, portfolio_sim_chart,
    macro_chart, portfolio_allocation_chart, correlation_heatmap,
)
from ui.components import (
    agent_card_technical, agent_card_news, agent_card_risk,
    agent_card_macro, final_trade_ticket,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Trading Desk",
    page_icon="📊",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Trading Desk")
    st.caption("Multi-agent AI decision engine")
    st.divider()

    mode = st.radio("Mode", ["Single Asset", "Portfolio"], horizontal=True)
    st.divider()

    if mode == "Single Asset":
        symbol = st.selectbox("Symbol", SUPPORTED_SYMBOLS, format_func=lambda s: SYMBOL_DISPLAY.get(s, s))
        symbols = [symbol]
    else:
        symbols = st.multiselect(
            "Symbols (2–4)",
            SUPPORTED_SYMBOLS,
            default=SUPPORTED_SYMBOLS[:2],
            format_func=lambda s: SYMBOL_DISPLAY.get(s, s),
        )
        symbol = symbols[0] if symbols else SUPPORTED_SYMBOLS[0]

    time_horizon = st.radio("Time Horizon", ["intraday", "swing"], horizontal=True)
    st.divider()
    account_size  = st.number_input("Account Size (USD)", min_value=100.0, value=10000.0, step=500.0)
    risk_mode     = st.select_slider("Risk Mode", options=["conservative", "balanced", "aggressive"], value="balanced")
    max_risk_pct  = st.slider("Max Risk per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5) / 100
    max_leverage  = st.slider("Max Leverage", min_value=1.0, max_value=10.0, value=2.0, step=0.5)
    st.divider()
    run_button    = st.button("Analyze", type="primary", use_container_width=True)

# ── Header ─────────────────────────────────────────────────────────────────────
if mode == "Single Asset":
    st.title("Multi-Agent Trading Desk")
    st.caption(f"Analyzing: **{SYMBOL_DISPLAY.get(symbol, symbol)}** | Horizon: {time_horizon} | Risk: {risk_mode}")
else:
    st.title("Portfolio Analysis Mode")
    names = ", ".join(SYMBOL_DISPLAY.get(s, s) for s in symbols)
    st.caption(f"Symbols: **{names}** | Horizon: {time_horizon} | Risk: {risk_mode}")

if not run_button:
    if mode == "Portfolio" and len(symbols) < 2:
        st.warning("Select at least 2 symbols for portfolio mode.")
    else:
        st.info("Configure your parameters in the sidebar and click **Analyze**.")
    st.stop()

if mode == "Portfolio" and len(symbols) < 2:
    st.error("Select at least 2 symbols for portfolio mode.")
    st.stop()

# ── Shared: Macro context (fetched once, used everywhere) ─────────────────────
macro_ctx    = {"available": False}
vix          = None
macro_result = None

with st.spinner("Fetching macro data (FRED + VIX)..."):
    macro_ctx = fetch_macro_context()
    vix       = fetch_vix()

# ══════════════════════════════════════════════════════════════════════════════
# SINGLE ASSET MODE
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single Asset":

    user_input = UserInput(
        symbol=symbol,
        time_horizon=time_horizon,
        account_size=account_size,
        risk_mode=risk_mode,
        max_risk_per_trade_pct=max_risk_pct,
        max_leverage=max_leverage,
    )
    risk_constraints = {
        "max_risk_per_trade_pct": max_risk_pct,
        "max_leverage": max_leverage,
        "risk_mode": risk_mode,
        "account_size": account_size,
    }

    # ── Fetch price data ───────────────────────────────────────────────────────
    with st.spinner("Fetching market data..."):
        try:
            df      = fetch_ohlcv(symbol, time_horizon)
            price   = get_latest_price(df)
            returns = get_returns(df, time_horizon)
            rsi_val = compute_rsi(df)
            vol     = compute_volatility(df, symbol=symbol, time_horizon=time_horizon)
            mu      = compute_drift(df, symbol=symbol, time_horizon=time_horizon)
            macd_data = compute_macd(df)
            bb_data   = compute_bollinger_bands(df)
            market_context = build_market_context(symbol, df, returns, time_horizon)
        except Exception as e:
            st.error(f"Failed to fetch market data: {e}")
            st.stop()

    # Optional: real-time Finnhub quote
    rt_quote = get_realtime_quote(symbol)

    with st.spinner("Fetching headlines..."):
        headlines = fetch_headlines(symbol)

    # ── Market snapshot ────────────────────────────────────────────────────────
    st.subheader("Market Snapshot")
    snap_cols = st.columns(6)

    price_display = rt_quote["current"] if rt_quote else price
    price_label   = "Live Price" if rt_quote else "Price (delayed)"
    delta_display = returns.get("1d") or returns.get("1h", 0)

    snap_cols[0].metric(price_label, f"${price_display:,.2f}", f"{delta_display:+.2%}")
    if time_horizon == "intraday":
        snap_cols[1].metric("4h Return",  f"{returns.get('4h', 0):+.2%}")
        snap_cols[2].metric("24h Return", f"{returns.get('1d', 0):+.2%}")
    else:
        snap_cols[1].metric("5d Return",  f"{returns.get('5d', 0):+.2%}")
        snap_cols[2].metric("1mo Return", f"{returns.get('1mo', 0):+.2%}")
    snap_cols[3].metric("RSI (14)",    f"{rsi_val:.1f}")
    snap_cols[4].metric("Ann. Vol",    f"{vol:.0%}")
    if vix is not None:
        snap_cols[5].metric("VIX", f"{vix:.1f}", delta=None)

    # Finnhub company profile (equities only)
    profile = get_company_profile(symbol)
    if profile:
        with st.expander("Company Profile"):
            pc = st.columns(4)
            pc[0].metric("Market Cap", f"${profile.get('marketCapitalization', 0):,.0f}M")
            pc[1].metric("Industry",   profile.get("finnhubIndustry", "—"))
            pc[2].metric("Country",    profile.get("country", "—"))
            pc[3].metric("IPO Date",   profile.get("ipo", "—"))

    # ── Charts ─────────────────────────────────────────────────────────────────
    st.subheader("Technical Charts")
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Price + Bollinger Bands", "MACD", "RSI"])
    with chart_tab1:
        st.plotly_chart(enhanced_price_chart(df, symbol, bb_data, time_horizon), use_container_width=True)
        bb_col1, bb_col2, bb_col3 = st.columns(3)
        bb_col1.metric("%B (Bollinger)", f"{bb_data['pct_b']:.2f}", help="0=at lower band, 1=at upper band")
        bb_col2.metric("BB Bandwidth",   f"{bb_data['bandwidth']:.3f}")
        bb_col3.metric("BB Squeeze",     "Yes 🔴" if bb_data["squeeze"] else "No 🟢")
    with chart_tab2:
        st.plotly_chart(macd_chart(macd_data, symbol), use_container_width=True)
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("MACD",      f"{macd_data['macd']:.4f}")
        mc2.metric("Signal",    f"{macd_data['signal']:.4f}")
        mc3.metric("Histogram", f"{macd_data['histogram']:.4f}")
        st.caption(f"MACD crossover: **{macd_data['crossover'].upper()}**")
    with chart_tab3:
        st.plotly_chart(rsi_chart(df, symbol), use_container_width=True)

    # ── Macro section ──────────────────────────────────────────────────────────
    if macro_ctx.get("available"):
        st.subheader("Macro Context (FRED)")
        st.plotly_chart(macro_chart(macro_ctx, vix), use_container_width=True)
        detected_regime = macro_ctx.get("regime", "unknown")
        st.caption(f"Detected regime: **{detected_regime.replace('_', ' ').title()}**")

    # ── Run agents ─────────────────────────────────────────────────────────────
    st.subheader("Agent Analysis")

    col_tech, col_news = st.columns(2)
    col_risk, col_macro = st.columns(2)

    with col_tech:
        with st.container(border=True):
            with st.spinner("Running Technical Agent..."):
                try:
                    tech_result = technical_agent.run(market_context)
                except Exception as e:
                    st.error(f"Technical agent failed: {e}")
                    st.stop()
            agent_card_technical(tech_result)

    with col_news:
        with st.container(border=True):
            with st.spinner("Running News Agent..."):
                try:
                    news_result = news_agent.run(symbol, headlines)
                except Exception as e:
                    st.error(f"News agent failed: {e}")
                    st.stop()
            agent_card_news(news_result)

    # Macro agent (only if FRED available)
    macro_agent_result = None
    if macro_ctx.get("available"):
        with col_macro:
            with st.container(border=True):
                with st.spinner("Running Macro Agent..."):
                    try:
                        macro_agent_result = macro_agent.run(macro_ctx, symbol, time_horizon)
                    except Exception as e:
                        st.warning(f"Macro agent failed (non-fatal): {e}")
                if macro_agent_result:
                    agent_card_macro(macro_agent_result)

    # Risk agent
    with col_risk:
        with st.container(border=True):
            with st.spinner("Running Risk Manager..."):
                try:
                    risk_result = risk_agent.run(tech_result, news_result, risk_constraints, market_context)
                except Exception as e:
                    st.error(f"Risk agent failed: {e}")
                    st.stop()
            agent_card_risk(risk_result)

    # Portfolio agent
    st.divider()
    with st.container(border=True):
        with st.spinner("Running Portfolio Manager..."):
            try:
                portfolio_result = portfolio_agent.run(
                    tech_result, news_result, risk_result, risk_constraints, macro_agent_result
                )
                portfolio_result = enforce_constraints(portfolio_result, max_risk_pct, max_leverage)
            except Exception as e:
                st.error(f"Portfolio agent failed: {e}")
                st.stop()

        st.subheader("Final Recommendation")
        final_trade_ticket(portfolio_result, account_size)

    # ── Agent disagreement summary ─────────────────────────────────────────────
    actions = {
        "Technical": tech_result.suggested_action,
        "News": news_result.suggested_action,
        "Risk": risk_result.override_action or (None if risk_result.approved else "hold"),
        "Portfolio": portfolio_result.final_action,
    }
    non_none = {k: v for k, v in actions.items() if v is not None}
    if len(set(non_none.values())) > 1:
        parts = [f"**{k}**: {v}" for k, v in non_none.items()]
        st.caption("Agent disagreement: " + " | ".join(parts))

    # ── Monte Carlo simulation ─────────────────────────────────────────────────
    if portfolio_result.confidence >= 0.50 and portfolio_result.final_action != "hold":
        st.subheader("GBM Monte Carlo Simulation")
        horizon = MC_INTRADAY_HOURS if time_horizon == "intraday" else MC_SWING_DAYS
        with st.spinner("Running simulation..."):
            sim = run_gbm_simulation(
                current_price=price,
                mu=mu,
                sigma=vol,
                horizon=horizon,
                symbol=symbol,
                time_horizon=time_horizon,
            )
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        sim_col1.metric("P(price ends higher)", f"{sim['prob_up']:.0%}")
        sim_col2.metric("Median expected return", f"{sim['expected_return']:+.1%}")
        sim_col3.metric("95% VaR", f"{sim['var_95']:.1%}")
        st.plotly_chart(
            monte_carlo_chart(
                sim, symbol,
                stop_pct=portfolio_result.stop_loss_pct,
                target_pct=portfolio_result.take_profit_pct,
                time_horizon=time_horizon,
            ),
            use_container_width=True,
        )
        st.caption(
            f"GBM inputs: μ={mu:.1%} ann. drift · σ={vol:.1%} ann. vol · "
            f"{MC_N_PATHS} paths · {horizon} {'hours' if time_horizon == 'intraday' else 'days'} forward. "
            "Simulation assumes constant drift and volatility; not a price forecast."
        )
    elif portfolio_result.final_action == "hold":
        st.info("Simulation skipped — recommendation is HOLD.")

    # ── Earnings surprise (if Finnhub available) ───────────────────────────────
    earnings = get_earnings_surprise(symbol)
    if earnings:
        with st.expander("Recent Earnings Surprises"):
            for e in earnings:
                q    = e.get("period", "")
                est  = e.get("estimate", 0) or 0
                act  = e.get("actual", 0) or 0
                surp = e.get("surprisePercent", 0) or 0
                icon = "🟢" if surp > 0 else "🔴"
                st.markdown(f"{icon} **{q}** — Actual: `{act:.2f}` vs Est: `{est:.2f}` (surprise: {surp:+.1f}%)")

    # ── Debug expander ─────────────────────────────────────────────────────────
    with st.expander("Raw Agent Outputs (Debug)"):
        tabs = ["Technical", "News", "Risk", "Portfolio", "Headlines"]
        if macro_agent_result:
            tabs.insert(3, "Macro")
        dbg_tabs = st.tabs(tabs)
        idx = 0
        with dbg_tabs[idx]:  st.json(tech_result.model_dump());  idx += 1
        with dbg_tabs[idx]:  st.json(news_result.model_dump());  idx += 1
        with dbg_tabs[idx]:  st.json(risk_result.model_dump());  idx += 1
        if macro_agent_result:
            with dbg_tabs[idx]:  st.json(macro_agent_result.model_dump());  idx += 1
        with dbg_tabs[idx]:  st.json(portfolio_result.model_dump());  idx += 1
        with dbg_tabs[idx]:
            for h in headlines:
                st.markdown(f"- {h}")


# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    risk_constraints = {
        "max_risk_per_trade_pct": max_risk_pct,
        "max_leverage": max_leverage,
        "risk_mode": risk_mode,
        "account_size": account_size,
    }

    # Shared macro agent run (one run covers all assets)
    macro_agent_result = None
    if macro_ctx.get("available"):
        with st.spinner("Running Macro Agent..."):
            try:
                macro_agent_result = macro_agent.run(macro_ctx, "portfolio", time_horizon)
            except Exception:
                pass

    # ── Per-symbol agent analysis ──────────────────────────────────────────────
    st.subheader("Per-Symbol Agent Analysis")
    per_symbol: dict = {}

    for sym in symbols:
        with st.expander(f"{SYMBOL_DISPLAY.get(sym, sym)}", expanded=True):
            try:
                with st.spinner(f"Fetching data for {sym}..."):
                    df_s      = fetch_ohlcv(sym, time_horizon)
                    price_s   = get_latest_price(df_s)
                    returns_s = get_returns(df_s, time_horizon)
                    vol_s     = compute_volatility(df_s, symbol=sym, time_horizon=time_horizon)
                    mu_s      = compute_drift(df_s, symbol=sym, time_horizon=time_horizon)
                    ctx_s     = build_market_context(sym, df_s, returns_s, time_horizon)
                    headlines_s = fetch_headlines(sym)

                c1, c2 = st.columns([1, 1])
                with c1:
                    with st.spinner(f"Technical agent ({sym})..."):
                        tech_s = technical_agent.run(ctx_s)
                    agent_card_technical(tech_s)
                with c2:
                    with st.spinner(f"News agent ({sym})..."):
                        news_s = news_agent.run(sym, headlines_s)
                    agent_card_news(news_s)

                with st.spinner(f"Risk + Portfolio agents ({sym})..."):
                    risk_s      = risk_agent.run(tech_s, news_s, risk_constraints, ctx_s)
                    port_s      = portfolio_agent.run(tech_s, news_s, risk_s, risk_constraints, macro_agent_result)
                    port_s      = enforce_constraints(port_s, max_risk_pct, max_leverage)

                c3, c4 = st.columns([1, 1])
                with c3:
                    with st.container(border=True):
                        agent_card_risk(risk_s)
                with c4:
                    with st.container(border=True):
                        st.markdown("#### Portfolio Manager")
                        bias_map = {"long": "🟢 LONG", "short": "🔴 SHORT", "hold": "⚪ HOLD"}
                        st.markdown(f"**{bias_map[port_s.final_action]}**")
                        st.progress(port_s.confidence, text=f"Confidence: {port_s.confidence:.0%}")

                per_symbol[sym] = {
                    "df": df_s,
                    "price": price_s,
                    "vol": vol_s,
                    "mu": mu_s,
                    "tech": tech_s,
                    "news": news_s,
                    "risk": risk_s,
                    "portfolio": port_s,
                }
            except Exception as e:
                st.error(f"Failed to analyze {sym}: {e}")

    if len(per_symbol) < 2:
        st.error("At least 2 symbols must complete analysis for portfolio optimization.")
        st.stop()

    # ── Portfolio optimization ─────────────────────────────────────────────────
    st.divider()
    st.subheader("Portfolio Optimization")

    with st.spinner("Optimizing portfolio (mean-variance)..."):
        hist_returns = fetch_multi_returns(list(per_symbol.keys()))
        agent_signals      = {s: d["portfolio"].final_action for s, d in per_symbol.items()}
        agent_confidences  = {s: d["portfolio"].confidence   for s, d in per_symbol.items()}
        opt = optimize_portfolio(hist_returns, agent_signals, agent_confidences)

    opt_col1, opt_col2, opt_col3 = st.columns(3)
    opt_col1.metric("Expected Return (ann.)", f"{opt['portfolio_return']:+.1%}")
    opt_col2.metric("Volatility (ann.)",      f"{opt['portfolio_volatility']:.1%}")
    opt_col3.metric("Sharpe Ratio",           f"{opt['sharpe_ratio']:.2f}")

    if opt["eligible_symbols"]:
        st.caption(f"Long-eligible symbols: {', '.join(opt['eligible_symbols'])}")
        non_eligible = [s for s in per_symbol if s not in opt["eligible_symbols"]]
        if non_eligible:
            st.caption(f"Held to cash (no long signal): {', '.join(non_eligible)}")
    else:
        st.warning("No symbols received a LONG signal — full cash position recommended.")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            portfolio_allocation_chart(opt["weights_max_sharpe"], opt["weights_min_variance"]),
            use_container_width=True,
        )
    with chart_col2:
        if isinstance(opt.get("correlation_matrix"), pd.DataFrame):
            st.plotly_chart(correlation_heatmap(opt["correlation_matrix"]), use_container_width=True)

    # ── Per-symbol price charts ────────────────────────────────────────────────
    st.subheader("Price Charts")
    for sym, d in per_symbol.items():
        st.plotly_chart(
            enhanced_price_chart(d["df"], sym, compute_bollinger_bands(d["df"]), time_horizon),
            use_container_width=True,
        )

    # ── Macro section ──────────────────────────────────────────────────────────
    if macro_ctx.get("available"):
        st.subheader("Macro Context")
        macro_chart_col, macro_card_col = st.columns([2, 1])
        with macro_chart_col:
            st.plotly_chart(macro_chart(macro_ctx, vix), use_container_width=True)
        if macro_agent_result:
            with macro_card_col:
                with st.container(border=True):
                    agent_card_macro(macro_agent_result)

    # ── Portfolio simulation (correlated GBM) ─────────────────────────────────
    eligible = opt["eligible_symbols"]
    if eligible and isinstance(opt.get("correlation_matrix"), pd.DataFrame):
        st.subheader("Portfolio GBM Simulation (Correlated)")
        horizon = MC_INTRADAY_HOURS if time_horizon == "intraday" else MC_SWING_DAYS
        w_sharpe = opt["weights_max_sharpe"]
        prices_s = {s: per_symbol[s]["price"] for s in eligible}
        mus_s    = {s: per_symbol[s]["mu"]    for s in eligible}
        sigmas_s = {s: per_symbol[s]["vol"]   for s in eligible}
        corr_df  = opt["correlation_matrix"].loc[eligible, eligible]

        with st.spinner("Running correlated portfolio simulation..."):
            try:
                port_sim = simulate_portfolio(
                    prices=prices_s,
                    mus=mus_s,
                    sigmas=sigmas_s,
                    weights={s: w_sharpe[s] for s in eligible},
                    corr_matrix=corr_df,
                    horizon=horizon,
                    time_horizon=time_horizon,
                )
                if port_sim:
                    ps_col1, ps_col2, ps_col3 = st.columns(3)
                    ps_col1.metric("P(portfolio up)",         f"{port_sim['prob_up']:.0%}")
                    ps_col2.metric("Median expected return",  f"{port_sim['expected_return']:+.1%}")
                    ps_col3.metric("95% VaR",                 f"{port_sim['var_95']:.1%}")
                    label = "Hours" if time_horizon == "intraday" else "Days"
                    st.plotly_chart(portfolio_sim_chart(port_sim, label), use_container_width=True)
                    st.caption(
                        "Correlated simulation via Cholesky decomposition. "
                        "Based on 6-month historical correlations. Not a price forecast."
                    )
            except Exception as e:
                st.warning(f"Portfolio simulation failed: {e}")

    # ── Final allocation table ─────────────────────────────────────────────────
    st.subheader("Final Allocation")
    rows = []
    for sym in symbols:
        d = per_symbol.get(sym)
        if not d:
            continue
        w_ms = opt["weights_max_sharpe"].get(sym, 0.0)
        w_mv = opt["weights_min_variance"].get(sym, 0.0)
        rows.append({
            "Symbol":             SYMBOL_DISPLAY.get(sym, sym),
            "Signal":             d["portfolio"].final_action.upper(),
            "Confidence":         f"{d['portfolio'].confidence:.0%}",
            "Max Sharpe Weight":  f"{w_ms:.1%}",
            "Min Var Weight":     f"{w_mv:.1%}",
            "Ann. Vol":           f"{d['vol']:.1%}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
