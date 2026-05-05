import os
from pathlib import Path

import pytest

from app.auth.password_policy import validate_password
from app.auth.service import AuthService
from app.common.exceptions import AuthenticationError, ValidationError
from app.server.config import get_settings
from app.storage.database import init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    get_settings.cache_clear()
    init_db()
    yield
    get_settings.cache_clear()


def test_password_policy_accepts_valid_password():
    validate_password("ivan", "Qwerty1!", "user")


def test_password_policy_rejects_weak_password():
    with pytest.raises(ValidationError):
        validate_password("ivan", "qwerty", "user")


def test_login_and_change_password():
    service = AuthService()
    service.create_user("ivan", "Qwerty1!", role="user")
    login = service.login("ivan", "Qwerty1!")
    assert login.user.username == "ivan"
    service.change_password(login.user, "Qwerty1!", "Newpass1!")
    login2 = service.login("ivan", "Newpass1!")
    assert login2.user.username == "ivan"


def test_failed_attempts_lock_account():
    service = AuthService()
    service.create_user("petr", "Qwerty1!", role="user")
    for _ in range(3):
        with pytest.raises(AuthenticationError):
            service.login("petr", "bad")
    with pytest.raises(AuthenticationError):
        service.login("petr", "Qwerty1!")


def test_authentication_parameters_are_configurable(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "configurable.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "configurable_audit.log"))
    monkeypatch.setenv("ENERGY_AUTH_MAX_FAILED_ATTEMPTS", "2")
    monkeypatch.setenv("ENERGY_AUTH_LOCK_MINUTES", "15")
    monkeypatch.setenv("ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH", "8")
    get_settings.cache_clear()
    init_db()

    with pytest.raises(ValidationError):
        validate_password("shortuser", "Qwe1!a", "user")

    service = AuthService()
    service.create_user("lockuser", "Longpass1!", role="user")

    for _ in range(2):
        with pytest.raises(AuthenticationError):
            service.login("lockuser", "bad")

    with pytest.raises(AuthenticationError):
        service.login("lockuser", "Longpass1!")
