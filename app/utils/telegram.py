"""
app/utils/telegram.py
Gửi tin nhắn và file qua Telegram API sử dụng TelegramClient.

Usage:
    from app.utils.telegram import telegram_client

    telegram_client.send_message("Hello World")
    telegram_client.send_document("logs/app.log", caption="Error Traceback Log")
"""

import os
import requests
from app.config import settings

class TelegramClient:
    """
    Client tương tác với Telegram API.
    Hỗ trợ gửi tin nhắn và gửi tài liệu (logs).
    """
    def __init__(self, token: str | None = None, default_chat_id: str | None = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.default_chat_id = default_chat_id or settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        # Sử dụng requests.Session để tối ưu connection pooling (Keep-Alive)
        self.session = requests.Session()

    def _escape_md(self, text: str) -> str:
        """Escape các ký tự đặc biệt của Telegram Markdown v1."""
        return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")

    def _format_body(self, body: dict) -> str:
        """Chuyển đổi dict thành chuỗi định dạng Markdown 'Key: Value', mỗi cặp một dòng."""
        return "\n".join(f"*{k}:* {self._escape_md(str(v))}" for k, v in body.items())

    def send_message(
        self,
        body: dict | str,
        chat_id: str | None = None,
        parse_mode: str | None = "Markdown",
        silent: bool = False,
    ) -> dict | None:
        """
        Gửi tin nhắn dạng dict hoặc text tới Telegram.
        """
        target_chat_id = chat_id or self.default_chat_id
        text = self._format_body(body) if isinstance(body, dict) else body

        payload: dict = {
            "chat_id": target_chat_id,
            "text": text,
            "disable_notification": silent,
        }
        if parse_mode is not None:
            payload["parse_mode"] = parse_mode

        try:
            resp = self.session.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10,
            )
            if not resp.ok:
                print(f"[Telegram] send_message failed: {resp.status_code} — {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print(f"[Telegram] send_message error: {e}")
            return None

    def send_document(
        self,
        file_path: str,
        caption: str | None = None,
        chat_id: str | None = None,
    ) -> dict | None:
        """
        Gửi file tài liệu (document) lên Telegram.
        """
        target_chat_id = chat_id or self.default_chat_id
        if not os.path.exists(file_path):
            print(f"[Telegram] send_document failed: File '{file_path}' does not exist.")
            return None

        payload: dict = {
            "chat_id": target_chat_id,
        }
        if caption is not None:
            payload["caption"] = caption

        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                resp = self.session.post(
                    f"{self.base_url}/sendDocument",
                    data=payload,
                    files=files,
                    timeout=30,  # File lớn cần thời gian lâu hơn chút
                )
            if not resp.ok:
                print(f"[Telegram] send_document failed: {resp.status_code} — {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print(f"[Telegram] send_document error: {e}")
            return None

# Khởi tạo mặc định instance để sử dụng nhanh trong toàn dự án
telegram_client = TelegramClient()
