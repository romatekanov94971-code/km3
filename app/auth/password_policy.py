from __future__ import annotations

import re

from app.common.exceptions import ValidationError
from app.server.config import get_settings

_SPECIAL_RE = re.compile(r"[^A-Za-zА-Яа-яЁё0-9]")


def validate_password(username: str, password: str, role: str = "user") -> None:
    """Проверка пароля по настраиваемой политике ТЗ для пользователей и администраторов."""
    settings = get_settings()
    min_len = settings.auth_admin_min_password_length if role == "admin" else settings.auth_user_min_password_length

    if len(password) < min_len:
        raise ValidationError(f"Пароль для роли {role} должен быть не короче {min_len} символов.")

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
        raise ValidationError("Пароль должен содержать спецсимвол.")


__all__ = ['validate_password']
