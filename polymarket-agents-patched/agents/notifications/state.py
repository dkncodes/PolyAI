import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

STATE_PATH = os.getenv("POLYAI_STATE_PATH", "data/trade_journal.json")


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def load_state(path: str = STATE_PATH) -> Dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {"trades": []}


def save_state(state: Dict, path: str = STATE_PATH) -> None:
    _ensure_parent(path)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def add_trade(trade: Dict, path: str = STATE_PATH) -> None:
    state = load_state(path)
    state.setdefault("trades", [])
    trade.setdefault("created_at", datetime.utcnow().isoformat() + "Z")
    trade.setdefault("status", "OPEN")
    state["trades"].append(trade)
    save_state(state, path)


def open_trades(path: str = STATE_PATH) -> List[Dict]:
    return [t for t in load_state(path).get("trades", []) if t.get("status") == "OPEN"]


def settle_trade(trade_id: str, result: str, path: str = STATE_PATH) -> bool:
    state = load_state(path)
    changed = False
    for t in state.get("trades", []):
        if t.get("id") == trade_id and t.get("status") == "OPEN":
            t["status"] = "SETTLED"
            t["result"] = result.upper()
            t["settled_at"] = datetime.utcnow().isoformat() + "Z"
            changed = True
    if changed:
        save_state(state, path)
    return changed


def all_trades(path: str = STATE_PATH) -> List[Dict]:
    return load_state(path).get("trades", [])


def settled_trades(path: str = STATE_PATH) -> List[Dict]:
    return [t for t in all_trades(path) if t.get("status") == "SETTLED"]


def recent_trades(limit: int = 5, path: str = STATE_PATH) -> List[Dict]:
    trades = sorted(all_trades(path), key=lambda t: t.get("created_at", ""), reverse=True)
    return trades[:limit]


def pnl_summary(path: str = STATE_PATH) -> Tuple[float, int, int]:
    """
    Returns (estimated_pnl_usd, wins, losses) based on settled trade outcomes.
    Assumes stake-sized PnL proxy: WIN => +amount_usdc, LOSE => -amount_usdc.
    """
    pnl = 0.0
    wins = 0
    losses = 0
    for t in settled_trades(path):
        amt = float(t.get("amount_usdc", 0.0) or 0.0)
        res = (t.get("result") or "").upper()
        if res == "WIN":
            pnl += amt
            wins += 1
        elif res == "LOSE":
            pnl -= amt
            losses += 1
    return pnl, wins, losses
