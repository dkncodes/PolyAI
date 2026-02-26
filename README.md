# PolyAI — Polymarket Agents Hardening Patch Bundle

This repository contains a clean patch bundle for `github.com/Polymarket/agents` based on a security/reliability audit.

## Included
- `polymarket_agents_hardening.patch` — unified diff patch for key hardening fixes
- `AUDIT_SUMMARY.md` — concise findings, risk notes, and win-potential estimate

## Patched Areas
- Secret hygiene (remove private key print)
- Retry safety (remove infinite recursion)
- Risk controls (trade-size clamp caps)
- Scheduler stability fix
- Env var correctness for OpenAI key

## Apply Patch
```bash
git clone https://github.com/Polymarket/agents
cd agents
git apply /path/to/polymarket_agents_hardening.patch
```

## Notes
This bundle is intended as a starting point. For live trading, add full backtesting, slippage/liquidity controls, and strict drawdown limits.
