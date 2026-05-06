from __future__ import annotations

import json
import logging
import secrets
from dataclasses import replace
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Protocol

from app.audit.event_models import AuditEvent
from app.common.utils import safe_headers
from app.server.config import get_settings


class AuditSink(Protocol):
    """Канал обработки события аудита."""

    def write(self, event: AuditEvent) -> AuditEvent:
        ...


_AUDIT_SINK_REGISTRY: list[tuple[int, type[object]]] = []


def register_audit_sink(*, order: int) -> callable:
    """Регистрирует sink-класс аудита в общей цепочке обработки.

    Это снимает жесткую конфигурацию с `get_audit_sinks()`: для добавления нового
    канала достаточно объявить класс и пометить его декоратором
    `@register_audit_sink(order=...)`.
    """

    def decorator(cls: type[object]) -> type[object]:
        _AUDIT_SINK_REGISTRY.append((order, cls))
        _AUDIT_SINK_REGISTRY.sort(key=lambda item: item[0])
        return cls

    return decorator


@register_audit_sink(order=10)
class SQLiteAuditSink:
    """Сохраняет событие в SQLite и добавляет sequence_number."""

    def write(self, event: AuditEvent) -> AuditEvent:
        from app.storage.repositories import AuditRepository

        sequence_number: int | None = None
        try:
            sequence_number = AuditRepository().create(
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
        return replace(event, sequence_number=sequence_number)


@register_audit_sink(order=20)
class RemoteQueueAuditSink:
    """Ставит событие в неблокирующую очередь удаленной отправки."""

    def write(self, event: AuditEvent) -> AuditEvent:
        from app.audit.remote import enqueue_audit_event_remote

        remote_queued = enqueue_audit_event_remote(event.to_dict())
        return replace(event, remote_queued=remote_queued)


@register_audit_sink(order=30)
class FileAuditSink:
    """Пишет финальный AuditEvent в файловый журнал с ротацией."""

    def write(self, event: AuditEvent) -> AuditEvent:
        get_audit_logger().info(json.dumps(event.to_dict(), ensure_ascii=False))
        return event


def get_audit_logger() -> logging.Logger:
    """Возвращает именованный logger без отдельного глобального singleton."""
    settings = get_settings()
    log_path = Path(settings.audit_log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_log_path = str(log_path.resolve())

    logger = logging.getLogger("energy_system.audit")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    existing_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, RotatingFileHandler)
            and getattr(handler, "baseFilename", None) == resolved_log_path
        ),
        None,
    )
    if existing_handler is not None:
        return logger

    # Удаляем только handlers, созданные этим модулем ранее. Чужие handlers,
    # добавленные pytest, IDE или внешней системой логирования, не трогаем.
    for handler in list(logger.handlers):
        if getattr(handler, "_energy_system_audit_handler", False):
            logger.removeHandler(handler)
            handler.close()

    handler = RotatingFileHandler(
        log_path,
        maxBytes=settings.audit_log_max_bytes,
        backupCount=settings.audit_log_backup_count,
        encoding="utf-8",
    )
    handler._energy_system_audit_handler = True  # type: ignore[attr-defined]
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def get_audit_sinks() -> tuple[AuditSink, ...]:
    """Создает sink-объекты из реестра, а не из захардкоженного списка."""
    return tuple(cls() for _, cls in _AUDIT_SINK_REGISTRY)


def build_audit_event(
    event_name: str,
    component: str,
    event_type: str,
    subject: str | None = None,
    headers: dict[str, Any] | None = None,
    details: dict[str, Any] | None = None,
    event_id: str | None = None,
) -> AuditEvent:
    """Формирует AuditEvent без записи в sinks."""
    from app.common.utils import utcnow_iso

    settings = get_settings()
    detail_level = settings.audit_detail_level if settings.audit_detail_level in {"basic", "standard", "full"} else "standard"
    safe = safe_headers(headers)

    stored_headers = {} if detail_level == "basic" else safe
    stored_details = {} if detail_level == "basic" else (details or {})

    return AuditEvent(
        event_name=event_name,
        component=component,
        event_type=event_type,
        event_id=event_id or secrets.token_hex(8),
        event_time=utcnow_iso(),
        subject=subject,
        headers=stored_headers,
        details=stored_details,
        detail_level=detail_level,
    )


def audit_event(
    event_name: str,
    component: str,
    event_type: str,
    subject: str | None = None,
    headers: dict[str, Any] | None = None,
    details: dict[str, Any] | None = None,
    event_id: str | None = None,
) -> str:
    """Регистрирует событие аудита через цепочку sink-объектов."""
    event = build_audit_event(
        event_name=event_name,
        component=component,
        event_type=event_type,
        subject=subject,
        headers=headers,
        details=details,
        event_id=event_id,
    )
    for sink in get_audit_sinks():
        event = sink.write(event)
    return event.event_id


__all__ = [
    "AuditSink",
    "FileAuditSink",
    "RemoteQueueAuditSink",
    "SQLiteAuditSink",
    "audit_event",
    "build_audit_event",
    "get_audit_logger",
    "get_audit_sinks",
    "register_audit_sink",
]
