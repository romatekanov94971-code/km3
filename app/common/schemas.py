from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class OperationMode(str, Enum):
    """Режим работы энергообъекта."""

    AUTO = "auto"
    WINTER = "winter"
    SUMMER = "summer"


# Backward-compatible public alias.
Role = UserRole


@dataclass(frozen=True)
class CalculationInput:
    """Входные параметры расчета эффективности ТЭС."""

    total_load: float
    num_blocks: int
    nominal_power_per_block: float
    nominal_efficiency: float
    temp_c: float
    humidity: float
    wind_speed: float
    wind_dir: float
    own_needs_coeff: float = 0.05
    beta: float = 0.4
    condenser_vacuum_kpa: float | None = None
    operation_mode: OperationMode | str = OperationMode.AUTO

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CalculationInput":
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass(frozen=True)
class CalculationResult:
    """Выходные показатели расчета, требуемые ТЗ."""

    load_per_block: float
    block_efficiency: float
    efficiency_brutto: float
    own_needs_power: float
    own_needs_percent: float
    efficiency_netto: float
    fuel_consumption: float
    total_power_brutto: float
    total_power_netto: float
    external_factor: float
    temperature_factor: float
    humidity_factor: float
    wind_speed_factor: float
    wind_direction_factor: float
    condenser_vacuum_factor: float = 1.0
    is_overloaded: bool = False
    warning: str | None = None
    operation_mode: str = OperationMode.AUTO.value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TemperatureAnalysisPoint:
    temp_c: float
    heat_removal_factor: float
    efficiency_netto_percent: float
    fuel_consumption: float
    calculation_trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LoadDistributionPoint:
    blocks: int
    load_per_block: float
    load_percent: float
    efficiency_netto_percent: float
    fuel_consumption: float
    calculation_trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CondenserVacuumPoint:
    vacuum_kpa: float
    condenser_vacuum_factor: float
    block_efficiency_percent: float
    efficiency_netto_percent: float
    fuel_consumption: float
    calculation_trace: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CondenserVacuumOptimizationResult:
    best_vacuum_kpa: float
    best_efficiency_netto_percent: float
    best_fuel_consumption: float
    points: list[CondenserVacuumPoint] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_vacuum_kpa": self.best_vacuum_kpa,
            "best_efficiency_netto_percent": self.best_efficiency_netto_percent,
            "best_fuel_consumption": self.best_fuel_consumption,
            "points": [point.to_dict() for point in self.points],
        }


@dataclass(frozen=True)
class FullCalculationResult:
    main_result: CalculationResult
    temperature_analysis: list[TemperatureAnalysisPoint]
    load_distribution: list[LoadDistributionPoint]
    optimal_blocks: LoadDistributionPoint
    condenser_vacuum_optimization: CondenserVacuumOptimizationResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "main_result": self.main_result.to_dict(),
            "temperature_analysis": [p.to_dict() for p in self.temperature_analysis],
            "load_distribution": [p.to_dict() for p in self.load_distribution],
            "optimal_blocks": self.optimal_blocks.to_dict(),
            "condenser_vacuum_optimization": self.condenser_vacuum_optimization.to_dict(),
        }


__all__ = ['CalculationInput', 'CalculationResult', 'TemperatureAnalysisPoint', 'LoadDistributionPoint', 'CondenserVacuumPoint', 'CondenserVacuumOptimizationResult', 'FullCalculationResult', 'OperationMode', 'Role', 'UserRole']
