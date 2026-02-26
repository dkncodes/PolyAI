import json
import os
from datetime import datetime
from typing import Dict, List

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
