from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    """Текущее время UTC без зависимости от локальной машины."""
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat()


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def safe_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    """Удаляет из заголовков потенциально чувствительные значения."""
    if not headers:
        return {}
    hidden = {"authorization", "cookie", "set-cookie", "x-session-token"}
    result: dict[str, str] = {}
    for key, value in headers.items():
        lowered = str(key).lower()
        result[str(key)] = "***" if lowered in hidden else str(value)
    return result


__all__ = ['parse_iso_datetime', 'safe_headers', 'utcnow', 'utcnow_iso']
