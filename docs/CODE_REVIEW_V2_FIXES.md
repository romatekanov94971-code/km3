# Исправления по code review v2

Закрыты пункты из таблицы действий повторного ревью.

| Приоритет | Файл | Исправление |
|---|---|---|
| Критический | `app/auth/models.py` | `is_admin` теперь безопасно сравнивает `role.value` / `str(role)` с `UserRole.ADMIN.value`; `ValueError` на Python 3.12 исключен. |
| Высокий | `app/audit/event_models.py` | Удалено мертвое поле `remote_sent`; актуальное поле — `remote_queued`. |
| Средний | `app/client/main_window.py` | Добавлены `_do_logout()` и `_do_logout_and_close()`; меню «Выйти» вызывает logout явно, `closeEvent()` переиспользует общий метод. |
| Низкий | `app/audit/logger.py` | `audit_event()` декомпозирован на sink-объекты: SQLite, remote queue, file sink. |
| Низкий | `app/storage/interfaces.py`, `app/auth/service.py` | Добавлен протокол `IUserRepository`; `AuthService` зависит от интерфейса, а не от конкретного класса. |

Проверка:

```bash
PYTHONPATH=. pytest -q
# 46 passed
```
