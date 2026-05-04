import pytest

from app.calculation.core import calc_tes_efficiency
from app.calculation.optimization import analyze_temperature, find_optimal_blocks, optimize_condenser_vacuum
from app.common.exceptions import ValidationError
from app.common.schemas import CalculationInput


def sample_input(**overrides):
    data = dict(
        total_load=400,
        num_blocks=2,
        nominal_power_per_block=300,
        nominal_efficiency=0.38,
        temp_c=32,
        humidity=80,
        wind_speed=5,
        wind_dir=30,
    )
    data.update(overrides)
    return CalculationInput(**data)


def test_calc_tes_efficiency_outputs_required_indicators():
    result = calc_tes_efficiency(sample_input())
    assert result.load_per_block == pytest.approx(200)
    assert result.block_efficiency > 0
    assert result.efficiency_brutto > result.efficiency_netto
    assert result.own_needs_power > 0
    assert result.fuel_consumption > 0
    assert result.external_factor > 0


def test_overload_is_limited_by_nominal_power():
    result = calc_tes_efficiency(sample_input(total_load=700))
    assert result.is_overloaded is True
    assert result.load_per_block == pytest.approx(300)
    assert result.warning is not None


def test_invalid_humidity_raises_error():
    with pytest.raises(ValidationError):
        calc_tes_efficiency(sample_input(humidity=120))


def test_find_optimal_blocks():
    best = find_optimal_blocks(sample_input(temp_c=25, humidity=60, wind_dir=90), max_blocks=4)
    assert best.blocks in {2, 3, 4}
    assert best.efficiency_netto_percent > 0


def test_optimize_condenser_vacuum():
    result = optimize_condenser_vacuum(sample_input(temp_c=20, humidity=60, wind_dir=90))
    assert result.best_vacuum_kpa == pytest.approx(88)
    assert result.best_efficiency_netto_percent > 0
    assert len(result.points) > 0


def test_temperature_analysis_contains_heat_removal_factor():
    points = analyze_temperature(sample_input(humidity=60, wind_dir=90), temp_min=-10, temp_max=10, step=10)
    assert len(points) == 3
    assert all(point.heat_removal_factor > 0 for point in points)
