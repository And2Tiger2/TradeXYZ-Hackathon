# Multi-Agent Trading Desk — Build Plan

## Concept

A transparent, risk-aware multi-agent decision engine for trading ideas.

Four specialized AI agents each produce a structured opinion. A final Portfolio Manager agent synthesizes them into one trade recommendation. The system biases toward inaction unless evidence is strong.

**Pitch:** "We split trading decisions across specialized agents — technical analyst, news analyst, risk manager, and portfolio manager — and give the risk manager veto power. The result is transparent, controllable, and finance-relevant."

---

## Folder Structure

```
TradeXYZ-Hackathon/
├── app.py                     # Streamlit entry point
├── config.py                  # Constants, symbols, thresholds
├── requirements.txt
├── agents/
│   ├── __init__.py
│   ├── technical.py           # Technical analysis agent
│   ├── news.py                # News/sentiment agent
│   ├── risk.py                # Risk manager agent
│   └── portfolio.py           # Final decision agent
├── data/
│   ├── __init__.py
│   ├── market.py              # yfinance price/OHLCV fetch
│   ├── news.py                # NewsAPI / Tavily headline fetch
│   └── indicators.py          # SMA, RSI, volatility calculations
├── schemas/
│   ├── __init__.py
│   ├── inputs.py              # UserInput Pydantic model
│   └── outputs.py             # All agent output Pydantic models
└── ui/
    ├── components.py          # Reusable Streamlit UI components
    └── charts.py              # Plotly price chart helper
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| LLM | Anthropic Claude (claude-sonnet-4-6) or OpenAI GPT-4o |
| Market data | yfinance |
| News data | NewsAPI or Tavily |
| Validation | Pydantic v2 |
| Charts | Plotly |
| Config | python-dotenv |

**`.env` file (not committed):**
```
ANTHROPIC_API_KEY=...
NEWS_API_KEY=...        # or TAVILY_API_KEY=...
```

---

## Pydantic Schemas

### `schemas/inputs.py`

```python
from pydantic import BaseModel
from typing import Literal

class UserInput(BaseModel):
    symbol: str                          # e.g. "BTC-USD", "ETH-USD", "AAPL"
    time_horizon: Literal["intraday", "swing"]
    account_size: float                  # USD
    risk_mode: Literal["aggressive", "balanced", "conservative"]
    max_risk_per_trade_pct: float        # e.g. 0.01 = 1%
    max_leverage: float                  # e.g. 2.0
```

### `schemas/outputs.py`

```python
from pydantic import BaseModel
from typing import Optional, Literal

class TechnicalOutput(BaseModel):
    bias: Literal["bullish", "bearish", "neutral"]
    confidence: float                    # 0.0 - 1.0
    signals: list[str]
    risks: list[str]
    suggested_action: Literal["long", "short", "hold"]

class NewsOutput(BaseModel):
    bias: Literal["bullish", "bearish", "neutral"]
    confidence: float
    headline_summary: str
    positive_drivers: list[str]
    negative_drivers: list[str]
    suggested_action: Literal["long", "short", "hold"]

class RiskOutput(BaseModel):
    risk_rating: Literal["low", "medium", "high"]
    approved: bool
    max_position_pct: float
    max_leverage: float
    stop_loss_pct: Optional[float]
    take_profit_pct: Optional[float]
    warnings: list[str]
    override_action: Optional[Literal["hold"]]

class PortfolioOutput(BaseModel):
    final_action: Literal["long", "short", "hold"]
    confidence: float
    position_size_pct: float
    max_leverage: float
    entry_rationale: list[str]
    stop_loss_pct: Optional[float]
    take_profit_pct: Optional[float]
    key_risks: list[str]
    why_not_hold: Optional[str]
```

---

## Data Layer

### `data/market.py`
- `fetch_ohlcv(symbol, period="1mo")` → DataFrame via yfinance
- `get_latest_price(symbol)` → float
- `get_returns(df)` → dict with `1d`, `5d`, `1mo` return percentages

### `data/indicators.py`
- `compute_sma(df, window)` → Series
- `compute_rsi(df, window=14)` → float (latest value)
- `compute_volatility(df, window=20)` → float (annualized)

### `data/news.py`
- `fetch_headlines(symbol, n=8)` → list of headline strings
- Use NewsAPI `everything` endpoint, or Tavily search as fallback
- Map symbols to search terms: `"BTC-USD"` → `"Bitcoin"`, `"AAPL"` → `"Apple stock"`

**Symbol-to-search-term map** (in `config.py`):
```python
SYMBOL_MAP = {
    "BTC-USD": "Bitcoin BTC",
    "ETH-USD": "Ethereum ETH",
    "AAPL": "Apple AAPL stock",
    "SPY": "S&P 500 SPY",
}
```

---

## Agent Layer

Each agent follows the same pattern:

1. Build a `context` dict from data
2. Construct a role-specific system prompt
3. Call the LLM with `response_format=json` (or prompt it to return JSON)
4. Parse and validate with Pydantic
5. Return the typed output

### LLM call wrapper (`agents/__init__.py`)
```python
def call_llm(system_prompt: str, user_message: str, schema: type) -> dict:
    # Call Anthropic or OpenAI
    # Parse JSON from response
    # Validate with schema(**parsed)
    # Return validated model
