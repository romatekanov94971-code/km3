from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import timedelta
from pathlib import Path

from app.audit.logger import audit_event
from app.auth.models import AuthenticatedUser, LoginResult
from app.auth.password_policy import validate_password
from app.auth.session_manager import session_manager
from app.common.exceptions import AccountLockedError, AuthenticationError, RepositoryError, ValidationError
from app.common.utils import parse_iso_datetime, utcnow, utcnow_iso
from app.storage.repositories import UserRecord, UserRepository
from app.server.config import get_settings

_ITERATIONS = 210_000


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        calculated = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations)
        ).hex()
        return hmac.compare_digest(calculated, digest)
    except Exception:
        return False


def to_authenticated_user(record: UserRecord) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=record.id,
        username=record.username,
        role=record.role,
        must_change_password=record.must_change_password,
    )


class AuthService:
    def __init__(self, users: UserRepository | None = None) -> None:
        self.users = users or UserRepository()

    def _generate_initial_admin_password(self) -> str:
        """Генерирует первичный пароль, соответствующий политике администратора."""
        return f"{secrets.token_urlsafe(14)}Aa1!"

    def _get_initial_admin_password(self) -> tuple[str, str]:
        """Возвращает первичный пароль администратора и источник получения.

        Пароль не хранится в коде и не подставляется в UI:
        1) можно задать ENERGY_DEFAULT_ADMIN_PASSWORD;
        2) иначе пароль генерируется и сохраняется в локальный файл первичных учетных данных.
        """
        settings = get_settings()
        if settings.default_admin_password:
            validate_password(settings.default_admin_username, settings.default_admin_password, "admin")
            return settings.default_admin_password, "environment"

        credentials_path = Path(settings.initial_admin_credentials_file)
        if credentials_path.exists():
            for line in credentials_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("password="):
                    password = line.split("=", 1)[1].strip()
                    validate_password(settings.default_admin_username, password, "admin")
                    return password, str(credentials_path)

        password = self._generate_initial_admin_password()
        validate_password(settings.default_admin_username, password, "admin")
        credentials_path.parent.mkdir(parents=True, exist_ok=True)
        credentials_path.write_text(
            "Initial administrator credentials\n"
            f"username={settings.default_admin_username}\n"
            f"password={password}\n"
            "Change this password immediately after first login.\n",
            encoding="utf-8",
        )
        try:
            credentials_path.chmod(0o600)
        except OSError:
            pass
        return password, str(credentials_path)

    def ensure_default_admin(self) -> None:
        """Создает первичного администратора без захардкоженного пароля."""
        settings = get_settings()
        username = settings.default_admin_username
        if self.users.get_by_username(username) is None:
            password, source = self._get_initial_admin_password()
            self.users.create_user(
                username=username,
                password_hash=hash_password(password),
                role="admin",
                must_change_password=True,
            )
            audit_event(
                event_name="default_admin_created",
                component="auth",
                event_type="admin_action",
                subject="system",
                details={"username": username, "password_source": source},
            )

    def create_user(self, username: str, password: str, role: str = "user", must_change_password: bool = True) -> UserRecord:
        if role not in {"user", "admin"}:
            raise ValidationError("Роль должна быть user или admin.")
        if self.users.get_by_username(username):
            raise ValidationError("Пользователь с таким именем уже существует.")
        validate_password(username, password, role)
        user = self.users.create_user(username, hash_password(password), role, must_change_password)
        audit_event(
            event_name="user_created",
            component="auth",
            event_type="admin_action",
            subject=username,
            details={"role": role},
        )
        return user

    def login(self, username: str, password: str, headers: dict | None = None) -> LoginResult:
        user = self.users.get_by_username(username)
        if not user or not user.is_active:
            audit_event(
                event_name="login_failed",
                component="auth",
                event_type="auth",
                subject=username,
                headers=headers,
                details={"reason": "unknown_or_inactive_user"},
            )
            raise AuthenticationError("Неверный идентификатор или пароль.")

        locked_until = parse_iso_datetime(user.locked_until)
        if locked_until and locked_until > utcnow():
            audit_event(
                event_name="login_blocked_locked_account",
                component="auth",
                event_type="auth",
                subject=username,
                headers=headers,
                details={"locked_until": user.locked_until},
            )
            minutes = get_settings().auth_lock_minutes
            raise AccountLockedError(f"Учетная запись заблокирована. Автоматическая разблокировка через {minutes} минут.")

        if not verify_password(password, user.password_hash):
            settings = get_settings()
            attempts = user.failed_attempts + 1
            locked_iso = None
            if attempts >= settings.auth_max_failed_attempts:
                locked_iso = (utcnow() + timedelta(minutes=settings.auth_lock_minutes)).isoformat()
            self.users.set_failed_attempts(user.id, attempts, locked_iso)
            audit_event(
                event_name="login_failed",
                component="auth",
                event_type="auth",
                subject=username,
                headers=headers,
                details={"reason": "bad_password", "failed_attempts": attempts, "locked_until": locked_iso},
            )
            raise AuthenticationError("Неверный идентификатор или пароль.")

        self.users.reset_failed_attempts(user.id)
        authed = to_authenticated_user(user)
        token = session_manager.create_session(authed)
        audit_event(
            event_name="login_success",
            component="auth",
            event_type="auth",
            subject=username,
            headers=headers,
        )
        return LoginResult(user=authed, session_token=token, must_change_password=user.must_change_password)


    def change_user_role(self, username: str, new_role: str, admin_username: str) -> UserRecord:
        if new_role not in {"user", "admin"}:
            raise ValidationError("Роль должна быть user или admin.")
        record = self.users.get_by_username(username)
        if record is None:
            raise ValidationError("Пользователь не найден.")
        self.users.update_role(record.id, new_role)
        updated = self.users.get_by_id(record.id)
        if updated is None:
            raise RepositoryError("Не удалось прочитать пользователя после изменения роли.")
        audit_event(
            event_name="user_role_changed",
            component="auth",
            event_type="admin_action",
            subject=admin_username,
            details={"target_username": username, "old_role": record.role, "new_role": new_role},
        )
        return updated

    def logout(self, token: str | None, username: str | None = None) -> None:
        session_manager.revoke(token)
        audit_event(event_name="logout", component="auth", event_type="auth", subject=username)

    def change_password(self, user: AuthenticatedUser, old_password: str, new_password: str) -> None:
        record = self.users.get_by_id(user.id)
        if record is None:
            raise AuthenticationError("Пользователь не найден.")
        if not verify_password(old_password, record.password_hash):
            audit_event(
                event_name="password_change_failed",
                component="auth",
                event_type="auth",
                subject=user.username,
                details={"reason": "bad_old_password"},
            )
            raise AuthenticationError("Старый пароль указан неверно.")
        validate_password(record.username, new_password, record.role)
        self.users.update_password(record.id, hash_password(new_password), must_change_password=False)
        audit_event(event_name="password_changed", component="auth", event_type="auth", subject=user.username)



__all__ = ['AuthService', 'hash_password', 'to_authenticated_user', 'verify_password']
