from __future__ import annotations

from pathlib import Path

from app.auth.models import AuthenticatedUser
from app.common.schemas import UserRole


def test_is_admin_accepts_enum_and_string_roles():
    assert AuthenticatedUser(id=1, username="a", role=UserRole.ADMIN).is_admin is True
    assert AuthenticatedUser(id=2, username="u", role=UserRole.USER).is_admin is False
    assert AuthenticatedUser(id=3, username="a2", role="admin").is_admin is True
    assert AuthenticatedUser(id=4, username="u2", role="user").is_admin is False


def test_audit_event_has_no_dead_remote_sent_field():
    source = Path("app/audit/event_models.py").read_text(encoding="utf-8")
    assert "remote_queued" in source
    assert "remote_sent" not in source
    uml = Path("docs/uml/class_diagram_simplified.puml").read_text(encoding="utf-8")
    assert "remote_sent" not in uml


def test_main_window_has_explicit_logout_methods():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert "def _do_logout(" in source
    assert "def _do_logout_and_close(" in source
    assert "logout_action.triggered.connect(self._do_logout_and_close)" in source
    assert "def closeEvent" in source
    assert "self._do_logout(show_errors=False)" in source


def test_audit_event_is_decomposed_into_sinks():
    source = Path("app/audit/logger.py").read_text(encoding="utf-8")
    assert "class AuditSink" in source
    assert "class SQLiteAuditSink" in source
    assert "class RemoteQueueAuditSink" in source
    assert "class FileAuditSink" in source
    assert "for sink in get_audit_sinks()" in source


def test_auth_service_depends_on_repository_protocol():
    source = Path("app/auth/service.py").read_text(encoding="utf-8")
    interface_source = Path("app/storage/interfaces.py").read_text(encoding="utf-8")
    assert "IUserRepository" in source
    assert "users: IUserRepository | None" in source
    assert "class IUserRepository" in interface_source
