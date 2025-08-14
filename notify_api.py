
from fastapi import APIRouter, Request, Header, HTTPException
from storage import get_users
from bot import bot
import datetime

router = APIRouter()

AUTH_SECRET = "proton-secret-token"  # секрет должен храниться в env в боевом

@router.post("/notify")
async def notify(request: Request, authorization: str = Header(None)):
    if authorization != f"Bearer {AUTH_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()

    # логирование
    with open("log.txt", "a") as log:
        log.write(f"{datetime.datetime.now().isoformat()} | {data}\n")

    message = f"Новая заявка: *{data['type']}* — *{data['location']}* — *{data['date']}*."
    message += f"\n[Перейти к заявке]({data['url']})"

    for user_id in get_users():
        try:
            await bot.send_message(user_id, message)
        except Exception:
            continue

    return {"status": "ok"}
