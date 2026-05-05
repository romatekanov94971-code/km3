class EnergySystemError(Exception):
    """Базовое исключение программного комплекса."""


class ValidationError(EnergySystemError):
    """Ошибка проверки входных параметров."""


class AuthenticationError(EnergySystemError):
    """Ошибка аутентификации."""


class AuthorizationError(EnergySystemError):
    """Ошибка авторизации."""


class AccountLockedError(AuthenticationError):
    """Учетная запись временно заблокирована."""


class RepositoryError(EnergySystemError):
    """Ошибка работы с хранилищем данных."""


__all__ = ['EnergySystemError', 'ValidationError', 'AuthenticationError', 'AuthorizationError', 'AccountLockedError', 'RepositoryError']
