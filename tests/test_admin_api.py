import json

import pytest
from fastapi.testclient import TestClient

from app.auth.service import AuthService
from app.server.api import app
from app.server.config import get_settings
from app.storage.database import init_db


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit.log"))
    get_settings.cache_clear()
    init_db()
    AuthService().create_user("root", "Secure1!", role="admin", must_change_password=False)
    AuthService().create_user("operator", "Worker1!", role="user", must_change_password=False)
    yield
    get_settings.cache_clear()


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["token"]


def test_admin_can_create_user_and_view_audit():
    client = TestClient(app)
    admin_token = _login(client, "root", "Secure1!")

    create_response = client.post(
        "/auth/users",
        json={
            "username": "new_user",
            "password": "Newuser1!",
            "role": "user",
            "must_change_password": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_response.status_code == 200, create_response.text
    assert create_response.json()["username"] == "new_user"

    audit_response = client.get("/calc/audit", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_response.status_code == 200, audit_response.text
    event_names = {event["event_name"] for event in audit_response.json()}
    assert "user_created" in event_names


def test_regular_user_cannot_create_user_or_view_audit():
    client = TestClient(app)
    user_token = _login(client, "operator", "Worker1!")

    create_response = client.post(
        "/auth/users",
        json={
            "username": "bad",
            "password": "Baduser1!",
            "role": "user",
            "must_change_password": True,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert create_response.status_code == 403

    audit_response = client.get("/calc/audit", headers={"Authorization": f"Bearer {user_token}"})
    assert audit_response.status_code == 403


def test_audit_headers_are_sanitized():
    client = TestClient(app)
    admin_token = _login(client, "root", "Secure1!")

    response = client.get(
        "/calc/audit",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Cookie": "sessionid=secret-cookie",
        },
    )
    assert response.status_code == 200, response.text
    events = response.json()
    assert events

    for event in events:
        headers = {str(k).lower(): str(v) for k, v in event.get("headers", {}).items()}
        assert admin_token not in json.dumps(headers, ensure_ascii=False)
        if "authorization" in headers:
            assert headers["authorization"] == "***"
        if "cookie" in headers:
            assert headers["cookie"] == "***"


def test_admin_can_cleanup_audit():
    client = TestClient(app)
    admin_token = _login(client, "root", "Secure1!")

    response = client.post("/calc/audit/cleanup?retention_days=1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200, response.text
    assert "deleted" in response.json()


def test_audit_detail_level_is_configurable(tmp_path, monkeypatch):
    monkeypatch.setenv("ENERGY_DB_PATH", str(tmp_path / "audit_detail.sqlite3"))
    monkeypatch.setenv("ENERGY_AUDIT_LOG", str(tmp_path / "audit_detail.log"))
    monkeypatch.setenv("ENERGY_AUDIT_DETAIL_LEVEL", "basic")
    get_settings.cache_clear()
    init_db()
    AuthService().create_user("detailadmin", "Secure1!", role="admin", must_change_password=False)

    client = TestClient(app)
    token = _login(client, "detailadmin", "Secure1!")
    response = client.get("/calc/audit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    events = response.json()
    assert events
    assert all(event.get("headers", {}) == {} for event in events)
    assert all(event.get("details", {}) == {} for event in events)


def test_admin_can_change_user_role_and_policy_is_visible():
    client = TestClient(app)
    admin_token = _login(client, "root", "Secure1!")

    policy_response = client.get("/auth/policy", headers={"Authorization": f"Bearer {admin_token}"})
    assert policy_response.status_code == 200, policy_response.text
    assert policy_response.json()["auth_max_failed_attempts"] == 3
    assert policy_response.json()["auth_lock_minutes"] == 15

    role_response = client.patch(
        "/auth/users/operator/role",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert role_response.status_code == 200, role_response.text
    assert role_response.json()["role"] == "admin"

    audit_response = client.get("/calc/audit", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_response.status_code == 200, audit_response.text
    assert any(event["event_name"] == "user_role_changed" for event in audit_response.json())
