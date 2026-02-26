# PolyAI — Patched Polymarket Agents + Telegram Ops

PolyAI provides a hardened release of `github.com/Polymarket/agents` plus Telegram updates/commands for live ops.

## Repository Structure
- `polymarket-agents-patched/` — full patched source snapshot
- `polymarket_agents_hardening.patch` — patch-only bundle
- `AUDIT_SUMMARY.md` — security/reliability audit summary
- `RELEASE_NOTES_v1.0.0.md` — initial release notes

## What’s Added in PolyAI Upgrade
- Trade execution notifications to Telegram
- `/balance` and `/positions` command handling via Telegram bot
- Position monitor for win/lose notifications when markets resolve
- Local trade journal for tracked positions (`data/trade_journal.json`)

## Quick Start
```bash
git clone https://github.com/dkncodes/PolyAI.git
cd PolyAI/polymarket-agents-patched
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with at least:
- `POLYGON_WALLET_PRIVATE_KEY`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Run Components
### 1) Trading bot
```bash
python scripts/python/cli.py run_autonomous_trader
```

### 2) Telegram command bot
```bash
python scripts/python/telegram_bot.py
```
Commands:
- `/balance`
- `/positions`
- `/help`

### 3) Position result monitor (win/lose updates)
```bash
python scripts/python/position_monitor.py
```

## Notes
- Use paper-trade / low-risk rollout first.
- No strategy guarantees profit.
- Keep private keys and bot tokens in `.env` only.
