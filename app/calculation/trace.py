from __future__ import annotations

from typing import Any

from app.calculation.constants import (
    CONDENSER_VACUUM_QUADRATIC_LOSS,
    FUEL_CONSUMPTION_COEFFICIENT,
    MAX_EFFECTIVE_WIND_SPEED_MPS,
    MIN_CONDENSER_VACUUM_FACTOR,
    OPTIMAL_CONDENSER_VACUUM_KPA,
    REFERENCE_HUMIDITY_PERCENT,
    REFERENCE_TEMPERATURE_C,
)
from app.calculation.core import resolve_operation_mode, seasonal_heat_removal_factor
from app.common.schemas import CalculationInput, CalculationResult


def _r(value: float | int | None, digits: int = 6) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    return round(float(value), digits)


def source_input_snapshot(data: CalculationInput) -> dict[str, Any]:
    """Фиксирует исходные параметры, из которых строится точка графика."""
    return {
        "total_load_mw": _r(data.total_load),
        "num_blocks": data.num_blocks,
        "nominal_power_per_block_mw": _r(data.nominal_power_per_block),
        "nominal_efficiency": _r(data.nominal_efficiency),
        "temp_c": _r(data.temp_c),
        "humidity_percent": _r(data.humidity),
        "wind_speed_mps": _r(data.wind_speed),
        "wind_direction_deg": _r(data.wind_dir),
        "own_needs_coeff": _r(data.own_needs_coeff),
        "beta": _r(data.beta),
        "condenser_vacuum_kpa": _r(data.condenser_vacuum_kpa),
        "requested_operation_mode": str(data.operation_mode),
    }


def base_trace(data: CalculationInput, result: CalculationResult) -> dict[str, Any]:
    applied_mode = resolve_operation_mode(data.temp_c, data.operation_mode)
    return {
        "source": "calculation_core",
        "note": "Точка графика построена не из случайных/захардкоженных чисел, а из введенных параметров и расчетных формул ядра.",
        "input": source_input_snapshot(data),
        "applied_operation_mode": applied_mode.value,
        "calculated_factors": {
            "temperature_factor": _r(result.temperature_factor),
            "humidity_factor": _r(result.humidity_factor),
            "wind_speed_factor": _r(result.wind_speed_factor),
            "wind_direction_factor": _r(result.wind_direction_factor),
            "seasonal_factor": _r(seasonal_heat_removal_factor(applied_mode)),
            "condenser_vacuum_factor": _r(result.condenser_vacuum_factor),
            "external_factor": _r(result.external_factor),
            "own_needs_percent": _r(result.own_needs_percent),
        },
        "main_result": {
            "load_per_block_mw": _r(result.load_per_block),
            "efficiency_brutto_percent": _r(result.efficiency_brutto * 100),
            "efficiency_netto_percent": _r(result.efficiency_netto * 100),
            "fuel_consumption": _r(result.fuel_consumption),
        },
    }


def temperature_point_trace(
    data: CalculationInput,
    result: CalculationResult,
    heat_removal_factor: float,
) -> dict[str, Any]:
    trace = base_trace(data, result)
    trace.update(
        {
            "graph": "temperature_analysis",
            "x_axis": {"name": "Температура наружного воздуха", "value": _r(data.temp_c), "unit": "°C"},
            "y_axis": {
                "name": "Теплоотводящая способность",
                "value": _r(heat_removal_factor),
                "unit": "relative",
            },
            "formula": {
                "temperature_factor": (
                    f"если T <= {REFERENCE_TEMPERATURE_C}: "
                    f"1 + 0.003 * ({REFERENCE_TEMPERATURE_C} - T), иначе 1 - 0.002 * (T - {REFERENCE_TEMPERATURE_C})"
                ),
                "humidity_factor": f"если H <= {REFERENCE_HUMIDITY_PERCENT}: 1, иначе 1 - 0.0005 * (H - {REFERENCE_HUMIDITY_PERCENT})",
                "wind_speed_factor": f"1 + 0.002 * min(V, {MAX_EFFECTIVE_WIND_SPEED_MPS})",
                "heat_removal_factor": "temperature_factor * humidity_factor * wind_speed_factor * wind_direction_factor * seasonal_factor",
            },
            "substitution": (
                f"{_r(result.temperature_factor)} * {_r(result.humidity_factor)} * "
                f"{_r(result.wind_speed_factor)} * {_r(result.wind_direction_factor)} * "
                f"{_r(trace['calculated_factors']['seasonal_factor'])} = {_r(heat_removal_factor)}"
            ),
        }
    )
    return trace


