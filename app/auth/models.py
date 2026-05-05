from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: str
    must_change_password: bool = False

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@dataclass(frozen=True)
class LoginResult:
    user: AuthenticatedUser
    session_token: str
    must_change_password: bool


__all__ = ['AuthenticatedUser', 'LoginResult']
