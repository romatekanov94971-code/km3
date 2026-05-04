from __future__ import annotations

from app.common.exceptions import ValidationError
from app.common.schemas import CalculationInput


def validate_calculation_input(data: CalculationInput) -> None:
    """Проверка входных параметров расчета."""
    if data.total_load <= 0:
        raise ValidationError("Общая нагрузка ТЭС должна быть больше 0 МВт.")
    if data.num_blocks <= 0:
        raise ValidationError("Количество работающих блоков должно быть больше 0.")
    if data.nominal_power_per_block <= 0:
        raise ValidationError("Номинальная мощность блока должна быть больше 0 МВт.")
    if not 0 < data.nominal_efficiency < 1:
        raise ValidationError("Номинальный КПД должен быть долей от 0 до 1, например 0.38.")
    if data.temp_c < -60 or data.temp_c > 60:
        raise ValidationError("Температура наружного воздуха должна быть в диапазоне от -60 до 60 °C.")
    if not 0 <= data.humidity <= 100:
        raise ValidationError("Влажность должна быть в диапазоне от 0 до 100%.")
    if data.wind_speed < 0 or data.wind_speed > 80:
        raise ValidationError("Скорость ветра должна быть в диапазоне от 0 до 80 м/с.")
    if not 0 <= data.wind_dir <= 360:
        raise ValidationError("Направление ветра должно быть в диапазоне от 0 до 360 градусов.")
    if data.own_needs_coeff < 0 or data.own_needs_coeff >= 0.5:
        raise ValidationError("Коэффициент собственных нужд должен быть от 0 до 0.5.")
    if data.beta < 0 or data.beta > 2:
        raise ValidationError("Коэффициент beta должен быть от 0 до 2.")
    if data.condenser_vacuum_kpa is not None and not 50 <= data.condenser_vacuum_kpa <= 110:
        raise ValidationError("Разрежение в конденсаторе должно быть в диапазоне от 50 до 110 кПа.")
