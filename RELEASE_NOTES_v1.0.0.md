# PolyAI v1.0.0 — Fully Patched Release

This release publishes a fully patched source snapshot of `Polymarket/agents` with safety and reliability hardening.

## Included
- `polymarket-agents-patched/` (full patched source)
- `polymarket_agents_hardening.patch`
- `AUDIT_SUMMARY.md`

## Hardening applied
1. Removed private key print path
2. Replaced recursive retry with bounded retry logic
3. Added trade size risk caps via env-configurable bounds
4. Fixed scheduler architecture bug
5. Corrected OPENAI env var mismatch in search connector

## New env knobs
- `MAX_PORTFOLIO_FRACTION_PER_TRADE` (default `0.02`)
- `MIN_PORTFOLIO_FRACTION_PER_TRADE` (default `0.001`)

## Notes
This improves operational safety, but does **not** guarantee profitability.
Use paper-trade/low-risk rollout before live trading.
