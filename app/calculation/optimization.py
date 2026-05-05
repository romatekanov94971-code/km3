from __future__ import annotations

from dataclasses import replace

from app.calculation.core import calc_tes_efficiency
from app.calculation.formulas import condenser_vacuum_correction, heat_removal_factor
from app.common.schemas import (
    CalculationInput,
    CondenserVacuumOptimizationResult,
    CondenserVacuumPoint,
    LoadDistributionPoint,
    TemperatureAnalysisPoint,
)


def analyze_temperature(
    data: CalculationInput,
    temp_min: int = -20,
    temp_max: int = 40,
    step: int = 5,
) -> list[TemperatureAnalysisPoint]:
    """Анализ зависимости КПД и теплоотводящей способности от температуры."""
    if step <= 0:
        raise ValueError("Шаг температуры должен быть больше 0.")

    points: list[TemperatureAnalysisPoint] = []
    for temp_c in range(temp_min, temp_max + 1, step):
        current = replace(data, temp_c=float(temp_c))
        result = calc_tes_efficiency(current)
        points.append(
            TemperatureAnalysisPoint(
                temp_c=float(temp_c),
                heat_removal_factor=heat_removal_factor(
                    float(temp_c), data.humidity, data.wind_speed, data.wind_dir
                ),
                efficiency_netto_percent=result.efficiency_netto * 100,
                fuel_consumption=result.fuel_consumption,
            )
        )
    return points


def analyze_load_distribution(data: CalculationInput, max_blocks: int = 8) -> list[LoadDistributionPoint]:
    """Анализ эффективности при разном количестве работающих блоков."""
    if max_blocks <= 0:
        raise ValueError("Максимальное количество блоков должно быть больше 0.")

    points: list[LoadDistributionPoint] = []
    for blocks in range(1, max_blocks + 1):
        if blocks * data.nominal_power_per_block < data.total_load:
            continue
        current = replace(data, num_blocks=blocks)
        result = calc_tes_efficiency(current)
        points.append(
            LoadDistributionPoint(
                blocks=blocks,
                load_per_block=result.load_per_block,
                load_percent=result.load_per_block / data.nominal_power_per_block * 100,
                efficiency_netto_percent=result.efficiency_netto * 100,
                fuel_consumption=result.fuel_consumption,
            )
        )
    return points


def find_optimal_blocks(data: CalculationInput, max_blocks: int = 8) -> LoadDistributionPoint:
    """Поиск количества блоков с максимальным КПД нетто."""
    points = analyze_load_distribution(data, max_blocks=max_blocks)
    if not points:
        raise ValueError("Нет допустимого количества блоков для заданной нагрузки.")
    return max(points, key=lambda point: point.efficiency_netto_percent)


def optimize_condenser_vacuum(
    data: CalculationInput,
    vacuum_min_kpa: int = 70,
    vacuum_max_kpa: int = 95,
    step_kpa: int = 1,
) -> CondenserVacuumOptimizationResult:
    """Поиск оптимального значения разрежения в конденсаторе турбины."""
    if step_kpa <= 0:
        raise ValueError("Шаг разрежения должен быть больше 0.")
    if vacuum_min_kpa > vacuum_max_kpa:
        raise ValueError("Минимальное разрежение не может быть больше максимального.")

    points: list[CondenserVacuumPoint] = []
    for vacuum in range(vacuum_min_kpa, vacuum_max_kpa + 1, step_kpa):
        current = replace(data, condenser_vacuum_kpa=float(vacuum))
        result = calc_tes_efficiency(current)
        points.append(
            CondenserVacuumPoint(
                vacuum_kpa=float(vacuum),
                condenser_vacuum_factor=condenser_vacuum_correction(float(vacuum)),
                block_efficiency_percent=result.block_efficiency * 100,
                efficiency_netto_percent=result.efficiency_netto * 100,
                fuel_consumption=result.fuel_consumption,
            )
        )
    best = max(points, key=lambda point: point.efficiency_netto_percent)
    return CondenserVacuumOptimizationResult(
        best_vacuum_kpa=best.vacuum_kpa,
        best_efficiency_netto_percent=best.efficiency_netto_percent,
        best_fuel_consumption=best.fuel_consumption,
        points=points,
    )


__all__ = ['analyze_temperature', 'analyze_load_distribution', 'find_optimal_blocks', 'optimize_condenser_vacuum']
