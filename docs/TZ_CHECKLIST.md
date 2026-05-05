# Детальный чек-лист соответствия ТЗ

Документ составлен по каждому пункту технического задания. Формат: пункт ТЗ → где реализовано → как проверить.

## 1.1. Цели и задачи

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| 1.1.1. Разработка программного комплекса для оценки эффективности и основных энергетических показателей энергооборудования | ✅ | Общий проект `energy_system_final`, расчетный сценарий `app/calculation/orchestrator.py`, запуск `python main.py demo`, API `/calc/run`, GUI `python main.py gui`. |
| 1.1.2.1. Оптимизация и определение эффективности при заданных: нагрузке ТЭС, количестве блоков, температуре, влажности, направлении и скорости ветра | ✅ | Входная модель `CalculationInput`; поля GUI в `MainWindow`; API-модель `CalculationRequest`; расчет в `core.py`; поправки в `formulas.py`. |
| 1.1.2.2. Оптимальное разрежение в конденсаторе турбины | ✅ | `optimize_condenser_vacuum()` в `app/calculation/optimization.py`; результат входит в `FullCalculationResult`. |
| 1.1.2.3. Графики зависимости теплоотводящей способности от температуры наружного воздуха | ✅ | `analyze_temperature()` и `TemperatureAnalysisPoint.heat_removal_factor`; окно `ChartsWindow`; модуль `reporting/charts.py`. |
| Требования к срокам | ✅ | Организационный пункт; проект готов к демонстрации и сдаче. |

## 1.2. Критерии успешности

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Оперативный расчет режимов работы энергообъекта с учетом варьируемых параметров | ✅ | CLI demo, GUI, API `/calc/run`; тесты `tests/test_calculation.py`. |
| UML-диаграммы в необходимом количестве | ✅ | `docs/uml`: Use Case, Component, Class, Sequence Login, Sequence Calculation, Deployment. |
| Презентация и демонстрация работы приложения | ✅ | `docs/presentation/architecture_overview.pptx`; сценарий демонстрации `docs/DEMO_SCRIPT.md`. |

## 2. Технические требования к результатам

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Математическое ядро базируется на методах расчета из приложения 1 | ✅ | Формулы поправок и расчет эффективности перенесены в `app/calculation/formulas.py`, `core.py`, `optimization.py`. |
| Клиентская часть PyQt5/6 | ✅ | PyQt6-клиент: `app/client/*`. |
| Серверная часть | ✅ | FastAPI: `app/server/api.py`, маршруты `app/server/routes/*`. |
| Подсистема аутентификации и авторизации | ✅ | `app/auth/*`, роли `user/admin`, зависимости `get_current_user`, `get_admin_user`. |
| Оркестратор вычислительных задач | ✅ | `app/calculation/orchestrator.py`. |
| Математическое ядро | ✅ | `formulas.py`, `core.py`, `optimization.py`, `validators.py`. |
| Подсистема хранения данных | ✅ | SQLite, `app/storage/database.py`, `repositories.py`, миграция `001_init.sql`. |
| Подсистема аудита и логирования | ✅ | `app/audit/*`, таблица `audit_events`, `RotatingFileHandler`. |
| Особое внимание поправкам внешних факторов: температура | ✅ | `temperature_correction()`. |
| Влажность | ✅ | `humidity_correction()`. |
| Скорость ветра | ✅ | `wind_speed_correction()`. |
| Направление ветра | ✅ | `wind_direction_correction()`. |
| Выход: нагрузка на энергоблок | ✅ | `CalculationResult.load_per_block`. |
| Выход: КПД блока | ✅ | `CalculationResult.block_efficiency`. |
| Выход: КПД ТЭС брутто | ✅ | `CalculationResult.efficiency_brutto`. |
| Выход: собственные нужды | ✅ | `CalculationResult.own_needs_power`, `own_needs_percent`. |
| Выход: КПД ТЭС нетто | ✅ | `CalculationResult.efficiency_netto`. |
| Выход: удельный расход топлива | ✅ | `CalculationResult.fuel_consumption`. |

