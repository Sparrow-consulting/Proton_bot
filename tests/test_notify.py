import os
import sys
from pathlib import Path
import types
import importlib

# Добавляем корень репозитория в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Безопасные ENV для запуска приложения в тесте:
# токен валидного формата (НЕ боевой), чтобы aiogram не падал на валидации
os.environ["BOT_TOKEN"] = "123456:TEST"
os.environ.setdefault("LARAVEL_API_BASE", "https://example.invalid")

def _safe_monkeypatch():
    """Глушим внешние вызовы, чтобы тест не ходил в сеть/Telegram."""
    # 1) requests
    try:
        import requests  # type: ignore
        def _noop(self, method, url, *a, **kw):  # pragma: no cover
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{}'
            resp.url = url
            return resp
        requests.Session.request = _noop  # type: ignore
    except Exception:
        pass

    # 2) aiogram Bot.send_message
    try:
        from aiogram import Bot  # type: ignore
        async def _fake_send_message(self, chat_id, text, *a, **kw):  # pragma: no cover
            return types.SimpleNamespace(message_id=1)
        Bot.send_message = _fake_send_message  # type: ignore
    except Exception:
        pass

    # 3) функции в notify_api (если есть)
    try:
        notify_api = importlib.import_module("notify_api")
        for name in ("send_notification", "send_message", "notify", "send_telegram_message"):
            if hasattr(notify_api, name) and callable(getattr(notify_api, name)):
                async def _noop_async(*a, **kw):  # pragma: no cover
                    return {"status": "ok"}
                setattr(notify_api, name, _noop_async)
    except Exception:
        pass


def test_notify_ok():
    _safe_monkeypatch()

    import main  # в main должен быть app = FastAPI(...)
    from fastapi.testclient import TestClient

    assert hasattr(main, "app"), "В main.py должен быть объект app (FastAPI)"
    client = TestClient(main.app)

    payload = {"telegram_id": 123456789, "text": "CI smoke", "url": "https://example.com"}
    r = client.post("/notify", json=payload)
    assert r.status_code // 100 == 2, r.text
    assert r.headers.get("content-type", "").startswith("application/json")
