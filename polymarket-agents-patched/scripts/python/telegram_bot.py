#!/usr/bin/env python3
import os
import time
import requests

from agents.polymarket.polymarket import Polymarket

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send(text: str):
    if not (BOT_TOKEN and CHAT_ID):
        return
    requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": text}, timeout=20)


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
        lines.append(f"- ${amt:,.2f} | {q}")
    lines.append(f"Total tracked exposure: ${total:,.2f}")
    return "\n".join(lines)


def handle_command(cmd: str, polymarket: Polymarket):
    cmd = (cmd or "").strip().lower()
    if cmd in ["/start", "/help"]:
        send("PolyAI bot commands:\n/balance - wallet USDC + open position summary\n/positions - open tracked trades\n/help")
        return

    if cmd == "/balance":
        bal = polymarket.get_usdc_balance()
        pos = polymarket.get_open_positions()
        exposure = sum(float(t.get("amount_usdc", 0.0)) for t in pos)
        send(
            f"USDC balance: ${bal:,.2f}\n"
            f"Open positions: {len(pos)}\n"
            f"Tracked exposure: ${exposure:,.2f}"
        )
        return

    if cmd == "/positions":
        send(format_positions(polymarket))
        return


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
