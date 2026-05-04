from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import timedelta

from app.auth.models import AuthenticatedUser
from app.common.utils import utcnow


@dataclass
class Session:
    token: str
    user: AuthenticatedUser
    expires_at: float


class SessionManager:
    """Простой in-memory менеджер сессий для учебного API."""

    def __init__(self, ttl_minutes: int = 120) -> None:
        self.ttl = timedelta(minutes=ttl_minutes)
        self._sessions: dict[str, Session] = {}

    def create_session(self, user: AuthenticatedUser) -> str:
        self.cleanup()
        token = secrets.token_urlsafe(32)
        expires_at = (utcnow() + self.ttl).timestamp()
        self._sessions[token] = Session(token=token, user=user, expires_at=expires_at)
        return token

    def get_user(self, token: str | None) -> AuthenticatedUser | None:
        if not token:
            return None
        self.cleanup()
        session = self._sessions.get(token)
        if not session:
            return None
        return session.user

    def revoke(self, token: str | None) -> None:
        if token:
            self._sessions.pop(token, None)

    def cleanup(self) -> None:
        now_ts = utcnow().timestamp()
        expired = [token for token, session in self._sessions.items() if session.expires_at < now_ts]
        for token in expired:
            self._sessions.pop(token, None)


session_manager = SessionManager()
