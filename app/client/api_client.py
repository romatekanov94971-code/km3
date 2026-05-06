from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class HttpApiClient:
    """Базовый HTTP-клиент с авторизационным токеном."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("ENERGY_API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.token: str | None = None
        self.current_user: dict[str, Any] | None = None

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", str(exc))
            except Exception:
                detail = str(exc)
            raise RuntimeError(detail) from exc


class AuthApiClient:
    def __init__(self, http: HttpApiClient) -> None:
        self.http = http

    def login(self, username: str, password: str) -> dict[str, Any]:
        data = self.http.request("POST", "/auth/login", {"username": username, "password": password})
        self.http.token = data["token"]
        self.http.current_user = data.get("user")
        return data

    def logout(self) -> dict[str, Any] | None:
        try:
            result = self.http.request("POST", "/auth/logout")
        finally:
            self.http.token = None
            self.http.current_user = None
        return result

    def change_password(self, old_password: str, new_password: str) -> dict[str, Any]:
        return self.http.request("POST", "/auth/change-password", {"old_password": old_password, "new_password": new_password})

    def create_user(self, username: str, password: str, role: str = "user", must_change_password: bool = True) -> dict[str, Any]:
        return self.http.request(
            "POST",
            "/auth/users",
            {
                "username": username,
                "password": password,
                "role": role,
                "must_change_password": must_change_password,
            },
        )

    def get_auth_policy(self) -> dict[str, Any]:
        return self.http.request("GET", "/auth/policy")

    def change_user_role(self, username: str, role: str) -> dict[str, Any]:
        return self.http.request("PATCH", f"/auth/users/{username}/role", {"role": role})


class CalcApiClient:
    def __init__(self, http: HttpApiClient) -> None:
        self.http = http

    def run_calculation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.http.request("POST", "/calc/run", payload)

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.http.request("GET", f"/calc/history?limit={limit}")


class AuditApiClient:
    def __init__(self, http: HttpApiClient) -> None:
        self.http = http

    def get_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.http.request("GET", f"/calc/audit?limit={limit}")

    def cleanup_audit(self, retention_days: int | None = None) -> dict[str, Any]:
        query = "" if retention_days is None else f"?retention_days={retention_days}"
        return self.http.request("POST", f"/calc/audit/cleanup{query}")


class ExportApiClient:
    def __init__(self, http: HttpApiClient) -> None:
        self.http = http

    def export_csv(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.http.request("POST", "/calc/export/csv", payload)

    def export_pptx(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.http.request("POST", "/calc/export/pptx", payload)


class ApiClient:
    """Фасад для существующих GUI-окон.

    Внутри разделен на узкие клиенты Auth/Calc/Audit/Export, чтобы окна могли
    быть постепенно переведены на специализированные интерфейсы без поломки GUI.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.http = HttpApiClient(base_url)
        self.auth = AuthApiClient(self.http)
        self.calc = CalcApiClient(self.http)
        self.audit = AuditApiClient(self.http)
        self.export = ExportApiClient(self.http)

    @property
    def token(self) -> str | None:
        return self.http.token

    @property
    def current_user(self) -> dict[str, Any] | None:
        return self.http.current_user

    @property
    def username(self) -> str:
        if not self.current_user:
            return ""
        return str(self.current_user.get("username", ""))

    @property
    def role(self) -> str:
        if not self.current_user:
            return ""
        return str(self.current_user.get("role", ""))

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def login(self, username: str, password: str) -> dict[str, Any]:
        return self.auth.login(username, password)

    def logout(self) -> dict[str, Any] | None:
        return self.auth.logout()

    def change_password(self, old_password: str, new_password: str) -> dict[str, Any]:
        return self.auth.change_password(old_password, new_password)

    def create_user(self, username: str, password: str, role: str = "user", must_change_password: bool = True) -> dict[str, Any]:
        return self.auth.create_user(username, password, role, must_change_password)

    def get_auth_policy(self) -> dict[str, Any]:
        return self.auth.get_auth_policy()

    def change_user_role(self, username: str, role: str) -> dict[str, Any]:
        return self.auth.change_user_role(username, role)

    def run_calculation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.calc.run_calculation(payload)

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.calc.get_history(limit)

    def get_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.audit.get_audit_events(limit)

    def cleanup_audit(self, retention_days: int | None = None) -> dict[str, Any]:
        return self.audit.cleanup_audit(retention_days)

    def export_csv(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.export.export_csv(payload)

    def export_pptx(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.export.export_pptx(payload)


__all__ = ["ApiClient", "AuditApiClient", "AuthApiClient", "CalcApiClient", "ExportApiClient", "HttpApiClient"]
