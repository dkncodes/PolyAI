#!/usr/bin/env python3
import ast

from agents.polymarket.polymarket import Polymarket
from agents.notifications.state import open_trades, settle_trade


def infer_result_from_market(trade, market):
    """
    Infer WIN/LOSE from resolved market outcome prices.
    Heuristic: if market inactive and chosen token's outcome price >= 0.5 => WIN else LOSE.
    """
    if market.get("active", True):
        return None

    token_id = trade.get("token_id")
    try:
        token_ids = ast.literal_eval(market.get("clob_token_ids", "[]"))
        prices = ast.literal_eval(market.get("outcome_prices", "[]"))
        if token_id in token_ids and len(token_ids) == len(prices):
            idx = token_ids.index(token_id)
            p = float(prices[idx])
            return "WIN" if p >= 0.5 else "LOSE"
    except Exception:
        return None
    return None


def run_once():
    poly = Polymarket()
    notifier = poly.notifier
    trades = open_trades()

    for t in trades:
        token_id = t.get("token_id")
        if not token_id:
            continue
        try:
            market = poly.get_market(token_id)
            result = infer_result_from_market(t, market)
            if result:
                changed = settle_trade(t.get("id"), result)
                if changed:
                    notifier.send(notifier.fmt_trade_result(t.get("market_question", "Unknown Market"), result))
        except Exception:
            continue


if __name__ == "__main__":
    run_once()
