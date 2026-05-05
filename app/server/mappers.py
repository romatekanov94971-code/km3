from __future__ import annotations

from app.common.schemas import CalculationInput
from app.server.schemas import CalculationRequest


def calculation_request_to_input(payload: CalculationRequest) -> CalculationInput:
    """Маппинг API DTO в доменную модель расчетного ядра.

    Вынесено из Pydantic-модели, чтобы серверная DTO-схема не знала о внутренней
    dataclass-модели расчетного слоя.
    """
    return CalculationInput(**payload.model_dump())


__all__ = ["calculation_request_to_input"]