```

### `agents/technical.py` — System Prompt

```
You are a quantitative technical analyst.
Given current market statistics for a single asset, determine the short-term directional bias.
Consider only: price trend (SMA), momentum (recent returns), overbought/oversold (RSI), and volatility.
Do not reference fundamentals or news.
Be concise. Return only valid JSON matching this schema:
{
  "bias": "bullish" | "bearish" | "neutral",
  "confidence": 0.0-1.0,
  "signals": ["...", "..."],
  "risks": ["...", "..."],
  "suggested_action": "long" | "short" | "hold"
}
```

**User message:** formatted market_context JSON (price, returns, SMA, RSI, volatility)

### `agents/news.py` — System Prompt

```
You are a financial news and market sentiment analyst.
You will be given a list of recent news headlines about an asset.
Summarize the sentiment and identify the key bullish and bearish drivers.
Use only what is provided. Do not invent facts.
Return only valid JSON matching this schema:
{
  "bias": "bullish" | "bearish" | "neutral",
  "confidence": 0.0-1.0,
  "headline_summary": "...",
  "positive_drivers": ["...", "..."],
  "negative_drivers": ["...", "..."],
  "suggested_action": "long" | "short" | "hold"
}
```

**User message:** formatted list of headline strings

### `agents/risk.py` — System Prompt

```
You are a trading risk manager. Capital preservation is your first priority.
You are given the outputs of a technical analyst and a news analyst, plus the user's risk constraints.
Your job is to determine whether a trade is safe to execute, and at what size and leverage.
You may veto the trade entirely by setting approved=false and override_action="hold".
Bias toward smaller positions and lower leverage when uncertain.
Return only valid JSON matching this schema:
{
  "risk_rating": "low" | "medium" | "high",
  "approved": true | false,
  "max_position_pct": 0.0-1.0,
  "max_leverage": 0.0-N,
  "stop_loss_pct": 0.0-1.0 or null,
  "take_profit_pct": 0.0-1.0 or null,
  "warnings": ["...", "..."],
  "override_action": "hold" | null
}
```

**User message:** `{technical_output, news_output, risk_constraints}`

### `agents/portfolio.py` — System Prompt

```
You are the portfolio manager and final decision maker on a trading desk.
You receive structured reports from a technical analyst, news analyst, and risk manager.
Your job is to synthesize these into one final trade recommendation.
Rules:
- If the risk manager has approved=false, you must output final_action="hold".
- Default to "hold" when agent views are mixed or confidence is weak (below 0.55).
- Never recommend a position larger than what the risk manager approved.
- Be honest about uncertainty — do not force conviction.
Return only valid JSON matching this schema:
{
  "final_action": "long" | "short" | "hold",
  "confidence": 0.0-1.0,
  "position_size_pct": 0.0-1.0,
  "max_leverage": 0.0-N,
  "entry_rationale": ["...", "...", "..."],
  "stop_loss_pct": 0.0-1.0 or null,
  "take_profit_pct": 0.0-1.0 or null,
  "key_risks": ["...", "..."],
  "why_not_hold": "..." or null
}
```

**User message:** `{technical_output, news_output, risk_output, user_constraints}`

---

## Hard Constraints (Code-Enforced, Not LLM)

After parsing the portfolio output, enforce these in Python — do not trust the LLM alone:

```python
def enforce_constraints(output: PortfolioOutput, user: UserInput) -> PortfolioOutput:
    output.position_size_pct = min(output.position_size_pct, user.max_risk_per_trade_pct * 10)
    output.max_leverage = min(output.max_leverage, user.max_leverage)
    if output.confidence < 0.50:
        output.final_action = "hold"
        output.position_size_pct = 0.0
    return output
```

---

## Streamlit UI — `app.py`

### Layout

```
Sidebar                         Main area
─────────────────────           ──────────────────────────────────────────
Symbol dropdown                 [Market Snapshot — 4 metric cards]
Time horizon                    [Price chart — 30d]
Account size
Risk mode                       [Agent Panel — 4 cards in 2×2 grid]
Max risk % / trade              Technical  |  News
Max leverage                    Risk Mgr   |  Portfolio Manager
[Analyze] button
                                [Final Trade Ticket — large card]

                                [Debug Expander — raw JSON, prompts, logs]
