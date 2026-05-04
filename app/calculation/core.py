from __future__ import annotations

from app.calculation.formulas import (
    condenser_vacuum_correction,
    heat_removal_factor,
    humidity_correction,
    load_correction,
    temp_correction,
    wind_direction_correction,
    wind_speed_correction,
)
from app.calculation.validators import validate_calculation_input
from app.common.schemas import CalculationInput, CalculationResult


def calc_block_efficiency(
    power_mw: float,
    nominal_power: float,
    nominal_efficiency: float,
    temp_c: float,
    humidity: float,
    wind_speed: float,
    wind_dir: float,
    beta: float = 0.4,
    condenser_vacuum_kpa: float | None = None,
) -> float:
    """Расчет КПД одного энергоблока с учетом нагрузки и внешних факторов."""
    external_factor = heat_removal_factor(temp_c, humidity, wind_speed, wind_dir)
    vacuum_factor = condenser_vacuum_correction(condenser_vacuum_kpa) if condenser_vacuum_kpa else 1.0
    efficiency_at_nominal = nominal_efficiency * external_factor * vacuum_factor
    return load_correction(power_mw, nominal_power, efficiency_at_nominal, beta)


def calc_own_needs_coeff(temp_c: float, base_coeff: float) -> float:
    """Коэффициент собственных нужд с учетом температуры."""
    own_needs = base_coeff
    if temp_c > 25:
        own_needs += 0.005 * (temp_c - 25)
    elif temp_c < 0:
        own_needs += 0.003 * abs(temp_c)
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

    temp_factor = temp_correction(data.temp_c)
    humid_factor = humidity_correction(data.humidity)
    wind_speed_factor = wind_speed_correction(data.wind_speed)
    wind_direction_factor = wind_direction_correction(data.wind_dir)
    external_factor = temp_factor * humid_factor * wind_speed_factor * wind_direction_factor
    vacuum_factor = condenser_vacuum_correction(data.condenser_vacuum_kpa) if data.condenser_vacuum_kpa else 1.0

    block_efficiency = calc_block_efficiency(
        power_mw=load_per_block,
        nominal_power=data.nominal_power_per_block,
        nominal_efficiency=data.nominal_efficiency,
        temp_c=data.temp_c,
        humidity=data.humidity,
        wind_speed=data.wind_speed,
        wind_dir=data.wind_dir,
        beta=data.beta,
        condenser_vacuum_kpa=data.condenser_vacuum_kpa,
    )

    total_power_brutto = data.num_blocks * load_per_block
    efficiency_brutto = block_efficiency

    own_needs = calc_own_needs_coeff(data.temp_c, data.own_needs_coeff)
    own_needs_power = total_power_brutto * own_needs
    total_power_netto = total_power_brutto - own_needs_power
    efficiency_netto = efficiency_brutto * (1 - own_needs)
    fuel_consumption = 123 / efficiency_netto if efficiency_netto > 0 else float("inf")

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
    )
