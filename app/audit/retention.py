from __future__ import annotations

from datetime import timedelta

from app.common.utils import utcnow
from app.server.config import get_settings
from app.storage.repositories import AuditRepository


def cleanup_old_audit_events(retention_days: int | None = None) -> int:
    """Удаляет события аудита старше заданной глубины хранения."""
    days = retention_days if retention_days is not None else get_settings().audit_retention_days
    cutoff = (utcnow() - timedelta(days=days)).isoformat()
    return AuditRepository().delete_older_than(cutoff)
