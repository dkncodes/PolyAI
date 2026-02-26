# PolyAI v1.2.0 — PolyGun-style Telegram Ops Upgrade

## Telegram UX Upgrade
- Added richer command set:
  - `/status`
  - `/balance`
  - `/positions`
  - `/recent`
  - `/pnl`
  - `/help`
- Added inline dashboard buttons for quick refresh and navigation.

## Trade / Portfolio Notifications
- Trade execution sends Telegram alert:
  - market, token, dollar size, timestamp
- Position monitor sends WIN/LOSE alerts when trades are settled.

## Journal + Analytics
- Extended local trade journal utilities:
  - recent trades
  - settled trades
  - estimated PnL summary
- Added exposure and settled performance summaries in bot responses.

## Bug Fixes / Hardening
- Fixed event parser bug in `gamma.py` (`parse_event` -> `parse_pydantic_event`).
- Compiled and syntax-checked all upgraded modules.

## Notes
- PnL currently uses a stake-based proxy for settled WIN/LOSE records.
- For production-grade accounting, integrate fill prices + fees + realized settlement values.
