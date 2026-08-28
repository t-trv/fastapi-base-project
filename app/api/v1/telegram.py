from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.services import telegram as telegram_service

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook tiếp nhận các sự kiện cập nhật từ Telegram Bot.
    """
    try:
        data = await request.json()
    except Exception:
        return {"status": "bad request"}

    message = data.get("message")
    if not message:
        return {"status": "ok"}

    chat = message.get("chat", {})
    chat_id = str(chat.get("id"))
    text = message.get("text", "").strip()

    # Ủy thác xử lý logic nghiệp vụ cho Telegram Service
    result = await telegram_service.handle_webhook(
        chat_id=chat_id,
        text=text,
        background_tasks=background_tasks,
        db=db
    )

    return result
