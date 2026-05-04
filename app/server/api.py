from __future__ import annotations

import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.audit.logger import audit_event
from app.auth.service import auth_service
from app.common.exceptions import EnergySystemError
from app.server.config import ensure_runtime_dirs, get_settings
from app.server.dependencies import rate_limit
from app.server.routes import auth, calc
from app.storage.database import init_db

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Программный комплекс для оценки эффективности энергооборудования ТЭС.",
    dependencies=[Depends(rate_limit)],
)


@app.on_event("startup")
def on_startup() -> None:
    ensure_runtime_dirs()
    init_db()
    auth_service.ensure_default_admin()
    audit_event("api_started", "api", "system", subject="system")


@app.middleware("http")
async def audit_api_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    audit_event(
        event_name="api_request",
        component="api",
        event_type="api",
        subject=None,
        headers=dict(request.headers),
        details={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
        },
    )
    return response


@app.exception_handler(EnergySystemError)
async def energy_system_exception_handler(request: Request, exc: EnergySystemError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


app.include_router(auth.router)
app.include_router(calc.router)
