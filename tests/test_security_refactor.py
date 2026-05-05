from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.auth.service import AuthService
from app.server.api import app
from app.server.config import get_settings
from app.storage.database import init_db


def test_default_admin_password_is_generated_not_hardcoded(tmp_path, monkeypatch):
    credentials_file = tmp_path / "initial_admin_credentials.txt"
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    monkeypatch.setenv("ENERGY_INITIAL_ADMIN_CREDENTIALS_FILE", str(credentials_file))
    monkeypatch.delenv("ENERGY_DEFAULT_ADMIN_PASSWORD", raising=False)
    get_settings.cache_clear()

    init_db()
    AuthService().ensure_default_admin()

    content = credentials_file.read_text(encoding="utf-8")
    assert "username=admin" in content
    assert "password=" in content
    assert ("Admin" + "123!") not in content

    password = [line.split("=", 1)[1] for line in content.splitlines() if line.startswith("password=")][0]
    login = AuthService().login("admin", password)
    assert login.user.username == "admin"
    assert login.must_change_password is True


def test_login_window_does_not_prefill_password():
    source = Path("app/client/login_window.py").read_text(encoding="utf-8")
    assert 'QLineEdit("' + "Admin" + '123!")' not in source
    assert ("Admin" + "123!") not in source


def test_auth_routes_use_dependency_injection_not_global_singleton():
    service_source = Path("app/auth/service.py").read_text(encoding="utf-8")
    route_source = Path("app/server/routes/auth.py").read_text(encoding="utf-8")
    assert ("auth_" + "service = AuthService()") not in service_source
    assert "from app.auth.service import auth_service" not in route_source
    assert "Depends(get_auth_service)" in route_source


def test_admin_login_with_env_configured_password(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    monkeypatch.setenv("ENERGY_DEFAULT_ADMIN_PASSWORD", "RootEnv1!")
    get_settings.cache_clear()
    init_db()

    AuthService().ensure_default_admin()
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": "admin", "password": "RootEnv1!"})
    assert response.status_code == 200, response.text
