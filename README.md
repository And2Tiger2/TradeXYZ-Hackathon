# TradeXYZ-Hackathon

A multi-agent AI trading desk built with Streamlit. Four specialized agents (Technical, News, Risk, Portfolio) analyze market data and collaborate to produce a final trade recommendation.

## Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/)
- A [NewsAPI key](https://newsapi.org/) (optional — headlines will be skipped if missing)

## Setup

1. **Clone the repo and navigate into it:**

   ```bash
   git clone https://github.com/your-org/TradeXYZ-Hackathon.git
   cd TradeXYZ-Hackathon
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your keys:

   ```
   ANTHROPIC_API_KEY=your_anthropic_key_here
   NEWS_API_KEY=your_newsapi_key_here
   ```

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

1. In the **sidebar**, select a symbol, time horizon, account size, risk mode, and leverage limits.
2. Click **Analyze** to run all four agents.
3. View the market snapshot, per-agent analysis cards, and the final trade recommendation.
