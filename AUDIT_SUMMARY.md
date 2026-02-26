# Polymarket/agents Audit (2026-02-26)

Repository: https://github.com/Polymarket/agents

## How it works (short)
1. Pulls tradeable events/markets from Gamma/CLOB.
2. Uses Chroma RAG + OpenAI embeddings to filter events/markets.
3. Uses LLM prompts to estimate odds and generate a trade suggestion.
4. Converts suggestion to trade size and can execute market orders (currently commented in trade flow).

## Security / privacy findings

### Confirmed risks
- Private key may be printed in test helper (`agents/polymarket/polymarket.py` test function).
- Infinite recursive retry on trade failure (`agents/application/trade.py`).
- Trade size parsing is fragile and could over-allocate bankroll (`agents/application/executor.py`).
- Scheduler implementation broken by class naming collision/self-recursion (`agents/application/cron.py`).
- Env var typo in search connector (`OPEN_API_KEY` vs `OPENAI_API_KEY`).

### No direct leaked secrets found
- `.env.example` contains placeholders only.
- `.gitignore` excludes `.env` and local db artifacts.

## Hardening changes applied locally
- Fixed env var typo and made Tavily connector safer.
- Replaced recursive retry with bounded retry loop.
- Added risk caps for per-trade sizing (`MIN/MAX_PORTFOLIO_FRACTION_PER_TRADE`).
- Fixed scheduler architecture.
- Removed private key print from test helper.

## Win potential estimate
- In current baseline architecture (pre-hardening): **low** for sustained alpha.
- As a research assistant / candidate idea generator: **moderate utility**.
- For live deployment, requires:
  - strict risk engine,
  - backtesting + forward-paper validation,
  - slippage/liquidity guards,
  - model calibration metrics (Brier/log loss),
  - circuit breakers.

### Practical expectation
- Without upgrades: likely noisy/flat or negative net after fees.
- With disciplined risk + validation: potential incremental edge in specific niches, but not guaranteed.
