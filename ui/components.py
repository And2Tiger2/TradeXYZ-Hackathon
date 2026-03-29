import streamlit as st
from schemas.outputs import TechnicalOutput, NewsOutput, RiskOutput, PortfolioOutput, MacroOutput

BIAS_COLOR  = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}
ACTION_COLOR = {"long": "#2dc653", "short": "#e63946", "hold": "#8d99ae"}
ACTION_LABEL = {"long": "LONG ▲", "short": "SHORT ▼", "hold": "HOLD —"}
RISK_COLOR   = {"low": "🟢", "medium": "🟡", "high": "🔴"}
REGIME_LABEL = {
    "expansion":      ("🟢", "Expansion"),
    "tightening":     ("🟡", "Tightening"),
    "easing":         ("🟢", "Easing"),
    "high_inflation": ("🔴", "High Inflation"),
    "stagflation":    ("🔴", "Stagflation"),
    "inversion_risk": ("🔴", "Inversion Risk"),
    "unknown":        ("⚪", "Unknown"),
}


def agent_card_technical(result: TechnicalOutput):
    st.markdown("#### Technical Analyst")
    bias_icon = BIAS_COLOR.get(result.bias, "⚪")
    st.markdown(f"{bias_icon} **{result.bias.upper()}** &nbsp; suggested: `{result.suggested_action}`")
    st.progress(result.confidence, text=f"Confidence: {result.confidence:.0%}")
    if result.signals:
        st.markdown("**Signals**")
        for s in result.signals:
            st.markdown(f"- {s}")
    if result.risks:
        st.markdown("**Risks**")
        for r in result.risks:
            st.markdown(f"- {r}")


def agent_card_news(result: NewsOutput):
    st.markdown("#### News & Sentiment")
    bias_icon = BIAS_COLOR.get(result.bias, "⚪")
    st.markdown(f"{bias_icon} **{result.bias.upper()}** &nbsp; suggested: `{result.suggested_action}`")
    st.progress(result.confidence, text=f"Confidence: {result.confidence:.0%}")
    st.markdown(f"_{result.headline_summary}_")
    if result.positive_drivers:
        st.markdown("**Bullish drivers**")
        for d in result.positive_drivers:
            st.markdown(f"- {d}")
    if result.negative_drivers:
        st.markdown("**Bearish drivers**")
        for d in result.negative_drivers:
            st.markdown(f"- {d}")


def agent_card_risk(result: RiskOutput):
    st.markdown("#### Risk Manager")
    risk_icon    = RISK_COLOR.get(result.risk_rating, "⚪")
    approved_lbl = "✅ Approved" if result.approved else "❌ Vetoed"
    st.markdown(f"{risk_icon} **{result.risk_rating.upper()} RISK** &nbsp; {approved_lbl}")
    col1, col2 = st.columns(2)
    col1.metric("Max Size",     f"{result.max_position_pct:.0%}")
    col2.metric("Max Leverage", f"{result.max_leverage:.1f}x")
    if result.stop_loss_pct is not None:
        col1.metric("Stop Loss",   f"{result.stop_loss_pct:.1%}")
    if result.take_profit_pct is not None:
        col2.metric("Take Profit", f"{result.take_profit_pct:.1%}")
    if result.warnings:
        st.markdown("**Warnings**")
        for w in result.warnings:
            st.markdown(f"- {w}")


def agent_card_macro(result: MacroOutput):
    st.markdown("#### Macro Analyst")
    icon, label = REGIME_LABEL.get(result.macro_regime, ("⚪", result.macro_regime))
    appetite_icon = {"risk-on": "🟢", "risk-off": "🔴", "neutral": "⚪"}.get(result.risk_appetite, "⚪")
    st.markdown(f"{icon} **{label}** &nbsp; {appetite_icon} {result.risk_appetite}")
    st.progress(result.regime_confidence, text=f"Regime confidence: {result.regime_confidence:.0%}")
    adj = result.macro_risk_adjustment
    adj_str = f"{adj:+.0%}"
    adj_colour = "green" if adj > 0 else ("red" if adj < 0 else "gray")
    st.markdown(f"Macro risk adjustment: :{adj_colour}[**{adj_str}**]")
    st.markdown(f"_{result.implications_for_asset}_")
    if result.macro_tailwinds:
        st.markdown("**Tailwinds**")
        for t in result.macro_tailwinds:
            st.markdown(f"- {t}")
    if result.macro_headwinds:
        st.markdown("**Headwinds**")
        for h in result.macro_headwinds:
            st.markdown(f"- {h}")


def final_trade_ticket(result: PortfolioOutput, account_size: float):
    action       = result.final_action
    color        = ACTION_COLOR[action]
    label        = ACTION_LABEL[action]
    position_usd = result.position_size_pct * account_size

    st.markdown(
        f"""
        <div style="
            background-color: {color}22;
            border: 2px solid {color};
            border-radius: 12px;
            padding: 24px;
            margin-top: 8px;
        ">
        <h2 style="color: {color}; margin: 0 0 8px 0;">{label}</h2>
        <p style="font-size: 1.1rem; margin: 0;">
            Confidence: <strong>{result.confidence:.0%}</strong> &nbsp;|&nbsp;
            Position: <strong>{result.position_size_pct:.1%}</strong> (≈ ${position_usd:,.0f}) &nbsp;|&nbsp;
            Leverage: <strong>{result.max_leverage:.1f}x</strong>
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Rationale**")
        for r in result.entry_rationale:
            st.markdown(f"- {r}")
        if result.why_not_hold:
            st.markdown(f"_Why act now: {result.why_not_hold}_")
    with col2:
        st.markdown("**Key Risks**")
        for r in result.key_risks:
            st.markdown(f"- {r}")
        if result.stop_loss_pct:
            st.markdown(f"Stop loss: **{result.stop_loss_pct:.1%}**")
        if result.take_profit_pct:
            st.markdown(f"Take profit: **{result.take_profit_pct:.1%}**")
