#!/usr/bin/env python3
import os
import time
import requests

from agents.polymarket.polymarket import Polymarket
from agents.notifications.state import recent_trades, pnl_summary, open_trades

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send(text: str, reply_markup=None):
    if not (BOT_TOKEN and CHAT_ID):
        return
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{API}/sendMessage", json=payload, timeout=20)


def answer_callback(callback_id: str):
    if not callback_id:
        return
    try:
        requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": callback_id}, timeout=10)
    except Exception:
        pass


def format_positions(polymarket: Polymarket) -> str:
    trades = polymarket.get_open_positions()
    if not trades:
        return "No open positions in local trade journal."

    lines = [f"Open positions: {len(trades)}"]
    total = 0.0
    for t in trades[:10]:
        amt = float(t.get("amount_usdc", 0.0))
        total += amt
        q = t.get("market_question", "Unknown")
        tid = (t.get("id") or "")[:8]
        lines.append(f"- [{tid}] ${amt:,.2f} | {q}")
    lines.append(f"Total tracked exposure: ${total:,.2f}")
    return "\n".join(lines)


def format_recent(limit: int = 5) -> str:
    rows = recent_trades(limit=limit)
    if not rows:
        return "No trades in journal yet."
    lines = [f"Recent trades ({len(rows)}):"]
    for t in rows:
        status = t.get("status", "?")
        res = t.get("result", "-")
        amt = float(t.get("amount_usdc", 0.0) or 0.0)
        q = t.get("market_question", "Unknown")
        tid = (t.get("id") or "")[:8]
        lines.append(f"- [{tid}] {status}/{res} | ${amt:,.2f} | {q}")
    return "\n".join(lines)


def format_pnl() -> str:
    pnl, wins, losses = pnl_summary()
    total = wins + losses
    winrate = (wins / total * 100.0) if total else 0.0
    sign = "+" if pnl >= 0 else ""
    return (
        f"Estimated settled PnL: {sign}${pnl:,.2f}\n"
        f"Wins: {wins} | Losses: {losses} | Win rate: {winrate:.1f}%"
    )


def status_text(polymarket: Polymarket) -> str:
    bal = polymarket.get_usdc_balance()
    open_pos = open_trades()
    exposure = sum(float(t.get("amount_usdc", 0.0)) for t in open_pos)
    pnl, wins, losses = pnl_summary()
    sign = "+" if pnl >= 0 else ""
    return (
        "PolyAI Status\n"
        f"• USDC balance: ${bal:,.2f}\n"
        f"• Open positions: {len(open_pos)}\n"
        f"• Tracked exposure: ${exposure:,.2f}\n"
        f"• Settled PnL: {sign}${pnl:,.2f} (W:{wins}/L:{losses})"
    )


def dashboard_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "Refresh Status", "callback_data": "status"},
                {"text": "Balance", "callback_data": "balance"},
            ],
            [
                {"text": "Open Positions", "callback_data": "positions"},
                {"text": "Recent", "callback_data": "recent"},
            ],
            [
                {"text": "PnL", "callback_data": "pnl"}
            ],
        ]
    }


def handle_command(cmd: str, polymarket: Polymarket):
    cmd = (cmd or "").strip().lower()

    if cmd in ["/start", "/help"]:
        send(
            "PolyAI commands:\n"
            "/status - portfolio snapshot\n"
            "/balance - wallet USDC + exposure\n"
            "/positions - open tracked trades\n"
            "/recent - last 5 trades\n"
            "/pnl - settled PnL summary\n"
            "/help",
            reply_markup=dashboard_buttons(),
        )
        return

    if cmd == "/status":
        send(status_text(polymarket), reply_markup=dashboard_buttons())
        return

    if cmd == "/balance":
        bal = polymarket.get_usdc_balance()
        pos = polymarket.get_open_positions()
        exposure = sum(float(t.get("amount_usdc", 0.0)) for t in pos)
        send(
            f"USDC balance: ${bal:,.2f}\n"
            f"Open positions: {len(pos)}\n"
            f"Tracked exposure: ${exposure:,.2f}",
            reply_markup=dashboard_buttons(),
        )
        return

    if cmd == "/positions":
        send(format_positions(polymarket), reply_markup=dashboard_buttons())
        return

    if cmd == "/recent":
        send(format_recent(), reply_markup=dashboard_buttons())
        return

    if cmd == "/pnl":
        send(format_pnl(), reply_markup=dashboard_buttons())
        return


def handle_callback(data: str, callback_id: str, polymarket: Polymarket):
    action = (data or "").strip().lower()
    answer_callback(callback_id)

    if action == "status":
        send(status_text(polymarket), reply_markup=dashboard_buttons())
    elif action == "balance":
        handle_command("/balance", polymarket)
    elif action == "positions":
        handle_command("/positions", polymarket)
    elif action == "recent":
        handle_command("/recent", polymarket)
    elif action == "pnl":
        handle_command("/pnl", polymarket)


def run():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    polymarket = Polymarket()
    offset = None
    while True:
        try:
            payload = {"timeout": 30}
            if offset is not None:
                payload["offset"] = offset
            r = requests.get(f"{API}/getUpdates", params=payload, timeout=40)
            data = r.json()
            if not data.get("ok"):
                time.sleep(2)
                continue

            for upd in data.get("result", []):
                offset = upd["update_id"] + 1

                # callback buttons
                if "callback_query" in upd:
                    cq = upd.get("callback_query", {})
                    callback_id = cq.get("id")
                    cb_data = cq.get("data", "")
                    chat_id = str(cq.get("message", {}).get("chat", {}).get("id", ""))
                    if CHAT_ID and chat_id != CHAT_ID:
                        continue
                    handle_callback(cb_data, callback_id, polymarket)
                    continue

                msg = upd.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))

                # Restrict responses to configured chat if set
                if CHAT_ID and chat_id != CHAT_ID:
                    continue

                if text.startswith("/"):
                    handle_command(text, polymarket)
        except Exception:
            time.sleep(2)


if __name__ == "__main__":
    run()
