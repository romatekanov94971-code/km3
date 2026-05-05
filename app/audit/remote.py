from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from app.server.config import get_settings


def send_audit_event_remote(event: dict[str, Any]) -> bool:
    """Опциональная отправка события аудита на удаленный сервер сбора.

    Включается переменной окружения ENERGY_AUDIT_REMOTE_URL.
    Ошибка удаленной отправки не должна ломать основной бизнес-сценарий.
    """
    settings = get_settings()
    if not settings.audit_remote_url:
        return False

    body = json.dumps(event, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        settings.audit_remote_url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.audit_remote_timeout_seconds) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
