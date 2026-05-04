from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "Energy Equipment Efficiency System"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    db_path: str = "data/energy_system.sqlite3"
    audit_log_file: str = "logs/audit.log"
    audit_log_max_bytes: int = 1_000_000
    audit_log_backup_count: int = 5
    audit_retention_days: int = 180
    rate_limit_per_minute: int = 120


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        api_host=os.getenv("ENERGY_API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("ENERGY_API_PORT", "8000")),
        db_path=os.getenv("ENERGY_DB_PATH", "data/energy_system.sqlite3"),
        audit_log_file=os.getenv("ENERGY_AUDIT_LOG", "logs/audit.log"),
        audit_log_max_bytes=int(os.getenv("ENERGY_AUDIT_MAX_BYTES", "1000000")),
        audit_log_backup_count=int(os.getenv("ENERGY_AUDIT_BACKUPS", "5")),
        audit_retention_days=int(os.getenv("ENERGY_AUDIT_RETENTION_DAYS", "180")),
        rate_limit_per_minute=int(os.getenv("ENERGY_RATE_LIMIT_PER_MINUTE", "120")),
    )


def ensure_runtime_dirs() -> None:
    settings = get_settings()
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.audit_log_file).parent.mkdir(parents=True, exist_ok=True)
