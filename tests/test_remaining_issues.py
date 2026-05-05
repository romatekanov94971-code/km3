from __future__ import annotations

from pathlib import Path


def test_audit_logger_does_not_depend_on_first_handler():
    source = Path("app/audit/logger.py").read_text(encoding="utf-8")
    assert "logger.handlers" + "[0]" not in source
    assert "_energy_system_audit_handler" in source
    assert "existing_handler = next(" in source


def test_lifespan_uses_explicit_auth_service_not_di_helper():
    source = Path("app/server/api.py").read_text(encoding="utf-8")
    assert "AuthService().ensure_default_admin()" in source
    assert "get_auth_service()" + ".ensure_default_admin()" not in source


def test_auth_service_public_all_only_exports_service():
    source = Path("app/auth/service.py").read_text(encoding="utf-8")
    assert '__all__ = ["AuthService"]' in source