```

### Sidebar inputs
```python
symbol = st.selectbox("Symbol", ["BTC-USD", "ETH-USD", "AAPL", "SPY"])
horizon = st.radio("Time Horizon", ["intraday", "swing"])
account_size = st.number_input("Account Size (USD)", value=10000)
risk_mode = st.select_slider("Risk Mode", ["conservative", "balanced", "aggressive"])
max_risk_pct = st.slider("Max Risk per Trade (%)", 0.5, 5.0, 1.0) / 100
max_leverage = st.slider("Max Leverage", 1.0, 10.0, 2.0)
run = st.button("Analyze", type="primary")
```

### Market snapshot row
```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Price", f"${price:,.2f}", f"{ret_1d:+.1%}")
col2.metric("5d Return", f"{ret_5d:+.1%}")
col3.metric("RSI (14)", f"{rsi:.1f}")
col4.metric("20d Vol", f"{vol:.0%}")
```

### Agent cards
Each agent card shows:
- Badge: bullish / bearish / neutral (color-coded green/red/gray)
- Confidence bar: `st.progress(confidence)`
- Bullet list: signals or drivers
- Risks

### Final trade ticket
Large colored box:
- Action: **LONG** / **SHORT** / **HOLD** (green/red/gray)
- Confidence percentage
- Position size
- Leverage, Stop Loss, Take Profit
- Rationale bullets
- Key risk bullets

### Debug expander
```python
with st.expander("Raw Agent Outputs"):
    st.json(technical_output.model_dump())
    st.json(news_output.model_dump())
    st.json(risk_output.model_dump())
    st.json(portfolio_output.model_dump())
```

---

## Build Order (4-Hour Timeline)

### Hour 1 — Data + Schemas
- [ ] `requirements.txt` and `.env`
- [ ] `schemas/inputs.py` and `schemas/outputs.py` (Pydantic models)
- [ ] `data/market.py` — yfinance fetch + returns
- [ ] `data/indicators.py` — SMA, RSI, volatility
- [ ] `data/news.py` — NewsAPI headlines fetch
- [ ] `config.py` — symbol map, API keys, thresholds

### Hour 2 — Agent Layer
- [ ] `agents/__init__.py` — shared LLM call wrapper
- [ ] `agents/technical.py` — prompt + parse + validate
- [ ] `agents/news.py` — prompt + parse + validate
- [ ] `agents/risk.py` — prompt + parse + validate
- [ ] `agents/portfolio.py` — prompt + parse + validate
- [ ] `enforce_constraints()` function

### Hour 3 — Streamlit UI
- [ ] `app.py` — sidebar + main layout skeleton
- [ ] Market snapshot cards + price chart
- [ ] Four agent panels
- [ ] Final trade ticket card
- [ ] Debug / raw JSON expander
- [ ] Loading spinners during agent calls

### Hour 4 — Polish + Fallbacks
- [ ] Error handling: bad API responses, LLM JSON parse failures
- [ ] Fallback: if NewsAPI fails, use Tavily or skip news agent
- [ ] Cache market data with `@st.cache_data` so re-runs are fast
- [ ] Test all 4 supported symbols
- [ ] Clean up UI spacing and colors
- [ ] Write a 3-sentence demo pitch

---

## requirements.txt

```
streamlit
anthropic          # or openai
yfinance
pydantic>=2.0
plotly
python-dotenv
requests           # for NewsAPI
tavily-python      # optional fallback news source
pandas
numpy
```

---

## Supported Symbols

| Symbol | Asset | News search term |
|---|---|---|
| BTC-USD | Bitcoin | "Bitcoin BTC" |
| ETH-USD | Ethereum | "Ethereum ETH" |
| AAPL | Apple | "Apple AAPL stock" |
| SPY | S&P 500 ETF | "S&P 500 market" |

---

## Key Design Decisions

1. **Risk manager has veto power** — enforced in both the LLM prompt and in Python code.
2. **Hold is the default** — confidence must exceed 0.55 for any position; below that, system returns hold automatically.
3. **Structured JSON outputs** — all agents return Pydantic-validated JSON, not freeform text. This makes the app robust and transparent.
4. **Agents are isolated** — technical agent sees no headlines; news agent sees no price data. Separation makes disagreement meaningful.
5. **Hard code-level constraints** — position size and leverage are capped in Python after LLM response, so the LLM cannot override risk limits.

---

## Demo Script (for judges)

1. Select **BTC-USD**, balanced mode, $10,000 account, 1% max risk, 2x max leverage.
2. Click **Analyze**.
3. Show the four agent cards loading sequentially.
4. Point to the risk manager card — "notice the risk manager can veto regardless of what the other agents say."
5. Show the final trade ticket.
6. Open the debug expander — "every decision is fully inspectable."
7. Switch to **conservative** mode — show how the risk manager tightens and may flip the result to hold.

---

## Stretch Goals (only if MVP is done early)

- Agent disagreement summary card: "Technical is bullish but Risk manager is cautious"
- Paper trade log: save decisions to a local JSON file with timestamps
- Re-run over last 5 days to show consistency
- "Ask the desk" chat input for follow-up questions about the recommendation
- Side-by-side comparison of two symbols
