from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.common.utils import utcnow_iso


@dataclass(frozen=True)
class AuditEvent:
    event_name: str
    component: str
    event_type: str
    event_id: str
    event_time: str = field(default_factory=utcnow_iso)
    subject: str | None = None
    headers: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
