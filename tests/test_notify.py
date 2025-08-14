import os
import types
import importlib

# Перед импортом приложения задаём "безопасные" переменные окружения
os.environ.setdefault("BOT_TOKEN", "dummy-token")
os.environ.setdefault("LARAVEL_API_BASE", "https://example.invalid")

def _safe_monkeypatch():
    """
    Пытаемся заглушить любые внешние вызовы, которые может делать код:
    - aiogram.Bot.send_message
    - requests.Session.request
    - любые функции в notify_api, похожие на отправку
    """
    # 1) Заглушка requests (если используется)
    try:
        import requests  # type: ignore
        orig_req = requests.Session.request
        def _noop(self, method, url, *a, **kw):  # pragma: no cover
            # возвращаем минимально валидный объект Response
            resp = requests.Response()
            resp.status_code = 200
            resp._content = b'{}'
            resp.url = url
            return resp
        requests.Session.request = _noop  # type: ignore
    except Exception:
        pass

    # 2) Заглушка aiogram Bot.send_message (если используется)
    try:
        import aiogram  # type: ignore
        from aiogram import Bot  # type: ignore
        async def _fake_send_message(self, chat_id, text, *a, **kw):  # pragma: no cover
            return types.SimpleNamespace(message_id=1)
        Bot.send_message = _fake_send_message  # type: ignore
    except Exception:
        pass

    # 3) Заглушки функций внутри notify_api (если есть)
    try:
        notify_api = importlib.import_module("notify_api")
        for name in ("send_notification", "send_message", "notify", "send_telegram_message"):
            if hasattr(notify_api, name):
                fn = getattr(notify_api, name)
                if callable(fn):
                    async def _noop_async(*a, **kw):  # pragma: no cover
                        return {"status": "ok"}
                    def _noop_sync(*a, **kw):  # pragma: no cover
                        return {"status": "ok"}
                    setattr(
                        notify_api,
                        name,
                        _noop_async if getattr(fn, "__code__", None) and "ASYNC_GENERATOR" in str(fn.__code__.co_flags) else _noop_sync
                    )
    except Exception:
        pass


def test_notify_ok():
    _safe_monkeypatch()
    # Импортируем приложение
    import main  # должен содержать app = FastAPI(...)
    from fastapi.testclient import TestClient

    assert hasattr(main, "app"), "В main.py должен быть объект app (FastAPI)"
    client = TestClient(main.app)

    payload = {"telegram_id": 123456789, "text": "CI smoke", "url": "https://example.com"}
    r = client.post("/notify", json=payload)
    # допускаем разные коды успеха, но чаще всего 200/201
    assert r.status_code // 100 == 2, r.text
    # допускаем разные формы ответа, главное — JSON
    assert r.headers.get("content-type", "").startswith("application/json")
