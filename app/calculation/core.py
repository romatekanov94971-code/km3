from __future__ import annotations

from app.calculation.constants import (
    DEFAULT_LOAD_BETA,
    FUEL_CONSUMPTION_COEFFICIENT,
    OWN_NEEDS_HIGH_TEMPERATURE_INCREASE_PER_C,
    OWN_NEEDS_HIGH_TEMPERATURE_THRESHOLD_C,
    OWN_NEEDS_LOW_TEMPERATURE_INCREASE_PER_C,
    OWN_NEEDS_LOW_TEMPERATURE_THRESHOLD_C,
    SUMMER_HEAT_REMOVAL_FACTOR,
    SUMMER_OWN_NEEDS_EXTRA_COEFF,
    WINTER_HEAT_REMOVAL_FACTOR,
    WINTER_MODE_MAX_TEMPERATURE_C,
    WINTER_OWN_NEEDS_EXTRA_COEFF,
)
from app.calculation.formulas import (
    condenser_vacuum_correction,
    humidity_correction,
    load_correction,
    temp_correction,
    wind_direction_correction,
    wind_speed_correction,
)
from app.calculation.validators import validate_calculation_input
from app.common.schemas import CalculationInput, CalculationResult, OperationMode


def calc_block_efficiency(
    power_mw: float,
    nominal_power: float,
    nominal_efficiency: float,
    beta: float = DEFAULT_LOAD_BETA,
    external_factor: float = 1.0,
    condenser_vacuum_factor: float = 1.0,
) -> float:
    """Расчет КПД одного энергоблока без повторного расчета внешних факторов."""
    efficiency_at_nominal = nominal_efficiency * external_factor * condenser_vacuum_factor
    return load_correction(power_mw, nominal_power, efficiency_at_nominal, beta)


def resolve_operation_mode(temp_c: float, mode: OperationMode | str = OperationMode.AUTO) -> OperationMode:
    """Определяет фактически применяемый сезонный режим."""
    mode_value = mode if isinstance(mode, OperationMode) else OperationMode(str(mode))
    if mode_value is OperationMode.AUTO:
        return OperationMode.WINTER if temp_c < WINTER_MODE_MAX_TEMPERATURE_C else OperationMode.SUMMER
    return mode_value


def seasonal_heat_removal_factor(mode: OperationMode) -> float:
    """Сезонная поправка к теплоотводящей способности."""
    return WINTER_HEAT_REMOVAL_FACTOR if mode is OperationMode.WINTER else SUMMER_HEAT_REMOVAL_FACTOR


def calc_own_needs_coeff(temp_c: float, base_coeff: float, mode: OperationMode | str = OperationMode.AUTO) -> float:
    """Коэффициент собственных нужд с учетом температуры и режима работы."""
    applied_mode = resolve_operation_mode(temp_c, mode)
    own_needs = base_coeff
    if temp_c > OWN_NEEDS_HIGH_TEMPERATURE_THRESHOLD_C:
        own_needs += OWN_NEEDS_HIGH_TEMPERATURE_INCREASE_PER_C * (
            temp_c - OWN_NEEDS_HIGH_TEMPERATURE_THRESHOLD_C
        )
    elif temp_c < OWN_NEEDS_LOW_TEMPERATURE_THRESHOLD_C:
        own_needs += OWN_NEEDS_LOW_TEMPERATURE_INCREASE_PER_C * abs(temp_c)

    if applied_mode is OperationMode.WINTER:
        own_needs += WINTER_OWN_NEEDS_EXTRA_COEFF
    else:
        own_needs += SUMMER_OWN_NEEDS_EXTRA_COEFF
    return own_needs


def calc_tes_efficiency(data: CalculationInput) -> CalculationResult:
    """Основной расчет эффективности ТЭС."""
    validate_calculation_input(data)

    load_per_block = data.total_load / data.num_blocks
    is_overloaded = load_per_block > data.nominal_power_per_block
    warning = None

    if is_overloaded:
        warning = (
            f"Блок перегружен: {load_per_block:.1f} > "
            f"{data.nominal_power_per_block:.1f} МВт. "
            "Для расчета нагрузка блока ограничена номинальной мощностью."
        )
        load_per_block = data.nominal_power_per_block

    applied_mode = resolve_operation_mode(data.temp_c, data.operation_mode)
    temp_factor = temp_correction(data.temp_c)
    humid_factor = humidity_correction(data.humidity)
    wind_speed_factor = wind_speed_correction(data.wind_speed)
    wind_direction_factor = wind_direction_correction(data.wind_dir)
    season_factor = seasonal_heat_removal_factor(applied_mode)
    external_factor = temp_factor * humid_factor * wind_speed_factor * wind_direction_factor * season_factor
    vacuum_factor = condenser_vacuum_correction(data.condenser_vacuum_kpa) if data.condenser_vacuum_kpa else 1.0

    block_efficiency = calc_block_efficiency(
        power_mw=load_per_block,
        nominal_power=data.nominal_power_per_block,
        nominal_efficiency=data.nominal_efficiency,
        beta=data.beta,
        external_factor=external_factor,
        condenser_vacuum_factor=vacuum_factor,
    )

    total_power_brutto = data.num_blocks * load_per_block
    efficiency_brutto = block_efficiency

    own_needs = calc_own_needs_coeff(data.temp_c, data.own_needs_coeff, applied_mode)
    own_needs_power = total_power_brutto * own_needs
    total_power_netto = total_power_brutto - own_needs_power
    efficiency_netto = efficiency_brutto * (1 - own_needs)
    fuel_consumption = FUEL_CONSUMPTION_COEFFICIENT / efficiency_netto if efficiency_netto > 0 else float("inf")

    return CalculationResult(
        load_per_block=load_per_block,
        block_efficiency=block_efficiency,
        efficiency_brutto=efficiency_brutto,
        own_needs_power=own_needs_power,
        own_needs_percent=own_needs * 100,
        efficiency_netto=efficiency_netto,
        fuel_consumption=fuel_consumption,
        total_power_brutto=total_power_brutto,
        total_power_netto=total_power_netto,
        external_factor=external_factor,
        temperature_factor=temp_factor,
        humidity_factor=humid_factor,
        wind_speed_factor=wind_speed_factor,
        wind_direction_factor=wind_direction_factor,
        condenser_vacuum_factor=vacuum_factor,
        is_overloaded=is_overloaded,
        warning=warning,
        operation_mode=applied_mode.value,
    )


__all__ = ['calc_block_efficiency', 'calc_own_needs_coeff', 'calc_tes_efficiency', 'resolve_operation_mode', 'seasonal_heat_removal_factor']
