from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.common.schemas import OperationMode


class CalculationRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    total_load: float = Field(gt=0, description="Общая нагрузка ТЭС, МВт")
    num_blocks: int = Field(gt=0, description="Количество работающих блоков")
    nominal_power_per_block: float = Field(gt=0, description="Номинальная мощность блока, МВт")
    nominal_efficiency: float = Field(gt=0, lt=1, description="Номинальный КПД блока, доля")
    temp_c: float = Field(ge=-60, le=60, description="Температура наружного воздуха, °C")
    humidity: float = Field(ge=0, le=100, description="Влажность, %")
    wind_speed: float = Field(ge=0, description="Скорость ветра, м/с")
    wind_dir: float = Field(ge=0, le=360, description="Направление ветра, градусы")
    own_needs_coeff: float = Field(default=0.05, ge=0, lt=0.5)
    beta: float = Field(default=0.4, ge=0)
    condenser_vacuum_kpa: float | None = Field(default=None)
    operation_mode: OperationMode = Field(default=OperationMode.AUTO, description="Режим работы: auto/winter/summer")


__all__ = ["CalculationRequest"]
