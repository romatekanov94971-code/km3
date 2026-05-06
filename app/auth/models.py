from __future__ import annotations

from dataclasses import dataclass

from app.common.schemas import UserRole


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: UserRole | str
    must_change_password: bool = False

    @property
    def is_admin(self) -> bool:
        return UserRole(str(self.role)) is UserRole.ADMIN


@dataclass(frozen=True)
class LoginResult:
    user: AuthenticatedUser
    session_token: str
    must_change_password: bool


__all__ = ['AuthenticatedUser', 'LoginResult']
