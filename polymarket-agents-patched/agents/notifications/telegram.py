import os
import requests
from datetime import datetime


class TelegramNotifier:
    def __init__(self) -> None:
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send(self, message: str) -> bool:
        if not self.enabled():
            return False
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": True,
        }
        try:
            resp = requests.post(url, json=payload, timeout=20)
            return resp.status_code == 200
        except Exception:
            return False

    def fmt_trade_taken(self, market_question: str, token_id: str, amount_usdc: float) -> str:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        return (
            f"✅ Trade taken\n"
            f"• Market: {market_question}\n"
            f"• Token: {token_id}\n"
            f"• Size: ${amount_usdc:,.2f}\n"
            f"• Time: {ts}"
        )

    def fmt_trade_result(self, market_question: str, result: str) -> str:
        emoji = "🏆" if result.upper() == "WIN" else "⚠️"
        return f"{emoji} Trade {result.upper()}\n• Market: {market_question}"
