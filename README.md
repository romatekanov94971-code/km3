# Energy System

Программный комплекс для оценки эффективности и основных энергетических показателей энергооборудования ТЭС.

## Что реализовано

- математическое ядро на основе исходного ноутбука `Приложение 1.ipynb`;
- учет температуры, влажности, скорости и направления ветра;
- расчет нагрузки на энергоблок, КПД блока, КПД ТЭС брутто, собственных нужд, КПД ТЭС нетто, удельного расхода топлива;
- анализ зависимости теплоотводящей способности от температуры наружного воздуха;
- подбор оптимального количества работающих блоков;
- учебная модель оптимизации разрежения в конденсаторе турбины;
- FastAPI-сервер;
- PyQt6-клиент;
- парольная аутентификация с политикой сложности, блокировкой после трех неудачных попыток и разблокировкой через 15 минут;
- SQLite-хранилище пользователей, истории расчетов и аудита;
- аудит API-запросов, входов/выходов, расчетов, экспорта;
- ротация файловых журналов;
- экспорт CSV и PPTX;
- тесты расчетного ядра, авторизации и хранилища.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Запуск демонстрационного расчета

```bash
python main.py demo
```

## Запуск API

```bash
python main.py api
```

Документация API будет доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

После первого запуска создается первичный администратор.

```text
login: admin
password: см. data/initial_admin_credentials.txt
```

Пароль больше не захардкожен в UI или коде. Перед первым запуском можно задать свой пароль:

```bash
export ENERGY_DEFAULT_ADMIN_PASSWORD='RootSecure1!'
```

Если переменная не задана, система сгенерирует пароль и сохранит его в файле `data/initial_admin_credentials.txt`.

При первом входе GUI автоматически откроет окно смены пароля. После входа сменить пароль можно через меню `Аккаунт -> Сменить пароль`.

Через API смена пароля доступна по маршруту:

```text
POST /auth/change-password
```

Тело запроса:

```json
{"old_password": "<текущий пароль>", "new_password": "NewAdmin1!"}
```

## Запуск GUI

Сначала запустите API в одном терминале:

```bash
python main.py api
```

Затем GUI во втором терминале:

```bash
python main.py gui
```

## Тесты

```bash
PYTHONPATH=. pytest -q
```

Ожидаемый результат: `41 passed`

## Переменные окружения

```text
# API / интеграционные потоки
ENERGY_API_HOST=127.0.0.1
ENERGY_API_PORT=8000
ENERGY_API_BASE_URL=http://127.0.0.1:8000
ENERGY_API_SSL_CERTFILE=
ENERGY_API_SSL_KEYFILE=

# Rate limit
ENERGY_RATE_LIMIT_PER_MINUTE=120

# База данных
ENERGY_DB_PATH=data/energy_system.sqlite3

# Первичный администратор
ENERGY_DEFAULT_ADMIN_USERNAME=admin
ENERGY_DEFAULT_ADMIN_PASSWORD=
ENERGY_INITIAL_ADMIN_CREDENTIALS_FILE=data/initial_admin_credentials.txt

# Настраиваемые параметры аутентификации
ENERGY_AUTH_MAX_FAILED_ATTEMPTS=3
ENERGY_AUTH_LOCK_MINUTES=15
ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH=6
ENERGY_AUTH_ADMIN_MIN_PASSWORD_LENGTH=7

# Аудит
ENERGY_AUDIT_LOG=logs/audit.log
ENERGY_AUDIT_MAX_BYTES=1000000
ENERGY_AUDIT_BACKUPS=5
ENERGY_AUDIT_RETENTION_DAYS=180
ENERGY_AUDIT_DETAIL_LEVEL=standard
ENERGY_AUDIT_REMOTE_URL=
ENERGY_AUDIT_REMOTE_TIMEOUT=3.0
```

## Разделение ролей в GUI

После входа главное окно определяет роль пользователя.

Обычный пользователь видит расчетные функции, графики, экспорт и смену пароля.

Администратор дополнительно видит меню `Администрирование`:

```text
Администрирование
├─ Создать пользователя
├─ Изменить роль пользователя
├─ Политика безопасности
└─ Журнал аудита
```

## Аудит

Журнал аудита хранится в SQLite и в файловом журнале `logs/audit.log`.
Чувствительные заголовки `Authorization`, `Cookie`, `Set-Cookie`, `X-Session-Token` маскируются.

