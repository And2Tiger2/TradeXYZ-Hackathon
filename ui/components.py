import streamlit as st
from schemas.outputs import TechnicalOutput, NewsOutput, RiskOutput, PortfolioOutput, MacroOutput

# ── Helpers ────────────────────────────────────────────────────────────────────

def _bias_cls(bias: str) -> str:
    return {"bullish": "bull", "bearish": "bear", "neutral": "neutral"}.get(bias, "neutral")

def _risk_cls(rating: str) -> str:
    return {"low": "bull", "medium": "neutral", "high": "bear"}.get(rating, "neutral")

def _signals_html(items: list[str], cls: str = "") -> str:
    return "".join(f'<li class="{cls}">{i}</li>' for i in items)

def _section(title: str) -> None:
    st.markdown(
        f'<div class="tx-section"><span class="tx-section-title">{title}</span>'
        f'<div class="tx-section-line"></div></div>',
        unsafe_allow_html=True,
    )

# ── Page header ────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle_parts: dict[str, str]) -> None:
    sub_html = " &nbsp;·&nbsp; ".join(
        f'<span>{v}</span>' for v in subtitle_parts.values()
    )
    st.markdown(
        f'<div class="tx-header"><h1>{title}</h1>'
        f'<div class="sub">{sub_html}</div></div>',
        unsafe_allow_html=True,
    )

def section_header(title: str) -> None:
    _section(title)

# ── Agent cards ────────────────────────────────────────────────────────────────

def agent_card_technical(result: TechnicalOutput) -> None:
    cls  = _bias_cls(result.bias)
    pct  = int(result.confidence * 100)
    sigs = _signals_html(result.signals, "bull" if cls == "bull" else "")
    rsks = _signals_html(result.risks, "risk")
    badge_label = result.bias.upper()

    st.markdown(f"""
<div class="tx-agent-card {cls}">
  <div class="card-header">
    <div class="card-icon">📈</div>
    <div class="card-title">Technical Analyst</div>
    <span class="tx-badge {cls}">{badge_label}</span>
  </div>
  <div class="tx-confidence">
    <span class="tx-confidence-label">Confidence</span>
    <div class="tx-confidence-bar"><div class="tx-confidence-fill {cls}" style="width:{pct}%"></div></div>
    <span class="tx-confidence-val">{pct}%</span>
  </div>
  <div class="tx-sub-label">Signals</div>
  <ul class="tx-signal-list">{sigs}</ul>
  <div class="tx-sub-label">Risks</div>
  <ul class="tx-signal-list">{rsks}</ul>
</div>
""", unsafe_allow_html=True)


def agent_card_news(result: NewsOutput) -> None:
    cls  = _bias_cls(result.bias)
    pct  = int(result.confidence * 100)
    pos  = _signals_html(result.positive_drivers, "bull")
    neg  = _signals_html(result.negative_drivers, "risk")

    st.markdown(f"""
<div class="tx-agent-card {cls}">
  <div class="card-header">
    <div class="card-icon">📰</div>
    <div class="card-title">News &amp; Sentiment</div>
    <span class="tx-badge {cls}">{result.bias.upper()}</span>
  </div>
  <div class="tx-confidence">
    <span class="tx-confidence-label">Confidence</span>
    <div class="tx-confidence-bar"><div class="tx-confidence-fill {cls}" style="width:{pct}%"></div></div>
    <span class="tx-confidence-val">{pct}%</span>
  </div>
  <p style="font-size:0.78rem;color:rgba(190,195,235,0.6);font-style:italic;margin:0 0 10px;">{result.headline_summary}</p>
  <div class="tx-sub-label">Bullish Drivers</div>
  <ul class="tx-signal-list">{pos}</ul>
  <div class="tx-sub-label">Bearish Drivers</div>
  <ul class="tx-signal-list">{neg}</ul>
</div>
""", unsafe_allow_html=True)


def agent_card_risk(result: RiskOutput) -> None:
    cls          = _risk_cls(result.risk_rating)
    approved_lbl = '<span style="color:#00e87b;font-weight:700;">✓ Approved</span>' if result.approved \
                   else '<span style="color:#ff2d55;font-weight:700;">✕ Vetoed</span>'
    warns = _signals_html(result.warnings, "risk")

    stop_html   = f'<div class="tx-mini-metric"><span class="label">Stop Loss</span><span class="value" style="color:#ff2d55;">{result.stop_loss_pct:.1%}</span></div>'   if result.stop_loss_pct   else ""
    target_html = f'<div class="tx-mini-metric"><span class="label">Take Profit</span><span class="value" style="color:#00e87b;">{result.take_profit_pct:.1%}</span></div>' if result.take_profit_pct else ""

    st.markdown(f"""
<div class="tx-agent-card {cls}">
  <div class="card-header">
    <div class="card-icon">🛡️</div>
    <div class="card-title">Risk Manager</div>
    <span class="tx-badge {cls}">{result.risk_rating.upper()}</span>
  </div>
  <div style="font-size:0.85rem;margin-bottom:12px;">{approved_lbl}</div>
  <div class="tx-risk-metrics">
    <div class="tx-mini-metric">
      <span class="label">Max Position</span>
      <span class="value">{result.max_position_pct:.0%}</span>
    </div>
    <div class="tx-mini-metric">
      <span class="label">Max Leverage</span>
      <span class="value" style="color:#00d4ff;">{result.max_leverage:.1f}×</span>
    </div>
    {stop_html}
    {target_html}
  </div>
  <div class="tx-sub-label">Warnings</div>
  <ul class="tx-signal-list">{warns}</ul>
</div>
""", unsafe_allow_html=True)


