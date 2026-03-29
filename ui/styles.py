import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ═══════════════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #07071a !important;
    color: #dde0f0 !important;
}
* { box-sizing: border-box; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ═══════════════════════════════════════════════════════════════
   MAIN CONTENT
═══════════════════════════════════════════════════════════════ */
.main .block-container {
    max-width: 1440px !important;
    padding: 1.25rem 2.5rem 3rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #05051a !important;
    border-right: 1px solid rgba(255,255,255,0.055) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.75rem 1.25rem !important;
}
[data-testid="stSidebar"] h1 {
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: rgba(180,185,220,0.4) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em !important;
    margin-top: 2px !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: rgba(200,205,235,0.65) !important;
    letter-spacing: 0.02em !important;
}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════════════════ */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: #f0f2ff !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
}
h2 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: rgba(220,225,255,0.9) !important;
    letter-spacing: -0.01em !important;
    margin-top: 0.3rem !important;
}
h3 {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: rgba(200,205,240,0.75) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
p, li { color: rgba(210,215,245,0.75); font-size: 0.875rem; line-height: 1.65; }
strong { color: rgba(230,235,255,0.95) !important; font-weight: 600 !important; }
code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(255,255,255,0.07) !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
    font-size: 0.82rem !important;
    color: #00d4ff !important;
}

/* ═══════════════════════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: rgba(14,14,35,0.85) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.22) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.07) !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(180,185,225,0.5) !important;
}
[data-testid="stMetricValue"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: #f0f2ff !important;
    letter-spacing: -0.02em !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   PRIMARY BUTTON (Analyze)
═══════════════════════════════════════════════════════════════ */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed 0%, #00c8ff 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,200,255,0.3) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }
.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(210,215,245,0.8) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
}

/* ═══════════════════════════════════════════════════════════════
   FORM CONTROLS
═══════════════════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: rgba(12,12,30,0.95) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #dde0f0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: rgba(0,212,255,0.4) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.12) !important;
}
.stNumberInput input, .stTextInput input {
    background: rgba(12,12,30,0.95) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #f0f2ff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: rgba(0,212,255,0.4) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
}

/* ═══════════════════════════════════════════════════════════════
   RADIO / SELECT SLIDER
═══════════════════════════════════════════════════════════════ */
[data-testid="stRadio"] > div {
    gap: 6px !important;
}
[data-testid="stRadio"] label {
    font-size: 0.8rem !important;
    color: rgba(200,205,235,0.65) !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.8rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,10,26,0.8) !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    width: fit-content !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(190,195,230,0.55) !important;
    border-radius: 9px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 7px 18px !important;
    border: none !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,58,237,0.2) !important;
    color: #00d4ff !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ═══════════════════════════════════════════════════════════════
   PROGRESS BARS
═══════════════════════════════════════════════════════════════ */
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 100px !important;
    height: 5px !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #7c3aed, #00d4ff) !important;
    border-radius: 100px !important;
    transition: width 0.7s cubic-bezier(0.16,1,0.3,1) !important;
}

/* ═══════════════════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(10,10,25,0.7) !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    color: rgba(190,195,230,0.6) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary:hover {
    color: #00d4ff !important;
}

/* ═══════════════════════════════════════════════════════════════
   BORDERED CONTAINERS
═══════════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: rgba(11,11,27,0.9) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 18px !important;
    padding: 1.4rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 1.75rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════════════════════ */
[data-testid="stInfo"] {
    background: rgba(0,212,255,0.07) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 12px !important;
}
[data-testid="stInfo"] p { color: rgba(160,220,245,0.9) !important; }
[data-testid="stWarning"] {
    background: rgba(251,191,36,0.07) !important;
    border: 1px solid rgba(251,191,36,0.22) !important;
    border-radius: 12px !important;
}
[data-testid="stError"] {
    background: rgba(255,45,85,0.07) !important;
    border: 1px solid rgba(255,45,85,0.22) !important;
    border-radius: 12px !important;
}
[data-testid="stSuccess"] {
    background: rgba(0,232,123,0.07) !important;
    border: 1px solid rgba(0,232,123,0.22) !important;
    border-radius: 12px !important;
}

