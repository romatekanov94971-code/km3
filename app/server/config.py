from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    return value if value else None


@dataclass(frozen=True)
class Settings:
    app_name: str = "Energy Equipment Efficiency System"

    # API / integration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_ssl_certfile: str | None = None
    api_ssl_keyfile: str | None = None
    api_client_base_url: str = "http://127.0.0.1:8000"
    rate_limit_per_minute: int = 120

    # Storage
    db_path: str = "data/energy_system.sqlite3"

    # Initial administrator. Password is never hardcoded in UI/code:
    # set ENERGY_DEFAULT_ADMIN_PASSWORD or read generated credentials file after first API startup.
    default_admin_username: str = "admin"
    default_admin_password: str | None = None
    initial_admin_credentials_file: str = "data/initial_admin_credentials.txt"

    # Password authentication: configurable controls required by TZ 3.2
    auth_max_failed_attempts: int = 3
    auth_lock_minutes: int = 15
    auth_user_min_password_length: int = 6
    auth_admin_min_password_length: int = 7

    # Audit: configurable retention, detail level, rotation, remote collection
    audit_log_file: str = "logs/audit.log"
    audit_log_max_bytes: int = 1_000_000
    audit_log_backup_count: int = 5
    audit_retention_days: int = 180
    audit_detail_level: str = "standard"  # basic | standard | full
    audit_remote_url: str | None = None
    audit_remote_timeout_seconds: float = 3.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    api_host = os.getenv("ENERGY_API_HOST", "127.0.0.1")
    api_port = int(os.getenv("ENERGY_API_PORT", "8000"))
    ssl_cert = _optional_env("ENERGY_API_SSL_CERTFILE")
    ssl_key = _optional_env("ENERGY_API_SSL_KEYFILE")
    default_scheme = "https" if ssl_cert and ssl_key else "http"

    return Settings(
        api_host=api_host,
        api_port=api_port,
        api_ssl_certfile=ssl_cert,
        api_ssl_keyfile=ssl_key,
        api_client_base_url=os.getenv("ENERGY_API_BASE_URL", f"{default_scheme}://{api_host}:{api_port}"),
        rate_limit_per_minute=int(os.getenv("ENERGY_RATE_LIMIT_PER_MINUTE", "120")),
        db_path=os.getenv("ENERGY_DB_PATH", "data/energy_system.sqlite3"),
        default_admin_username=os.getenv("ENERGY_DEFAULT_ADMIN_USERNAME", "admin"),
        default_admin_password=_optional_env("ENERGY_DEFAULT_ADMIN_PASSWORD"),
        initial_admin_credentials_file=os.getenv(
            "ENERGY_INITIAL_ADMIN_CREDENTIALS_FILE",
            "data/initial_admin_credentials.txt",
        ),
        auth_max_failed_attempts=int(os.getenv("ENERGY_AUTH_MAX_FAILED_ATTEMPTS", "3")),
        auth_lock_minutes=int(os.getenv("ENERGY_AUTH_LOCK_MINUTES", "15")),
        auth_user_min_password_length=int(os.getenv("ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH", "6")),
        auth_admin_min_password_length=int(os.getenv("ENERGY_AUTH_ADMIN_MIN_PASSWORD_LENGTH", "7")),
        audit_log_file=os.getenv("ENERGY_AUDIT_LOG", "logs/audit.log"),
        audit_log_max_bytes=int(os.getenv("ENERGY_AUDIT_MAX_BYTES", "1000000")),
        audit_log_backup_count=int(os.getenv("ENERGY_AUDIT_BACKUPS", "5")),
        audit_retention_days=int(os.getenv("ENERGY_AUDIT_RETENTION_DAYS", "180")),
        audit_detail_level=os.getenv("ENERGY_AUDIT_DETAIL_LEVEL", "standard").lower(),
        audit_remote_url=_optional_env("ENERGY_AUDIT_REMOTE_URL"),
        audit_remote_timeout_seconds=float(os.getenv("ENERGY_AUDIT_REMOTE_TIMEOUT", "3.0")),
    )


def ensure_runtime_dirs() -> None:
    settings = get_settings()
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.audit_log_file).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.initial_admin_credentials_file).parent.mkdir(parents=True, exist_ok=True)


__all__ = ['Settings', 'ensure_runtime_dirs', 'get_settings']
