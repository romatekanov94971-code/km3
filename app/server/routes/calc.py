from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.audit.logger import audit_event
from app.auth.models import AuthenticatedUser
from app.calculation.core import calc_tes_efficiency
from app.calculation.optimization import analyze_temperature, optimize_condenser_vacuum
from app.calculation.orchestrator import run_full_calculation
from app.common.exceptions import ValidationError
from app.common.schemas import CalculationInput
from app.reporting.export_csv import export_full_result_to_csv
from app.reporting.export_pptx import export_full_result_to_pptx
from app.server.dependencies import get_admin_user, get_current_user
from app.storage.repositories import AuditRepository, CalculationRepository

router = APIRouter(prefix="/calc", tags=["calculation"])


class CalculationRequest(BaseModel):
    total_load: float = Field(gt=0, description="Общая нагрузка ТЭС, МВт")
    num_blocks: int = Field(gt=0, description="Количество работающих блоков")
    nominal_power_per_block: float = Field(gt=0, description="Номинальная мощность блока, МВт")
    nominal_efficiency: float = Field(gt=0, lt=1, description="Номинальный КПД блока, доля")
    temp_c: float = Field(description="Температура наружного воздуха, °C")
    humidity: float = Field(ge=0, le=100, description="Влажность, %")
    wind_speed: float = Field(ge=0, description="Скорость ветра, м/с")
    wind_dir: float = Field(ge=0, le=360, description="Направление ветра, градусы")
    own_needs_coeff: float = Field(default=0.05, ge=0, lt=0.5)
    beta: float = Field(default=0.4, ge=0)
    condenser_vacuum_kpa: float | None = Field(default=None)

    def to_input(self) -> CalculationInput:
        return CalculationInput(**self.model_dump())


@router.post("/run")
def run_calculation(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    try:
        result = run_full_calculation(payload.to_input())
        result_dict = result.to_dict()
        record_id = CalculationRepository().create(user.id, payload.model_dump(), result_dict)
        audit_event(
            event_name="calculation_run",
            component="calculation_orchestrator",
            event_type="calculation",
            subject=user.username,
            details={"history_id": record_id},
        )
        return {"history_id": record_id, **result_dict}
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/main")
def run_main_only(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    try:
        result = calc_tes_efficiency(payload.to_input()).to_dict()
        audit_event("main_calculation_run", "math_core", "calculation", subject=user.username)
        return result
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/temperature-analysis")
def run_temperature_analysis(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> list[dict]:
    points = analyze_temperature(payload.to_input())
    audit_event("temperature_analysis_run", "math_core", "calculation", subject=user.username)
    return [point.to_dict() for point in points]


@router.post("/optimize-vacuum")
def run_vacuum_optimization(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = optimize_condenser_vacuum(payload.to_input()).to_dict()
    audit_event("condenser_vacuum_optimized", "math_core", "calculation", subject=user.username)
    return result


@router.get("/history")
def history(limit: int = Query(default=50, ge=1, le=500), user: AuthenticatedUser = Depends(get_current_user)) -> list[dict]:
    return CalculationRepository().list_for_user(user.id, limit=limit)


@router.get("/audit")
def audit(limit: int = Query(default=100, ge=1, le=1000), admin: AuthenticatedUser = Depends(get_admin_user)) -> list[dict]:
    return AuditRepository().list_events(limit=limit)


@router.post("/export/csv")
def export_csv(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = run_full_calculation(payload.to_input())
    path = export_full_result_to_csv(result, directory="exports")
    audit_event("csv_export_created", "reporting", "export", subject=user.username, details={"path": str(path)})
    return {"path": str(path)}


@router.post("/export/pptx")
def export_pptx(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = run_full_calculation(payload.to_input())
    path = export_full_result_to_pptx(result, directory="exports")
    audit_event("pptx_export_created", "reporting", "export", subject=user.username, details={"path": str(path)})
    return {"path": str(path)}