def load_distribution_trace(data: CalculationInput, result: CalculationResult) -> dict[str, Any]:
    trace = base_trace(data, result)
    load_percent = result.load_per_block / data.nominal_power_per_block * 100
    trace.update(
        {
            "graph": "load_distribution",
            "x_axis": {"name": "Количество работающих блоков", "value": data.num_blocks, "unit": "шт."},
            "y_axis": {"name": "КПД нетто", "value": _r(result.efficiency_netto * 100), "unit": "%"},
            "formula": {
                "load_per_block": "total_load / num_blocks",
                "load_percent": "load_per_block / nominal_power_per_block * 100",
                "efficiency_netto": "block_efficiency * (1 - own_needs_coeff_with_temperature_and_season)",
                "fuel_consumption": f"{FUEL_CONSUMPTION_COEFFICIENT} / efficiency_netto",
            },
            "substitution": {
                "load_per_block": f"{_r(data.total_load)} / {data.num_blocks} = {_r(result.load_per_block)} МВт",
                "load_percent": f"{_r(result.load_per_block)} / {_r(data.nominal_power_per_block)} * 100 = {_r(load_percent)}%",
                "fuel_consumption": f"{FUEL_CONSUMPTION_COEFFICIENT} / {_r(result.efficiency_netto)} = {_r(result.fuel_consumption)}",
            },
        }
    )
    return trace


def condenser_vacuum_trace(data: CalculationInput, result: CalculationResult) -> dict[str, Any]:
    trace = base_trace(data, result)
    vacuum = float(data.condenser_vacuum_kpa or OPTIMAL_CONDENSER_VACUUM_KPA)
    deviation = vacuum - OPTIMAL_CONDENSER_VACUUM_KPA
    raw_factor = 1 - CONDENSER_VACUUM_QUADRATIC_LOSS * deviation**2
    trace.update(
        {
            "graph": "condenser_vacuum_optimization",
            "x_axis": {"name": "Разрежение в конденсаторе", "value": _r(vacuum), "unit": "кПа"},
            "y_axis": {"name": "КПД нетто", "value": _r(result.efficiency_netto * 100), "unit": "%"},
            "formula": {
                "condenser_vacuum_factor": (
                    f"max({MIN_CONDENSER_VACUUM_FACTOR}, "
                    f"1 - {CONDENSER_VACUUM_QUADRATIC_LOSS} * (vacuum_kpa - {OPTIMAL_CONDENSER_VACUUM_KPA})^2)"
                ),
                "efficiency_netto": "nominal_efficiency * external_factor * condenser_vacuum_factor * load_correction * (1 - own_needs)",
            },
            "substitution": {
                "deviation": f"{_r(vacuum)} - {OPTIMAL_CONDENSER_VACUUM_KPA} = {_r(deviation)}",
                "raw_factor": f"1 - {CONDENSER_VACUUM_QUADRATIC_LOSS} * ({_r(deviation)})^2 = {_r(raw_factor)}",
                "condenser_vacuum_factor": f"max({MIN_CONDENSER_VACUUM_FACTOR}, {_r(raw_factor)}) = {_r(result.condenser_vacuum_factor)}",
            },
        }
    )
    return trace


__all__ = [
    "base_trace",
    "condenser_vacuum_trace",
    "load_distribution_trace",
    "source_input_snapshot",
    "temperature_point_trace",
]
