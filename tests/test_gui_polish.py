from __future__ import annotations

from pathlib import Path


def test_global_qt_style_is_applied_in_gui_startup():
    main = Path("main.py").read_text(encoding="utf-8")
    style = Path("app/client/style.py").read_text(encoding="utf-8")
    assert "apply_app_style(app)" in main
    assert "APP_STYLESHEET" in style
    assert "primaryButton" in style
    assert "polish_table" in style


def test_main_window_has_grouped_clean_layout_and_summary():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert "QGroupBox" in source
    assert "Нагрузка и оборудование" in source
    assert "Внешние условия" in source
    assert "Дополнительные параметры и оптимизация" in source
    assert "self.summary" in source
    assert "statusBar().showMessage" in source


def test_dialogs_have_titles_and_primary_buttons():
    files = [
        "app/client/login_window.py",
        "app/client/change_password_window.py",
        "app/client/create_user_window.py",
        "app/client/change_role_window.py",
        "app/client/security_settings_window.py",
    ]
    for file in files:
        source = Path(file).read_text(encoding="utf-8")
        assert 'setProperty("role", "title")' in source
        assert "primaryButton" in source


def test_tables_are_polished():
    for file in ["app/client/audit_window.py", "app/client/history_window.py"]:
        source = Path(file).read_text(encoding="utf-8")
        assert "polish_table(self.table)" in source
        assert "SelectRows" in source
        assert "SingleSelection" in source