Настройки:

```text
ENERGY_AUDIT_MAX_BYTES=1000000
ENERGY_AUDIT_BACKUPS=5
ENERGY_AUDIT_RETENTION_DAYS=180
ENERGY_AUDIT_REMOTE_URL=
ENERGY_AUDIT_REMOTE_TIMEOUT=3.0
```

Если задан `ENERGY_AUDIT_REMOTE_URL`, события аудита дополнительно отправляются POST-запросом на удаленный сервер сбора.

## UML и презентация

```text
docs/uml/
docs/presentation/architecture_overview.pptx
docs/TZ_CHECKLIST.md
```

## Безопасность интеграционных потоков

Для локальной демонстрации API запускается на `http://127.0.0.1:8000`.
Для сетевого развертывания рекомендуется запускать FastAPI за HTTPS reverse proxy.

## Административные функции GUI

Для роли `admin` доступно меню:

```text
Администрирование
├─ Создать пользователя
├─ Изменить роль пользователя
├─ Политика безопасности
└─ Журнал аудита
```

## Документы для сдачи

```text
docs/TZ_CHECKLIST.md       # детальная сверка с каждым пунктом ТЗ
docs/DEMO_SCRIPT.md        # сценарий демонстрации
docs/uml/                  # PlantUML-диаграммы
docs/presentation/         # архитектура в PPTX
```


## Архитектурные исправления безопасности

В финальной версии устранены замечания ревизии:

- первичный пароль администратора не захардкожен в UI/коде;
- `AuthService` внедряется в FastAPI-роуты через `Depends(get_auth_service)`;
- `AuditEvent` используется как единая модель события аудита;
- `external_factor` рассчитывается один раз и передается в расчет блока;
- `SessionManager` защищен `threading.RLock`;
- магические числа расчетной модели вынесены в `app/calculation/constants.py`;
- `assert` удалены из production-кода и заменены явными исключениями.


## Исправления review v2

Закрыты замечания из ревью `review v2.pdf`:

- `SessionManager.cleanup()` разделен на публичный `cleanup()` и внутренний `_cleanup_unsafe()`;
- `audit_event()` больше не создает `AuditEvent` вручную дважды, используется `dataclasses.replace()`;
- комментарий `get_auth_service()` уточнен: `UserRepository` без состояния приложения, `SessionManager` остается singleton;
- удален `global _LOGGER`, используется кэш `logging.getLogger()`;
- добавлены `__all__` в публичные модули;
- маппинг `CalculationRequest -> CalculationInput` вынесен в `app/server/mappers.py`;
- добавлен комментарий, что rate limit является per-process;
- deprecated `@app.on_event("startup")` заменен на FastAPI `lifespan`;
- GUI больше не показывает серверный путь CSV/PPTX;
- добавлен `pyproject.toml` для pytest.


## Финальные мелкие исправления после v3

Закрыты последние замечания:

- `get_audit_logger()` больше не зависит от `первого handler в logger.handlers`;
- `lifespan` явно вызывает `AuthService().ensure_default_admin()`;
- `app/auth/service.py` экспортирует только публичный `AuthService`;
- добавлен `tests/test_remaining_issues.py`.

Проверка: `41 passed`.


## Исправления code review

Закрыты критические и высокоприоритетные замечания из последнего ревью:

- парольная политика использует явный whitelist спецсимволов и запрещает пробельные символы;
- удаленная отправка аудита вынесена из hot path в фоновую очередь `queue.Queue` + daemon worker;
- GUI отправляет `/auth/logout` при закрытии главного окна;
- файловый audit log теперь содержит `sequence_number` из SQLite;
- SQLite включается в WAL-режим и получает `busy_timeout`;
- роли представлены enum `UserRole`;
- `CalculationRequest.temp_c` валидируется на границе API через `Field(ge=-60, le=60)`;
- `ApiClient` разделен на узкие клиенты `AuthApiClient`, `CalcApiClient`, `AuditApiClient`, `ExportApiClient`;
- документация дополнена ограничением in-memory SessionManager;
- архитектурная презентация дополнена таблицей портов и протоколов.

### Ограничение SessionManager

Сессии хранятся в памяти процесса. Это нормально для учебной демонстрации, но при перезапуске API пользователи должны войти повторно. Для multi-worker / production-развертывания SessionManager нужно заменить на Redis/БД-backed хранилище сессий.
