from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from app.common.utils import utcnow_iso
from app.storage.database import session


@dataclass(frozen=True)
class UserRecord:
    id: int
    username: str
    password_hash: str
    role: str
    must_change_password: bool
    failed_attempts: int
    locked_until: str | None
    is_active: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "UserRecord":
        return cls(
            id=int(row["id"]),
            username=str(row["username"]),
            password_hash=str(row["password_hash"]),
            role=str(row["role"]),
            must_change_password=bool(row["must_change_password"]),
            failed_attempts=int(row["failed_attempts"]),
            locked_until=row["locked_until"],
            is_active=bool(row["is_active"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )


class UserRepository:
    def get_by_username(self, username: str) -> UserRecord | None:
        with session() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return UserRecord.from_row(row) if row else None

    def get_by_id(self, user_id: int) -> UserRecord | None:
        with session() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return UserRecord.from_row(row) if row else None

    def create_user(
        self,
        username: str,
        password_hash: str,
        role: str = "user",
        must_change_password: bool = True,
    ) -> UserRecord:
        now = utcnow_iso()
        with session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users(username, password_hash, role, must_change_password, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, password_hash, role, int(must_change_password), now, now),
            )
            user_id = int(cursor.lastrowid)
        user = self.get_by_id(user_id)
        assert user is not None
        return user

    def update_password(self, user_id: int, password_hash: str, must_change_password: bool = False) -> None:
        with session() as conn:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, must_change_password = ?, failed_attempts = 0,
                    locked_until = NULL, updated_at = ?
                WHERE id = ?
                """,
                (password_hash, int(must_change_password), utcnow_iso(), user_id),
            )

    def set_failed_attempts(self, user_id: int, failed_attempts: int, locked_until: str | None) -> None:
        with session() as conn:
            conn.execute(
                """
                UPDATE users SET failed_attempts = ?, locked_until = ?, updated_at = ? WHERE id = ?
                """,
                (failed_attempts, locked_until, utcnow_iso(), user_id),
            )

    def reset_failed_attempts(self, user_id: int) -> None:
        self.set_failed_attempts(user_id, 0, None)

    def list_users(self) -> list[UserRecord]:
        with session() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY username").fetchall()
            return [UserRecord.from_row(row) for row in rows]


class CalculationRepository:
    def create(self, user_id: int | None, input_data: dict[str, Any], result_data: dict[str, Any]) -> int:
        with session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO calculation_history(user_id, input_json, result_json, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, json.dumps(input_data, ensure_ascii=False), json.dumps(result_data, ensure_ascii=False), utcnow_iso()),
            )
            return int(cursor.lastrowid)

    def list_for_user(self, user_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        with session() as conn:
            if user_id is None:
                rows = conn.execute(
                    "SELECT * FROM calculation_history ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM calculation_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "input": json.loads(row["input_json"]),
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]


class AuditRepository:
    def create(
        self,
        event_name: str,
        component: str,
        event_type: str,
        event_id: str,
        subject: str | None = None,
        headers: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
        event_time: str | None = None,
    ) -> int:
        with session() as conn:
            cursor = conn.execute(
                """
                INSERT INTO audit_events(
                    event_time, event_name, component, subject, headers_json,
                    event_type, event_id, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_time or utcnow_iso(),
                    event_name,
                    component,
                    subject,
                    json.dumps(headers or {}, ensure_ascii=False),
                    event_type,
                    event_id,
                    json.dumps(details or {}, ensure_ascii=False),
                ),
            )
            return int(cursor.lastrowid)

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 1000))
        with session() as conn:
            rows = conn.execute("SELECT * FROM audit_events ORDER BY event_time DESC LIMIT ?", (limit,)).fetchall()
        return [
            {
                "id": row["id"],
                "event_time": row["event_time"],
                "event_name": row["event_name"],
                "component": row["component"],
                "subject": row["subject"],
                "headers": json.loads(row["headers_json"] or "{}"),
                "event_type": row["event_type"],
                "event_id": row["event_id"],
                "details": json.loads(row["details_json"] or "{}"),
            }
            for row in rows
        ]

    def delete_older_than(self, cutoff_iso: str) -> int:
        with session() as conn:
            cursor = conn.execute("DELETE FROM audit_events WHERE event_time < ?", (cutoff_iso,))
            return int(cursor.rowcount)