/* ═══════════════════════════════════════════════════════════════
   DATAFRAME
═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* ═══════════════════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.35); }

/* ═══════════════════════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════════════════════ */
.stSpinner svg { stroke: #00d4ff !important; }

/* ═══════════════════════════════════════════════════════════════
   CAPTION
═══════════════════════════════════════════════════════════════ */
[data-testid="stCaptionContainer"] p {
    color: rgba(160,165,210,0.45) !important;
    font-size: 0.73rem !important;
    line-height: 1.6 !important;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENT STYLES
═══════════════════════════════════════════════════════════════ */

/* Page header */
.tx-header {
    padding: 0.5rem 0 1.5rem;
    animation: txFadeDown 0.5s ease;
}
.tx-header h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #f0f2ff 0%, rgba(200,205,255,0.7) 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
}
.tx-header .sub {
    font-size: 0.82rem;
    color: rgba(170,175,220,0.5);
    margin-top: 4px;
    letter-spacing: 0.02em;
}
.tx-header .sub span { color: rgba(0,212,255,0.7); font-weight: 500; }

/* Section header */
.tx-section {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.75rem 0 0.9rem;
}
.tx-section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.07), transparent);
}
.tx-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: rgba(160,165,220,0.55);
}

/* Agent card */
.tx-agent-card {
    background: rgba(10,10,26,0.95);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 22px 22px 18px;
    position: relative;
    overflow: hidden;
    animation: txFadeUp 0.45s ease;
    height: 100%;
}
.tx-agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, rgba(124,58,237,0.6), rgba(0,212,255,0.6));
}
.tx-agent-card.bull::before { background: linear-gradient(90deg, #00e87b, #00d4ff); }
.tx-agent-card.bear::before { background: linear-gradient(90deg, #ff2d55, #ff7b00); }
.tx-agent-card.neutral::before { background: linear-gradient(90deg, #6b7280, #4b5563); }

.tx-agent-card .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
}
.tx-agent-card .card-icon {
    width: 32px; height: 32px;
    background: rgba(255,255,255,0.06);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
}
.tx-agent-card .card-title {
    flex: 1;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(180,185,230,0.6);
}
.tx-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 100px;
    text-transform: uppercase;
}
.tx-badge.bull { background: rgba(0,232,123,0.15); color: #00e87b; border: 1px solid rgba(0,232,123,0.3); }
.tx-badge.bear { background: rgba(255,45,85,0.15);  color: #ff2d55; border: 1px solid rgba(255,45,85,0.3); }
.tx-badge.neutral { background: rgba(107,114,128,0.2); color: #9ca3af; border: 1px solid rgba(107,114,128,0.3); }

.tx-confidence {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.tx-confidence-label { font-size: 0.68rem; font-weight: 500; color: rgba(160,165,215,0.5); letter-spacing: 0.06em; text-transform: uppercase; min-width: 70px; }
.tx-confidence-bar {
    flex: 1;
    height: 4px;
    background: rgba(255,255,255,0.07);
    border-radius: 100px;
    overflow: hidden;
}
.tx-confidence-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #7c3aed, #00d4ff);
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
}
.tx-confidence-fill.bull { background: linear-gradient(90deg, #00e87b, #00d4ff); }
.tx-confidence-fill.bear { background: linear-gradient(90deg, #ff2d55, #ff7b00); }
.tx-confidence-val { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700; color: #f0f2ff; min-width: 36px; text-align: right; }

.tx-signal-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.tx-signal-list li { font-size: 0.78rem; color: rgba(200,205,240,0.7); display: flex; align-items: flex-start; gap: 7px; line-height: 1.45; }
.tx-signal-list li::before { content: '›'; color: #00d4ff; font-weight: 700; margin-top: -1px; flex-shrink: 0; }
.tx-signal-list li.risk::before { color: #ff2d55; }
.tx-signal-list li.bull::before { color: #00e87b; }

.tx-sub-label { font-size: 0.67rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(160,165,215,0.4); margin: 12px 0 6px; }

.tx-risk-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 12px 0;
}
.tx-mini-metric {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
}
.tx-mini-metric .label { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(160,165,215,0.45); display: block; margin-bottom: 4px; }
.tx-mini-metric .value { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; color: #f0f2ff; }

/* Macro regime badge */
.tx-regime-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.tx-regime-pill.risk-on  { background: rgba(0,232,123,0.12); color: #00e87b; border: 1px solid rgba(0,232,123,0.25); }
.tx-regime-pill.risk-off { background: rgba(255,45,85,0.12);  color: #ff2d55; border: 1px solid rgba(255,45,85,0.25); }
.tx-regime-pill.neutral  { background: rgba(107,114,128,0.15); color: #9ca3af; border: 1px solid rgba(107,114,128,0.25); }

/* Final trade ticket */
.tx-ticket {
    border-radius: 20px;
    padding: 28px 32px;
    position: relative;
    overflow: hidden;
    animation: txFadeUp 0.5s ease;
    margin: 0.5rem 0 1rem;
}
.tx-ticket.long  { background: rgba(0,232,123,0.06); border: 1px solid rgba(0,232,123,0.25); }
.tx-ticket.short { background: rgba(255,45,85,0.06);  border: 1px solid rgba(255,45,85,0.25); }
.tx-ticket.hold  { background: rgba(107,114,128,0.06); border: 1px solid rgba(107,114,128,0.2); }

.tx-ticket::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.tx-ticket.long::before  { background: linear-gradient(90deg, #00e87b, #00d4ff); }
.tx-ticket.short::before { background: linear-gradient(90deg, #ff2d55, #ff7b00); }
.tx-ticket.hold::before  { background: linear-gradient(90deg, #6b7280, #4b5563); }

.tx-ticket-action {
    font-family: 'Inter', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 8px;
}
.tx-ticket.long  .tx-ticket-action { color: #00e87b; }
.tx-ticket.short .tx-ticket-action { color: #ff2d55; }
.tx-ticket.hold  .tx-ticket-action { color: #6b7280; }

.tx-ticket-sub {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 22px;
    flex-wrap: wrap;
}
.tx-ticket-sub .stat { display: flex; flex-direction: column; gap: 2px; }
.tx-ticket-sub .stat .s-label { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(160,165,215,0.45); }
.tx-ticket-sub .stat .s-value { font-family: 'JetBrains Mono', monospace; font-size: 1.05rem; font-weight: 700; color: #f0f2ff; }
.tx-ticket-sub .divider { width: 1px; height: 30px; background: rgba(255,255,255,0.08); }

.tx-ticket-body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    padding-top: 18px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.tx-ticket-col .col-title { font-size: 0.67rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(160,165,215,0.4); margin-bottom: 10px; }
.tx-ticket-col .rationale-item { font-size: 0.8rem; color: rgba(200,205,240,0.75); display: flex; gap: 8px; margin-bottom: 7px; line-height: 1.45; }
.tx-ticket-col .rationale-item::before { content: '→'; color: #00d4ff; font-weight: 700; flex-shrink: 0; }
.tx-ticket-col .risk-item { font-size: 0.8rem; color: rgba(200,205,240,0.75); display: flex; gap: 8px; margin-bottom: 7px; line-height: 1.45; }
.tx-ticket-col .risk-item::before { content: '⚠'; font-size: 0.7rem; color: #fb923c; flex-shrink: 0; margin-top: 1px; }
.tx-ticket-why { margin-top: 14px; font-size: 0.78rem; font-style: italic; color: rgba(170,180,230,0.5); }

.tx-ticket-levels {
    display: flex;
    gap: 10px;
    margin-top: 16px;
    flex-wrap: wrap;
}
.tx-level-chip {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 8px 16px;
    min-width: 90px;
}
.tx-level-chip .lc-label { font-size: 0.6rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(160,165,215,0.4); margin-bottom: 3px; }
.tx-level-chip .lc-value { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 700; }
.tx-level-chip.stop  .lc-value { color: #ff2d55; }
.tx-level-chip.target .lc-value { color: #00e87b; }
.tx-level-chip.leverage .lc-value { color: #00d4ff; }

/* Disagreement banner */
.tx-disagree {
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.18);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.77rem;
    color: rgba(251,191,36,0.8);
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Sim stat row */
.tx-sim-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1rem;
}
.tx-sim-stat {
    flex: 1;
    background: rgba(10,10,26,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
}
.tx-sim-stat .ss-label { font-size: 0.63rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(160,165,215,0.45); margin-bottom: 5px; display: block; }
.tx-sim-stat .ss-value { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #f0f2ff; }

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════════════════════════ */
@keyframes txFadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes txFadeDown {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes txPulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}
.live-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00e87b;
    display: inline-block;
    margin-right: 5px;
    animation: txPulse 2s ease infinite;
}

</style>
""", unsafe_allow_html=True)
