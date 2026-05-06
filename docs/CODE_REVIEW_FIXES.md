# Исправления по последнему code review

Закрыты рекомендации из раздела "6. Рекомендации к исправлению (приоритет)" последнего ревью.

| Приоритет | Файл | Исправление |
|---|---|---|
| Критический | `app/auth/password_policy.py` | `_SPECIAL_RE` заменен на явный whitelist спецсимволов, пробелы запрещены. |
| Критический | `app/audit/remote.py`, `app/audit/logger.py` | Удаленная отправка аудита перенесена в неблокирующую очередь с daemon worker. |
| Критический | `app/client/main_window.py` | Добавлен `closeEvent()` с вызовом `api.logout()`. |
| Высокий | `app/audit/logger.py` | В файловый audit log добавлен `sequence_number` из SQLite. |
| Высокий | `app/storage/database.py` | Добавлены `PRAGMA journal_mode = WAL` и `PRAGMA busy_timeout = 5000`. |
| Средний | `app/common/schemas.py` | Добавлен enum `UserRole`; `Role` оставлен как совместимый alias. |
| Средний | `app/client/api_client.py` | Клиент разделен на `AuthApiClient`, `CalcApiClient`, `AuditApiClient`, `ExportApiClient`. |
| Средний | `docs/presentation/architecture_overview.pptx` | Добавлена таблица сетевых портов и протоколов. |
| Низкий | `app/server/schemas.py` | Для `temp_c` добавлено `Field(ge=-60, le=60)`. |
| Низкий | `README.md`, `docs/ARCHITECTURE.md` | Задокументировано ограничение in-memory SessionManager. |

Проверка:

```bash
PYTHONPATH=. pytest -q
# 41 passed
```
