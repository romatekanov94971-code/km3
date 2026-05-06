from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError

from app.audit.event_models import AuditEvent
from app.audit.logger import audit_event
from app.auth.password_policy import validate_password
from app.common.exceptions import ValidationError
from app.common.schemas import UserRole
from app.server.api import app
from app.server.config import get_settings
from app.server.schemas import CalculationRequest
from app.storage.database import init_db


def test_password_special_characters_are_whitelisted():
    validate_password("operator", "GoodPass1!", UserRole.USER)
    with pytest.raises(ValidationError):
        validate_password("operator", "GoodPass1🙂", UserRole.USER)
    with pytest.raises(ValidationError):
        validate_password("operator", "Good Pass1!", UserRole.USER)


def test_temperature_is_validated_at_api_schema_boundary():
    with pytest.raises(PydanticValidationError):
        CalculationRequest(
            total_load=100,
            num_blocks=1,
            nominal_power_per_block=200,
            nominal_efficiency=0.38,
            temp_c=100,
            humidity=50,
            wind_speed=2,
            wind_dir=90,
        )


def test_audit_file_contains_sequence_number(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "audit.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    get_settings.cache_clear()
    init_db()

    event_id = audit_event("unit_test_event", "tests", "test", subject="tester")
    lines = (tmp_path / "audit.log").read_text(encoding="utf-8").splitlines()
    assert lines
    data = json.loads(lines[-1])
    assert data["event_id"] == event_id
    assert isinstance(data["sequence_number"], int)


def test_remote_audit_is_queued_not_sent_synchronously():
    source = Path("app/audit/logger.py").read_text(encoding="utf-8")
    assert "enqueue_audit_event_remote" in source
    assert "send_audit_event_remote(data)" not in source
    remote_source = Path("app/audit/remote.py").read_text(encoding="utf-8")
    assert "queue.Queue" in remote_source
    assert "threading.Thread" in remote_source


def test_database_uses_wal_mode():
    source = Path("app/storage/database.py").read_text(encoding="utf-8")
    assert "PRAGMA journal_mode = WAL" in source
    assert "PRAGMA busy_timeout" in source


def test_api_client_is_split_into_narrow_clients_and_logout_exists():
    source = Path("app/client/api_client.py").read_text(encoding="utf-8")
    assert "class AuthApiClient" in source
    assert "class CalcApiClient" in source
    assert "class AuditApiClient" in source
    assert "class ExportApiClient" in source
    assert "def logout" in source


def test_main_window_close_event_calls_logout():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert "def closeEvent" in source
    assert "self.api.logout()" in source


def test_roles_use_enum():
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.USER.value == "user"
    source = Path("app/common/schemas.py").read_text(encoding="utf-8")
    assert "class UserRole" in source
