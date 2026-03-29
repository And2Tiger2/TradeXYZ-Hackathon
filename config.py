import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

LLM_MODEL = "claude-sonnet-4-6"

SUPPORTED_SYMBOLS = ["BTC-USD", "ETH-USD", "AAPL", "SPY"]

CRYPTO_SYMBOLS = {"BTC-USD", "ETH-USD"}

SYMBOL_MAP = {
    "BTC-USD": "Bitcoin BTC cryptocurrency",
    "ETH-USD": "Ethereum ETH cryptocurrency",
    "AAPL": "Apple AAPL stock earnings",
    "SPY": "S&P 500 SPY market stocks",
}

SYMBOL_DISPLAY = {
    "BTC-USD": "Bitcoin (BTC)",
    "ETH-USD": "Ethereum (ETH)",
    "AAPL": "Apple Inc. (AAPL)",
    "SPY": "S&P 500 ETF (SPY)",
}

# Confidence below this threshold forces hold
MIN_CONFIDENCE_TO_TRADE = 0.50

# Headlines to fetch per symbol
NEWS_HEADLINE_COUNT = 8

# Price history
SWING_PERIOD = "3mo"
INTRADAY_PERIOD = "5d"
INTRADAY_INTERVAL = "1h"

# Monte Carlo
MC_N_PATHS = 500
MC_SWING_DAYS = 30
MC_INTRADAY_HOURS = 48

# Portfolio optimization risk-free rate (annualized)
RISK_FREE_RATE = 0.05
