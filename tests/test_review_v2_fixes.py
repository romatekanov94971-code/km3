from __future__ import annotations

from pathlib import Path


def test_session_manager_has_unsafe_cleanup_split():
    source = Path("app/auth/session_manager.py").read_text(encoding="utf-8")
    assert "def _cleanup_unsafe" in source
    assert "self._cleanup_unsafe()" in source
    assert "self.cleanup()" not in source.split("def create_session", 1)[1].split("def get_user", 1)[0]


def test_audit_logger_uses_replace_and_no_global_logger():
    source = Path("app/audit/logger.py").read_text(encoding="utf-8")
    assert "from dataclasses import replace" in source
    assert "replace(event, sequence_number=sequence_number)" in source
    assert "replace(event, remote_queued=remote_queued)" in source
    assert "global _LOGGER" not in source
    assert "_LOGGER:" not in source


def test_auth_service_dependency_comment_is_explicit():
    source = Path("app/server/dependencies.py").read_text(encoding="utf-8")
    assert "SessionManager" in source
    assert "глобальным singleton" in source
    assert "per-process" in source


def test_calculation_request_mapping_is_outside_pydantic_model():
    schema_source = Path("app/server/schemas.py").read_text(encoding="utf-8")
    mapper_source = Path("app/server/mappers.py").read_text(encoding="utf-8")
    route_source = Path("app/server/routes/calc.py").read_text(encoding="utf-8")
    assert "def to_input" not in schema_source
    assert "calculation_request_to_input" in mapper_source
    assert "payload.to_input()" not in route_source


def test_fastapi_uses_lifespan_not_deprecated_on_event():
    source = Path("app/server/api.py").read_text(encoding="utf-8")
    assert "lifespan=lifespan" in source
    assert "on_event" not in source


def test_gui_export_does_not_show_server_path_directly():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert "result['path']" not in source
    assert "filename" in source


def test_pyproject_exists_for_pytest():
    source = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pytest.ini_options]" in source
    assert "pythonpath" in source


def test_public_modules_define_all():
    modules = [
        "app/server/schemas.py",
        "app/server/mappers.py",
        "app/calculation/core.py",
        "app/calculation/formulas.py",
        "app/audit/logger.py",
        "app/auth/session_manager.py",
    ]
    for module in modules:
        assert "__all__" in Path(module).read_text(encoding="utf-8")