## 3.2. Парольная аутентификация

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Настройка и контроль параметров аутентификации | ✅ | `Settings`: `ENERGY_AUTH_MAX_FAILED_ATTEMPTS`, `ENERGY_AUTH_LOCK_MINUTES`, `ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH`, `ENERGY_AUTH_ADMIN_MIN_PASSWORD_LENGTH`; API `/auth/policy`; GUI `Политика безопасности`. |
| Смена установленных администратором паролей после первичной аутентификации | ✅ | `must_change_password`; `ChangePasswordWindow`; API `/auth/change-password`; первичный admin создается с требованием смены; пароль берется из `ENERGY_DEFAULT_ADMIN_PASSWORD` или генерируется в `data/initial_admin_credentials.txt`. |
| Исключено отображение вводимых символов пароля | ✅ | `QLineEdit.EchoMode.Password` в `LoginWindow`, `ChangePasswordWindow`, `CreateUserWindow`. |
| Блокировка после исчерпания попыток с авторазблокировкой через 15 минут | ✅ | `AuthService.login`, `locked_until`, настройка `ENERGY_AUTH_LOCK_MINUTES=15`. |
| Пароль не совпадает с идентификатором/частью имени пользователя | ✅ | `validate_password()`: проверка включения `username` в пароль. |
| Максимум неуспешных попыток до блокировки — 3 | ✅ | Настройка по умолчанию `ENERGY_AUTH_MAX_FAILED_ATTEMPTS=3`; тесты `test_failed_attempts_lock_account`. |
| Пользователь: пароль не менее 6 символов + верхний/нижний регистр + цифра + спецсимвол | ✅ | `validate_password()`, настройка `ENERGY_AUTH_USER_MIN_PASSWORD_LENGTH=6`. |
| Администратор: пароль не менее 7 символов + верхний/нижний регистр + цифра + спецсимвол | ✅ | `validate_password()`, настройка `ENERGY_AUTH_ADMIN_MIN_PASSWORD_LENGTH=7`. |
| Отказ при неверном идентификаторе или пароле | ✅ | `AuthenticationError`, HTTP 401; GUI показывает ошибку. |

## 3.3. Аудит

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Вход/выход и попытки входа пользователей/администраторов | ✅ | `login_success`, `login_failed`, `login_blocked_locked_account`, `logout`. |
| Доступ к аппаратным и программным компонентам | ✅ | `api_started`, `api_request`, обращения к маршрутам API. |
| Действия пользователей, связанные с изменением данных | ✅ | `calculation_run`, сохранение истории, экспорт CSV/PPTX. |
| Действия администраторов по изменению прав доступа, параметров и данных | ✅ | `user_created`, `user_role_changed`, `audit_cleanup_run`; GUI создания пользователя, смены роли и политики безопасности. |
| Действия интерфейсов ввода/вывода | ✅ | Ввод через GUI приводит к API-событиям; экспорт CSV/PPTX логируется. |
| Действия через API, включая аутентификацию/авторизацию | ✅ | Middleware `audit_api_requests`; auth/calc маршруты пишут события. |
| Дата и время события | ✅ | `event_time`. |
| Порядковый номер события | ✅ | Поле `id` таблицы `audit_events`. |
| Наименование события | ✅ | `event_name`. |
| Компонент / объект доступа | ✅ | `component`. |
| Учетная запись субъекта доступа | ✅ | `subject`. |
| Служебные заголовки | ✅ | `headers_json`, чувствительные значения маскируются. |
| Тип события | ✅ | `event_type`. |
| Идентификатор события | ✅ | `event_id`. |
| Нет паролей в компрометируемом виде | ✅ | Тела запросов с паролями не логируются; пароли хранятся PBKDF2-хешами; заголовки Authorization/Cookie маскируются. |
| Нет персональных данных | ✅ | Система использует только технический логин; ФИО, дата рождения, адрес и т.п. не собираются. |
| Настраиваемая глубина хранения | ✅ | `ENERGY_AUDIT_RETENTION_DAYS`, API `/calc/audit/cleanup`, кнопка очистки в `AuditWindow`. |
| Настраиваемая детализация | ✅ | `ENERGY_AUDIT_DETAIL_LEVEL=basic|standard|full`; тест `test_audit_detail_level_is_configurable`. |
| Отправка журналов на удаленный сервер | ✅ | `ENERGY_AUDIT_REMOTE_URL`, модуль `app/audit/remote.py`. |
| Ротация при ограничении места | ✅ | `RotatingFileHandler`, `ENERGY_AUDIT_MAX_BYTES`, `ENERGY_AUDIT_BACKUPS`. |

