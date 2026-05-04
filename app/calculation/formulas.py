from __future__ import annotations


def temp_correction(temp_c: float) -> float:
    """Поправка на температуру наружного воздуха из исходного приложения."""
    if temp_c <= 15:
        return 1 + 0.003 * (15 - temp_c)
    return 1 - 0.002 * (temp_c - 15)


def humidity_correction(humidity: float) -> float:
    """Поправка на влажность наружного воздуха из исходного приложения."""
    if humidity <= 60:
        return 1.0
    return 1 - 0.0005 * (humidity - 60)


def wind_speed_correction(speed: float) -> float:
    """Поправка на скорость ветра, м/с."""
    if speed <= 8:
        return 1 + 0.002 * speed
    return 1 + 0.002 * 8


def wind_direction_correction(direction_deg: float) -> float:
    """Поправка на направление ветра, градусы."""
    angle = direction_deg % 360
    if 0 <= angle <= 45:
        return 0.99
    if 180 <= angle <= 225:
        return 1.01
    return 1.00


def load_correction(
    current_power: float,
    nominal_power: float,
    base_efficiency: float,
    beta: float = 0.4,
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


def condenser_vacuum_correction(vacuum_kpa: float, optimal_vacuum_kpa: float = 88.0) -> float:
    """
    Учебная поправка на разрежение в конденсаторе турбины.

    В исходном приложении методики по разрежению нет, но ТЗ требует найти
    оптимальное значение. Поэтому используется гладкая квадратичная модель:
    максимум КПД достигается около 88 кПа, при отклонении КПД снижается.
    Коэффициенты вынесены в одну функцию, чтобы их можно было заменить на
    промышленную методику без изменения остального приложения.
    """
    deviation = vacuum_kpa - optimal_vacuum_kpa
    return max(0.94, 1 - 0.00035 * deviation**2)
