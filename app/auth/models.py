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
        role_value = self.role.value if isinstance(self.role, UserRole) else str(self.role)
        return role_value == UserRole.ADMIN.value


@dataclass(frozen=True)
class LoginResult:
    user: AuthenticatedUser
    session_token: str
    must_change_password: bool


__all__ = ['AuthenticatedUser', 'LoginResult']