## 4.1. Интеграционные потоки

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Безопасность конфиденциальности, целостности, доступности | ✅ | Аутентификация токеном, роли, rate limit, валидация входных данных, HTTPS-настройки для сетевого режима. |
| Однозначная идентификация сторон | ✅ | Сессионный токен, `AuthenticatedUser`, `subject` в аудите. |
| Подтверждение направления/получения данных | ✅ | HTTP-коды, JSON-ответы, `history_id`, audit `api_request` со статусом. |
| Невозможность искажения данных при обмене | ✅ | Pydantic-валидация API, `validators.py`, хранение входа/выхода расчета в истории; для сетевого развертывания предусмотрен HTTPS. |
| Невозможность перехвата данных идентификации/аутентификации | ✅ | Для локального демо используется loopback `127.0.0.1`; для сети поддержаны `ENERGY_API_SSL_CERTFILE` и `ENERGY_API_SSL_KEYFILE`; токены и пароли не логируются. |
| API rate limit от DDoS/перебора | ✅ | `rate_limit()` в `server/dependencies.py`, `ENERGY_RATE_LIMIT_PER_MINUTE`. |
| Регистрация всех API-событий | ✅ | Middleware `audit_api_requests` в `server/api.py`. |

## 4.2. Описание архитектуры

| Пункт ТЗ | Статус | Реализация / проверка |
|---|---:|---|
| Назначение ПО и сценарии использования | ✅ | `README.md`, `docs/presentation/architecture_overview.pptx`, Use Case UML. |
| Среда функционирования | ✅ | `README.md`: Python, FastAPI, PyQt6, SQLite, локальный/серверный запуск. |
| Ограничения и указания по применению | ✅ | `README.md`, `docs/DEMO_SCRIPT.md`: локальный режим, HTTPS для сети, переменные окружения. |
| Описание подсистем/модулей | ✅ | `README.md`, `docs/presentation/architecture_overview.pptx`, UML Component/Class. |
| Языки программирования | ✅ | Python 3; зависимости в `requirements.txt`. |
| Взаимодействие с ПО, интерфейсы, порты, протоколы | ✅ | FastAPI `:8000`, HTTP/JSON, опционально HTTPS, SQLite, файлы `logs/exports`. |
| UML-диаграммы | ✅ | `docs/uml/*.puml`. |
| Архитектура в `.pptx` | ✅ | `docs/presentation/architecture_overview.pptx`. |

## Проверка

```bash
PYTHONPATH=. pytest -q
# 30 passed
```


## Дополнительная ревизия безопасности

| Замечание | Статус | Исправление |
|---|---:|---|
| Захардкоженный пароль администратора в UI | ✅ | Поле пароля пустое; первичный пароль задается окружением или генерируется в файл. |
| `AuditEvent` не использовался | ✅ | `audit_event()` строит и пишет объект `AuditEvent`. |
| Двойной расчет `external_factor` | ✅ | Фактор считается один раз в `calc_tes_efficiency()` и передается в `calc_block_efficiency()`. |
| `assert` в production-коде | ✅ | Заменены на `RepositoryError`. |
| `SessionManager` не потокобезопасен | ✅ | Добавлен `threading.RLock`. |
| Магические числа | ✅ | Вынесены в `app/calculation/constants.py`. |
| Глобальный `auth_service` | ✅ | Удален; используется FastAPI DI `Depends(get_auth_service)`. |


## Синхронизация UML/презентации после security-refactor

✅ UML и презентация обновлены после удаления глобального `auth_service`, внедрения `Depends(get_auth_service)`, добавления `AuditEvent`, потокобезопасного `SessionManager`, вынесения констант и генерации первичного пароля администратора.


## Исправления review v2

| Замечание | Статус |
|---|---:|
| Разделить `cleanup()` и `_cleanup_unsafe()` | ✅ |
| Использовать `dataclasses.replace()` для `AuditEvent.remote_sent` | ✅ |
| Уточнить комментарий `get_auth_service()` | ✅ |
| Убрать `global _LOGGER` | ✅ |
| Добавить `__all__` | ✅ |
| Вынести маппинг `CalculationRequest -> CalculationInput` из Pydantic-модели | ✅ |
| Добавить комментарий про per-process rate limit | ✅ |
| Заменить deprecated `on_event("startup")` на `lifespan` | ✅ |
| Не показывать серверный путь CSV/PPTX в GUI | ✅ |
| Добавить `pyproject.toml` | ✅ |
