from __future__ import annotations

from app.calculation.constants import (
    CONDENSER_VACUUM_QUADRATIC_LOSS,
    DEFAULT_LOAD_BETA,
    HEAD_WIND_DIRECTION_MAX_DEG,
    HEAD_WIND_DIRECTION_MIN_DEG,
    HEAD_WIND_FACTOR,
    HIGH_HUMIDITY_EFFICIENCY_LOSS_PER_PERCENT,
    HIGH_TEMPERATURE_EFFICIENCY_LOSS_PER_C,
    LOW_TEMPERATURE_EFFICIENCY_GAIN_PER_C,
    MAX_EFFECTIVE_WIND_SPEED_MPS,
    MIN_CONDENSER_VACUUM_FACTOR,
    NEUTRAL_WIND_DIRECTION_FACTOR,
    OPTIMAL_CONDENSER_VACUUM_KPA,
    REFERENCE_HUMIDITY_PERCENT,
    REFERENCE_TEMPERATURE_C,
    TAIL_WIND_DIRECTION_MAX_DEG,
    TAIL_WIND_DIRECTION_MIN_DEG,
    TAIL_WIND_FACTOR,
    WIND_SPEED_EFFECT_PER_MPS,
)


def temp_correction(temp_c: float) -> float:
    """Поправка на температуру наружного воздуха из исходного приложения."""
    if temp_c <= REFERENCE_TEMPERATURE_C:
        return 1 + LOW_TEMPERATURE_EFFICIENCY_GAIN_PER_C * (REFERENCE_TEMPERATURE_C - temp_c)
    return 1 - HIGH_TEMPERATURE_EFFICIENCY_LOSS_PER_C * (temp_c - REFERENCE_TEMPERATURE_C)


def humidity_correction(humidity: float) -> float:
    """Поправка на влажность наружного воздуха из исходного приложения."""
    if humidity <= REFERENCE_HUMIDITY_PERCENT:
        return 1.0
    return 1 - HIGH_HUMIDITY_EFFICIENCY_LOSS_PER_PERCENT * (humidity - REFERENCE_HUMIDITY_PERCENT)


def wind_speed_correction(speed: float) -> float:
    """Поправка на скорость ветра, м/с."""
    effective_speed = min(speed, MAX_EFFECTIVE_WIND_SPEED_MPS)
    return 1 + WIND_SPEED_EFFECT_PER_MPS * effective_speed


def wind_direction_correction(direction_deg: float) -> float:
    """Поправка на направление ветра, градусы."""
    angle = direction_deg % 360
    if HEAD_WIND_DIRECTION_MIN_DEG <= angle <= HEAD_WIND_DIRECTION_MAX_DEG:
        return HEAD_WIND_FACTOR
    if TAIL_WIND_DIRECTION_MIN_DEG <= angle <= TAIL_WIND_DIRECTION_MAX_DEG:
        return TAIL_WIND_FACTOR
    return NEUTRAL_WIND_DIRECTION_FACTOR


def load_correction(
    current_power: float,
    nominal_power: float,
    base_efficiency: float,
    beta: float = DEFAULT_LOAD_BETA,
) -> float:
    """Поправка КПД на частичную нагрузку."""
    load_ratio = current_power / nominal_power
    if load_ratio >= 1:
        return base_efficiency
    return base_efficiency * (1 - beta * (1 - load_ratio) ** 2)


def heat_removal_factor(temp_c: float, humidity: float, wind_speed: float, wind_dir: float) -> float:
    """
    Интегральная теплоотводящая способность энергообъекта.

    В учебной модели она равна произведению внешних поправок. Именно этот
    показатель используется для графика зависимости теплоотводящей способности
    от температуры наружного воздуха.
    """
    return (
        temp_correction(temp_c)
        * humidity_correction(humidity)
        * wind_speed_correction(wind_speed)
        * wind_direction_correction(wind_dir)
    )


def condenser_vacuum_correction(
    vacuum_kpa: float,
    optimal_vacuum_kpa: float = OPTIMAL_CONDENSER_VACUUM_KPA,
) -> float:
    """
    Учебная поправка на разрежение в конденсаторе турбины.

    В исходном приложении методики по разрежению нет, но ТЗ требует найти
    оптимальное значение. Поэтому используется гладкая квадратичная модель:
    максимум КПД достигается около 88 кПа, при отклонении КПД снижается.
    Коэффициенты вынесены в именованные константы, чтобы их можно было заменить
    на промышленную методику без изменения остального приложения.
    """
    deviation = vacuum_kpa - optimal_vacuum_kpa
    return max(MIN_CONDENSER_VACUUM_FACTOR, 1 - CONDENSER_VACUUM_QUADRATIC_LOSS * deviation**2)
