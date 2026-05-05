from __future__ import annotations

import json
import logging
import secrets
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from app.audit.event_models import AuditEvent
from app.common.utils import safe_headers
from app.server.config import get_settings

_LOGGER: logging.Logger | None = None


def get_audit_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER
    settings = get_settings()
    log_path = Path(settings.audit_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("energy_system.audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=settings.audit_log_max_bytes,
            backupCount=settings.audit_log_backup_count,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    _LOGGER = logger
    return logger


def audit_event(
    event_name: str,
    component: str,
    event_type: str,
    subject: str | None = None,
    headers: dict[str, Any] | None = None,
    details: dict[str, Any] | None = None,
    event_id: str | None = None,
) -> str:
    """Регистрирует событие в файле и, если БД инициализирована, в SQLite."""
    from app.common.utils import utcnow_iso
    from app.storage.repositories import AuditRepository

    event_id = event_id or secrets.token_hex(8)
    event_time = utcnow_iso()
    settings = get_settings()
    detail_level = settings.audit_detail_level if settings.audit_detail_level in {"basic", "standard", "full"} else "standard"
    safe = safe_headers(headers)

    # Настраиваемая детализация журнала:
    # basic    - только обязательные поля события;
    # standard - обязательные поля + безопасные заголовки + details;
    # full     - то же, что standard; тела запросов и пароли намеренно не пишутся.
    stored_headers = {} if detail_level == "basic" else safe
    stored_details = {} if detail_level == "basic" else (details or {})

    event = AuditEvent(
        event_name=event_name,
        component=component,
        event_type=event_type,
        event_id=event_id,
        event_time=event_time,
        subject=subject,
        headers=stored_headers,
        details=stored_details,
        detail_level=detail_level,
    )
    data = event.to_dict()

    try:
        from app.audit.remote import send_audit_event_remote

        remote_sent = send_audit_event_remote(data)
    except Exception:
        remote_sent = False

    event = AuditEvent(
        event_name=event.event_name,
        component=event.component,
        event_type=event.event_type,
        event_id=event.event_id,
        event_time=event.event_time,
        subject=event.subject,
        headers=event.headers,
        details=event.details,
        detail_level=event.detail_level,
        remote_sent=remote_sent,
    )
    data = event.to_dict()

    get_audit_logger().info(json.dumps(data, ensure_ascii=False))
    try:
        AuditRepository().create(
            event_name=event.event_name,
            component=event.component,
            event_type=event.event_type,
            event_id=event.event_id,
            subject=event.subject,
            headers=event.headers,
            details=event.details,
            event_time=event.event_time,
        )
    except Exception:
        # В момент первичной инициализации БД таблицы могут еще отсутствовать.
        pass
    return event_id
