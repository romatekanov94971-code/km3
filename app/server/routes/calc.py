from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.audit.logger import audit_event
from app.auth.models import AuthenticatedUser
from app.calculation.core import calc_tes_efficiency
from app.calculation.optimization import analyze_temperature, optimize_condenser_vacuum
from app.calculation.orchestrator import run_full_calculation
from app.common.exceptions import ValidationError
from app.reporting.export_csv import export_full_result_to_csv
from app.reporting.export_pptx import export_full_result_to_pptx
from app.audit.retention import cleanup_old_audit_events
from app.server.dependencies import get_admin_user, get_current_user
from app.server.mappers import calculation_request_to_input
from app.server.schemas import CalculationRequest
from app.storage.repositories import AuditRepository, CalculationRepository

router = APIRouter(prefix="/calc", tags=["calculation"])



@router.post("/run")
def run_calculation(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    try:
        result = run_full_calculation(calculation_request_to_input(payload))
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
        result = calc_tes_efficiency(calculation_request_to_input(payload)).to_dict()
        audit_event("main_calculation_run", "math_core", "calculation", subject=user.username)
        return result
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/temperature-analysis")
def run_temperature_analysis(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> list[dict]:
    points = analyze_temperature(calculation_request_to_input(payload))
    audit_event("temperature_analysis_run", "math_core", "calculation", subject=user.username)
    return [point.to_dict() for point in points]


@router.post("/optimize-vacuum")
def run_vacuum_optimization(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = optimize_condenser_vacuum(calculation_request_to_input(payload)).to_dict()
    audit_event("condenser_vacuum_optimized", "math_core", "calculation", subject=user.username)
    return result


@router.get("/history")
def history(limit: int = Query(default=50, ge=1, le=500), user: AuthenticatedUser = Depends(get_current_user)) -> list[dict]:
    return CalculationRepository().list_for_user(user.id, limit=limit)


@router.get("/audit")
def audit(limit: int = Query(default=100, ge=1, le=1000), admin: AuthenticatedUser = Depends(get_admin_user)) -> list[dict]:
    return AuditRepository().list_events(limit=limit)


@router.post("/audit/cleanup")
def audit_cleanup(
    retention_days: int | None = Query(default=None, ge=1, le=3650),
    admin: AuthenticatedUser = Depends(get_admin_user),
) -> dict:
    deleted = cleanup_old_audit_events(retention_days)
    audit_event(
        "audit_cleanup_run",
        "audit",
        "admin_action",
        subject=admin.username,
        details={"retention_days": retention_days, "deleted": deleted},
    )
    return {"deleted": deleted, "retention_days": retention_days}


@router.post("/export/csv")
def export_csv(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = run_full_calculation(calculation_request_to_input(payload))
    path = export_full_result_to_csv(result, directory="exports")
    audit_event("csv_export_created", "reporting", "export", subject=user.username, details={"path": str(path)})
    return {"status": "created", "filename": path.name}


@router.post("/export/pptx")
def export_pptx(payload: CalculationRequest, user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    result = run_full_calculation(calculation_request_to_input(payload))
    path = export_full_result_to_pptx(result, directory="exports")
    audit_event("pptx_export_created", "reporting", "export", subject=user.username, details={"path": str(path)})
    return {"status": "created", "filename": path.name}


__all__ = ["router"]
