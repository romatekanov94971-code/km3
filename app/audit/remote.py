from __future__ import annotations

import json
import queue
import threading
import urllib.error
import urllib.request
from typing import Any

from app.server.config import get_settings

_REMOTE_QUEUE: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1000)
_WORKER_STARTED = False
_WORKER_LOCK = threading.Lock()


def send_audit_event_remote(event: dict[str, Any]) -> bool:
    """Синхронная отправка события на удаленный сервер сбора.

    Используется только внутри фонового worker-а. Основной request hot path
    вызывает enqueue_audit_event_remote() и не блокируется на сетевой timeout.
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


def _remote_worker() -> None:
    while True:
        event = _REMOTE_QUEUE.get()
        try:
            send_audit_event_remote(event)
        finally:
            _REMOTE_QUEUE.task_done()


def _ensure_worker_started() -> None:
    global _WORKER_STARTED
    if _WORKER_STARTED:
        return
    with _WORKER_LOCK:
        if _WORKER_STARTED:
            return
        thread = threading.Thread(target=_remote_worker, name="audit-remote-worker", daemon=True)
        thread.start()
        _WORKER_STARTED = True


def enqueue_audit_event_remote(event: dict[str, Any]) -> bool:
    """Ставит событие аудита в очередь удаленной отправки без блокировки API-запроса."""
    settings = get_settings()
    if not settings.audit_remote_url:
        return False

    _ensure_worker_started()
    try:
        _REMOTE_QUEUE.put_nowait(dict(event))
        return True
    except queue.Full:
        return False


__all__ = ["enqueue_audit_event_remote", "send_audit_event_remote"]
