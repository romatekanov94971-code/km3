from __future__ import annotations

from pathlib import Path


def test_main_window_button_mentions_graph_audit():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert 'QPushButton("Графики + аудит расчета")' in source


def test_charts_window_has_obvious_audit_tab_and_banner():
    source = Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert "АУДИТ ГРАФИКОВ ВКЛЮЧЕН" in source
    assert "Аудит графиков" in source
    assert "Скопировать расчет выбранной точки" in source
    assert "Есть trace" in source
    assert "График построен из расчетных точек" in source


def test_audit_tab_contains_summary_chart():
    source = Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert "def _audit_overview_figure" in source
    assert "Сводный график расчетных точек" in source
    assert "FigureCanvas(self._audit_overview_figure(result))" in source


from pathlib import Path


def test_temperature_and_load_graphs_have_legends():
    source = Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert 'Теплоотводящая способность' in source
    assert 'КПД нетто' in source
    assert 'Расход топлива' in source
    assert 'ax.legend(lines, labels, loc="best")' in source


def test_vacuum_graph_has_legend():
    source = Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert 'label="КПД нетто"' in source
    assert 'ax.legend(loc="best")' in source
