from __future__ import annotations

import re

from app.common.exceptions import ValidationError
from app.common.schemas import UserRole
from app.server.config import get_settings

# Явный whitelist спецсимволов из требований ТЗ и близких к ним символов.
# Пробелы, табуляции, emoji и произвольные unicode-символы не считаются спецсимволами.
_SPECIAL_RE = re.compile(r"[!@#$%^&*()_+\-=\[\]{}|;:',.<>/?`~\\]")
_WHITESPACE_RE = re.compile(r"\s")


def normalize_role(role: str | UserRole) -> UserRole:
    return role if isinstance(role, UserRole) else UserRole(str(role))


def validate_password(username: str, password: str, role: str | UserRole = UserRole.USER) -> None:
    """Проверка пароля по настраиваемой политике ТЗ для пользователей и администраторов."""
    settings = get_settings()
    role_value = normalize_role(role)
    min_len = settings.auth_admin_min_password_length if role_value is UserRole.ADMIN else settings.auth_user_min_password_length

    if len(password) < min_len:
        raise ValidationError(f"Пароль для роли {role_value.value} должен быть не короче {min_len} символов.")

    if _WHITESPACE_RE.search(password):
        raise ValidationError("Пароль не должен содержать пробельные символы.")

    username_lower = username.lower()
    password_lower = password.lower()
    if username_lower and username_lower in password_lower:
        raise ValidationError("Пароль не должен совпадать с идентификатором учетной записи или содержать его.")

    if not any(ch.isupper() for ch in password):
        raise ValidationError("Пароль должен содержать символ в верхнем регистре.")
    if not any(ch.islower() for ch in password):
        raise ValidationError("Пароль должен содержать символ в нижнем регистре.")
    if not any(ch.isdigit() for ch in password):
        raise ValidationError("Пароль должен содержать цифру.")
    if not _SPECIAL_RE.search(password):
        raise ValidationError("Пароль должен содержать спецсимвол из разрешенного набора: !@#$%^&*()_+-=[]{}|;:',.<>/?`~\\")


__all__ = ["normalize_role", "validate_password"]
