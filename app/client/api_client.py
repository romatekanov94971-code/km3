from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
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

    def login(self, username: str, password: str) -> dict[str, Any]:
        data = self._request("POST", "/auth/login", {"username": username, "password": password})
        self.token = data["token"]
        return data

    def change_password(self, old_password: str, new_password: str) -> dict[str, Any]:
        return self._request("POST", "/auth/change-password", {"old_password": old_password, "new_password": new_password})

    def run_calculation(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/calc/run", payload)

    def export_csv(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/calc/export/csv", payload)

    def export_pptx(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/calc/export/pptx", payload)
