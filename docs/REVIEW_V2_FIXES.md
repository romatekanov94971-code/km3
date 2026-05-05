# Исправления по review v2

## Новые проблемы из review v2

| Замечание | Исправление |
|---|---|
| `SessionManager.cleanup()` повторно захватывает `RLock` из `create_session()`/`get_user()` | Добавлен внутренний `_cleanup_unsafe()`, публичный `cleanup()` сам берет lock, внутренние вызовы используют `_cleanup_unsafe()`. |
| `audit_event()` создает `AuditEvent` дважды | Используется `dataclasses.replace(event, remote_sent=remote_sent)`. |
| Комментарий в `get_auth_service()` вводит в заблуждение | Комментарий уточнен: `AuthService` создается на запрос, `UserRepository` без состояния приложения, `SessionManager` — singleton. |
| Остался `global _LOGGER` | Удален `_LOGGER`; используется кэш `logging.getLogger("energy_system.audit")`, handler пересоздается при смене пути журнала. |

## Старые незакрытые замечания

| Замечание | Исправление |
|---|---|
| `__all__` в публичных модулях | Добавлены `__all__` в ключевые публичные модули. |
| Маппинг `CalculationRequest -> CalculationInput` внутри Pydantic-модели | DTO вынесена в `app/server/schemas.py`, маппинг — в `app/server/mappers.py`. |
| Комментарий про ограничения rate limiting | Добавлен комментарий, что текущий rate limit является in-memory per-process. |
| `@app.on_event("startup")` deprecated | Заменено на FastAPI `lifespan`. |
| GUI показывает серверный путь CSV/PPTX | GUI показывает только имя файла и пояснение про каталог `exports` серверной части. |
| `pyproject.toml` для pytest | Добавлен `pyproject.toml` с `pythonpath` и `testpaths`. |

## Проверка

```bash
PYTHONPATH=. pytest -q
# 30 passed
```


## Оставшиеся замечания после v3

| Замечание | Исправление |
|---|---|
| `get_audit_logger()` проверял только `handlers[0]` | Теперь ищется подходящий `RotatingFileHandler` по `baseFilename`, чужие handlers не удаляются; удаляются только handlers, помеченные `_energy_system_audit_handler`. |
| `lifespan` вызывал `get_auth_service()` напрямую | В `lifespan` используется явный `AuthService().ensure_default_admin()`, без имитации DI-контекста. |
| `__all__` в `app/auth/service.py` экспортировал приватные helpers | Теперь публичный экспорт модуля: `__all__ = ["AuthService"]`. |

## Проверка после финальных мелких правок

```bash
PYTHONPATH=. pytest -q
# 33 passed
```
