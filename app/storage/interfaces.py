from __future__ import annotations

from typing import Protocol

from app.storage.repositories import UserRecord


class IUserRepository(Protocol):
    """Минимальный интерфейс хранилища пользователей для AuthService."""

    def get_by_username(self, username: str) -> UserRecord | None:
        ...

    def get_by_id(self, user_id: int) -> UserRecord | None:
        ...

    def create_user(
        self,
        username: str,
        password_hash: str,
        role: str = "user",
        must_change_password: bool = True,
    ) -> UserRecord:
        ...

    def update_password(self, user_id: int, password_hash: str, must_change_password: bool = False) -> None:
        ...

    def set_failed_attempts(self, user_id: int, failed_attempts: int, locked_until: str | None) -> None:
        ...

    def reset_failed_attempts(self, user_id: int) -> None:
        ...

    def update_role(self, user_id: int, role: str) -> None:
        ...

    def list_users(self) -> list[UserRecord]:
        ...


__all__ = ["IUserRepository"]
