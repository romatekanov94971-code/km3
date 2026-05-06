from __future__ import annotations

from app.calculation.orchestrator import run_full_calculation
from app.common.schemas import CalculationInput, OperationMode


def sample_input() -> CalculationInput:
    return CalculationInput(
        total_load=400,
        num_blocks=2,
        nominal_power_per_block=300,
        nominal_efficiency=0.38,
        temp_c=25,
        humidity=60,
        wind_speed=3,
        wind_dir=90,
        condenser_vacuum_kpa=88,
        operation_mode=OperationMode.SUMMER,
    )


def test_temperature_points_have_calculation_trace():
    result = run_full_calculation(sample_input()).to_dict()
    point = result["temperature_analysis"][0]
    trace = point["calculation_trace"]

    assert trace["graph"] == "temperature_analysis"
    assert trace["source"] == "calculation_core"
    assert "input" in trace
    assert "formula" in trace
    assert "substitution" in trace
    assert "calculated_factors" in trace
    assert trace["y_axis"]["name"] == "Теплоотводящая способность"


def test_load_distribution_points_have_calculation_trace():
    result = run_full_calculation(sample_input()).to_dict()
    point = result["load_distribution"][0]
    trace = point["calculation_trace"]

    assert trace["graph"] == "load_distribution"
    assert trace["formula"]["load_per_block"] == "total_load / num_blocks"
    assert "fuel_consumption" in trace["substitution"]


def test_vacuum_points_have_calculation_trace():
    result = run_full_calculation(sample_input()).to_dict()
    point = result["condenser_vacuum_optimization"]["points"][0]
    trace = point["calculation_trace"]

    assert trace["graph"] == "condenser_vacuum_optimization"
    assert "condenser_vacuum_factor" in trace["formula"]
    assert "raw_factor" in trace["substitution"]


def test_charts_window_source_exposes_trace_ui():
    source = __import__("pathlib").Path("app/client/charts_window.py").read_text(encoding="utf-8")
    assert "Расчетный след выбранной точки" in source
    assert "calculation_trace" in source
    assert "КАК ПОСЧИТАНА ВЫБРАННАЯ ТОЧКА" in source
