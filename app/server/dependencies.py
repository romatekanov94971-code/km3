from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from app.auth.models import AuthenticatedUser
from app.auth.service import AuthService
from app.auth.session_manager import session_manager
from app.server.config import get_settings

# Учебный in-memory rate limit. Важно: ограничение работает per-process.
# При запуске нескольких процессов Uvicorn/Gunicorn для production лучше
# перенести bucket-и в Redis или другой общий storage.
_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = _BUCKETS[client_host]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Слишком много запросов.")
    bucket.append(now)


def _extract_token(authorization: str | None, x_session_token: str | None) -> str | None:
    if x_session_token:
        return x_session_token
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_session_token: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    token = _extract_token(authorization, x_session_token)
    user = session_manager.get_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется аутентификация.")
    return user


def get_admin_user(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора.")
    return user


def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
    x_session_token: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser | None:
    return session_manager.get_user(_extract_token(authorization, x_session_token))


def get_auth_service() -> AuthService:
    """Создает AuthService для текущего запроса.

    UserRepository не имеет состояния приложения и открывает соединения с БД
    внутри операций. SessionManager при этом остается глобальным singleton в
    app.auth.session_manager, поэтому сессии сохраняются между запросами.
    """
    return AuthService()


__all__ = [
    "get_admin_user",
    "get_auth_service",
    "get_current_user",
    "get_optional_user",
    "rate_limit",
]
