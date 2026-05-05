from __future__ import annotations

from app.calculation.core import calc_tes_efficiency
from app.calculation.optimization import (
    analyze_load_distribution,
    analyze_temperature,
    find_optimal_blocks,
    optimize_condenser_vacuum,
)
from app.common.schemas import CalculationInput, FullCalculationResult


def run_full_calculation(data: CalculationInput) -> FullCalculationResult:
    """Единая точка запуска расчета для API, GUI и CLI."""
    main_result = calc_tes_efficiency(data)
    temp_analysis = analyze_temperature(data)
    load_analysis = analyze_load_distribution(data)
    optimal_blocks = find_optimal_blocks(data)
    vacuum_optimization = optimize_condenser_vacuum(data)

    return FullCalculationResult(
        main_result=main_result,
        temperature_analysis=temp_analysis,
        load_distribution=load_analysis,
        optimal_blocks=optimal_blocks,
        condenser_vacuum_optimization=vacuum_optimization,
    )


__all__ = ['run_full_calculation']
