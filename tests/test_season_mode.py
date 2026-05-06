from __future__ import annotations

import pytest

from app.calculation.core import calc_tes_efficiency, resolve_operation_mode
from app.common.exceptions import ValidationError
from app.common.schemas import CalculationInput, OperationMode


def sample_input(**overrides):
    data = dict(
        total_load=400,
        num_blocks=2,
        nominal_power_per_block=300,
        nominal_efficiency=0.38,
        temp_c=25,
        humidity=60,
        wind_speed=3,
        wind_dir=90,
    )
    data.update(overrides)
    return CalculationInput(**data)


def test_auto_mode_selects_winter_for_low_temperature():
    assert resolve_operation_mode(-10, OperationMode.AUTO) is OperationMode.WINTER


def test_auto_mode_selects_summer_for_positive_temperature():
    assert resolve_operation_mode(25, OperationMode.AUTO) is OperationMode.SUMMER


def test_forced_winter_and_summer_modes_affect_result():
    winter = calc_tes_efficiency(sample_input(temp_c=10, operation_mode=OperationMode.WINTER))
    summer = calc_tes_efficiency(sample_input(temp_c=10, operation_mode=OperationMode.SUMMER))

    assert winter.operation_mode == "winter"
    assert summer.operation_mode == "summer"
    assert winter.external_factor != pytest.approx(summer.external_factor)
    assert winter.own_needs_percent != pytest.approx(summer.own_needs_percent)


def test_invalid_operation_mode_raises_validation_error():
    with pytest.raises(ValidationError):
        calc_tes_efficiency(sample_input(operation_mode="spring"))