def agent_card_macro(result: MacroOutput) -> None:
    ra_cls = {"risk-on": "risk-on", "risk-off": "risk-off", "neutral": "neutral"}.get(result.risk_appetite, "neutral")
    pct    = int(result.regime_confidence * 100)
    regime_display = result.macro_regime.replace("_", " ").title()
    adj    = result.macro_risk_adjustment
    adj_color = "#00e87b" if adj > 0 else ("#ff2d55" if adj < 0 else "#6b7280")
    adj_str = f"{adj:+.0%}"
    tw = _signals_html(result.macro_tailwinds, "bull")
    hw = _signals_html(result.macro_headwinds, "risk")

    st.markdown(f"""
<div class="tx-agent-card neutral">
  <div class="card-header">
    <div class="card-icon">🌐</div>
    <div class="card-title">Macro Analyst</div>
    <span class="tx-badge neutral">{regime_display}</span>
  </div>
  <span class="tx-regime-pill {ra_cls}">{result.risk_appetite.upper()}</span>
  <div class="tx-confidence">
    <span class="tx-confidence-label">Confidence</span>
    <div class="tx-confidence-bar"><div class="tx-confidence-fill" style="width:{pct}%"></div></div>
    <span class="tx-confidence-val">{pct}%</span>
  </div>
  <p style="font-size:0.78rem;color:rgba(190,195,235,0.6);font-style:italic;margin:0 0 10px;">{result.implications_for_asset}</p>
  <div style="font-size:0.78rem;margin-bottom:12px;">
    Risk adj: <span style="font-family:'JetBrains Mono',monospace;font-weight:700;color:{adj_color};">{adj_str}</span>
  </div>
  <div class="tx-sub-label">Tailwinds</div>
  <ul class="tx-signal-list">{tw}</ul>
  <div class="tx-sub-label">Headwinds</div>
  <ul class="tx-signal-list">{hw}</ul>
</div>
""", unsafe_allow_html=True)


# ── Final trade ticket ─────────────────────────────────────────────────────────

def final_trade_ticket(result: PortfolioOutput, account_size: float) -> None:
    action       = result.final_action
    action_label = {"long": "LONG ▲", "short": "SHORT ▼", "hold": "HOLD —"}[action]
    position_usd = result.position_size_pct * account_size
    conf_pct     = int(result.confidence * 100)

    rationale_html = "".join(f'<div class="rationale-item">{r}</div>' for r in result.entry_rationale)
    risks_html     = "".join(f'<div class="risk-item">{r}</div>' for r in result.key_risks)
    why_html       = f'<div class="tx-ticket-why">Why act now: {result.why_not_hold}</div>' if result.why_not_hold else ""

    stop_chip    = f'<div class="tx-level-chip stop"><span class="lc-label">Stop Loss</span><span class="lc-value">{result.stop_loss_pct:.1%}</span></div>'   if result.stop_loss_pct   else ""
    target_chip  = f'<div class="tx-level-chip target"><span class="lc-label">Take Profit</span><span class="lc-value">{result.take_profit_pct:.1%}</span></div>' if result.take_profit_pct else ""
    lev_chip     = f'<div class="tx-level-chip leverage"><span class="lc-label">Leverage</span><span class="lc-value">{result.max_leverage:.1f}×</span></div>'

    st.markdown(f"""
<div class="tx-ticket {action}">
  <div class="tx-ticket-action">{action_label}</div>
  <div class="tx-ticket-sub">
    <div class="stat">
      <span class="s-label">Confidence</span>
      <span class="s-value">{conf_pct}%</span>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <span class="s-label">Position Size</span>
      <span class="s-value">{result.position_size_pct:.1%}</span>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <span class="s-label">Capital at Risk</span>
      <span class="s-value">${position_usd:,.0f}</span>
    </div>
  </div>
  <div class="tx-ticket-levels">
    {lev_chip}{stop_chip}{target_chip}
  </div>
  <div class="tx-ticket-body">
    <div class="tx-ticket-col">
      <div class="col-title">Entry Rationale</div>
      {rationale_html}
      {why_html}
    </div>
    <div class="tx-ticket-col">
      <div class="col-title">Key Risks</div>
      {risks_html}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Agent disagreement banner ──────────────────────────────────────────────────

def disagreement_banner(actions: dict[str, str]) -> None:
    parts = " &nbsp;·&nbsp; ".join(
        f'<strong>{k}</strong>: {v}' for k, v in actions.items()
    )
    st.markdown(
        f'<div class="tx-disagree">⚡ Agent disagreement &nbsp;—&nbsp; {parts}</div>',
        unsafe_allow_html=True,
    )


# ── Simulation stats row ───────────────────────────────────────────────────────

def sim_stats_row(prob_up: float, expected_return: float, var_95: float) -> None:
    var_color = "#ff2d55" if var_95 < -0.05 else "#fb923c"
    er_color  = "#00e87b" if expected_return > 0 else "#ff2d55"
    st.markdown(f"""
<div class="tx-sim-row">
  <div class="tx-sim-stat">
    <span class="ss-label">P(Price Ends Higher)</span>
    <span class="ss-value">{prob_up:.0%}</span>
  </div>
  <div class="tx-sim-stat">
    <span class="ss-label">Median Expected Return</span>
    <span class="ss-value" style="color:{er_color};">{expected_return:+.1%}</span>
  </div>
  <div class="tx-sim-stat">
    <span class="ss-label">95% Value at Risk</span>
    <span class="ss-value" style="color:{var_color};">{var_95:.1%}</span>
  </div>
</div>
""", unsafe_allow_html=True)
