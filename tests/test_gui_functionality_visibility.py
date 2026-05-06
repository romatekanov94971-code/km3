from __future__ import annotations

from pathlib import Path

from app.server.schemas import CalculationRequest


def test_main_window_exposes_condenser_vacuum_season_and_history():
    source = Path("app/client/main_window.py").read_text(encoding="utf-8")
    assert "self.operation_mode" in source
    assert "Зимний режим" in source
    assert "Летний режим" in source
    assert "self.condenser_vacuum" in source
    assert "Разрежение в конденсаторе" in source
    assert "history_button" in source
    assert "HistoryWindow" in source


def test_charts_window_exposes_all_analysis_tabs():
    source = Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert "Температура" in source
    assert "Блоки" in source
    assert "Конденсатор" in source
    assert "load_distribution" in source
    assert "condenser_vacuum_optimization" in source


def test_history_window_exists():
    source = Path("app/client/history_window.py").read_text(encoding="utf-8")
    assert "class HistoryWindow" in source
    assert "get_history" in source


def test_calculation_request_dumps_operation_mode_as_string():
    payload = CalculationRequest(
        total_load=400,
        num_blocks=2,
        nominal_power_per_block=300,
        nominal_efficiency=0.38,
        temp_c=25,
        humidity=60,
        wind_speed=3,
        wind_dir=90,
        condenser_vacuum_kpa=88,
        operation_mode="winter",
    )
    dumped = payload.model_dump()
    assert dumped["operation_mode"] == "winter"
    assert dumped["condenser_vacuum_kpa"] == 88
