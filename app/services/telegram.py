import logging
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import telegram_client
from app.repositories.user import user_repository

logger = logging.getLogger("uvicorn.error")

async def handle_webhook(
    chat_id: str,
    text: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession
) -> dict:
    """
    Xử lý tin nhắn webhook từ Telegram, kiểm tra bảo mật và định tuyến các câu lệnh.
    """
    # Chỉ xử lý các câu lệnh bắt đầu bằng dấu gạch chéo '/'
    if not text.startswith("/"):
        return {"status": "ignored"}

    # Kiểm tra bảo mật Chat ID trước khi thực thi bất kỳ lệnh admin nào
    if chat_id != telegram_client.default_chat_id:
        logger.warning(f"[Telegram Service] Unauthorized access attempt from Chat ID: {chat_id}")
        # Gửi cảnh báo bảo mật về Chat ID admin cấu hình
        telegram_client.send_message(
            body=f"⚠️ Security Warning: Unauthorized user tried to execute '{text}' from Chat ID: {chat_id}",
            chat_id=telegram_client.default_chat_id
        )
        return {"status": "unauthorized"}

    # Định tuyến xử lý câu lệnh
    match text:
        case "/getlog":
            logger.info(f"[Telegram Service] Executing /getlog for Chat ID: {chat_id}")
            background_tasks.add_task(
                telegram_client.send_document,
                file_path="logs/app.log",
                caption="Here is the requested logs/app.log file.",
                chat_id=chat_id
            )
            return {"status": "ok"}

        case "/getusers":
            logger.info(f"[Telegram Service] Executing /getusers for Chat ID: {chat_id}")
            await _send_users_list(chat_id, db)
            return {"status": "ok"}

        case _:
            telegram_client.send_message(
                body=f"Unknown command: '{text}'. Supported commands:\n• /getlog - Get system log file\n• /getusers - List database users",
                chat_id=chat_id
            )
            return {"status": "unknown_command"}

async def _send_users_list(chat_id: str, db: AsyncSession):
    """
    Lấy danh sách users từ DB và gửi qua Telegram.
    """
    try:
        # Truy cập repository lấy danh sách người dùng
        users, _, _, _ = await user_repository.get_list(
            db,
            search_columns=["username"],
            limit=50
        )

        if users:
            user_lines = [f"• ID: `{u.id}` — Username: *{u.username}*" for u in users]
            message = "👥 *Current User List:*\n" + "\n".join(user_lines)
        else:
            message = "👥 *Current User List:* No users found."

        telegram_client.send_message(body=message, chat_id=chat_id)
    except Exception as e:
        logger.error(f"[Telegram Service] Error fetching users for command: {e}")
        telegram_client.send_message(body="❌ Error retrieving user list.", chat_id=chat_id)
