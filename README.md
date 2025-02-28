
# SeeOnline Project

Этот проект предоставляет REST API для мониторинга Telegram-пользователей и их онлайн-статусов. Ниже описаны основные
эндпоинты и методы работы с ними, а также команды для запуска Celery-воркеров и управления Docker-контейнерами.

---

## Документация по эндпоинтам

Все эндпоинты доступны по соответствующим URL. Для каждого используется стандартный набор методов `GET` / `POST` /
`PUT` / `PATCH` / `DELETE`, если не указано иное. Также включена базовая фильтрация (DjangoFilterBackend), позволяющая
осуществлять поиск и выборку записей по ключевым полям.

### 1. TrackerAccount

**Базовый URL**:

```
/tracker-accounts/
```

- **GET** `/<tracker_account_id>/` — получение данных одного аккаунта.
- **GET** `/` — получение списка аккаунтов (с фильтрацией по `id`, `telegram_user_id`, `is_active`, `is_auth`).
- **POST** `/` — создание нового трекер-аккаунта.
- **PUT/PATCH** `/<tracker_account_id>/` — обновление данных аккаунта.
- **DELETE** `/<tracker_account_id>/` — удаление аккаунта.

**Основные поля модели** (`TrackerAccount`):

- `id`: `int` — первичный ключ.
- `telegram_user_id`: `bigint` — уникальный идентификатор пользователя в Telegram.
- `api_id`: `int` — идентификатор API.
- `api_hash`: `str` — хеш для доступа к API.
- `is_active`: `bool` — активен ли аккаунт.
- `is_auth`: `bool` — прошёл ли он авторизацию.
- `created_at`, `updated_at`: даты создания/обновления.

**Фильтрация** (пример):

- `GET /tracker-accounts/?is_active=true`
- `GET /tracker-accounts/?telegram_user_id=1234567`

### 2. TrackerSetting

**Базовый URL**:

```
/tracker-settings/
```

- **GET** `/<tracker_setting_id>/` — получение настроек конкретного аккаунта.
- **GET** `/` — список настроек (фильтрация по `phone_number`, `tracker_account__telegram_user_id` и т.д.).
- **POST** `/` — создание настроек для аккаунта.
- **PUT/PATCH** `/<tracker_setting_id>/` — обновление настроек.
- **DELETE** `/<tracker_setting_id>/` — удаление настроек.

**Основные поля модели** (`TrackerSetting`):

- `id`: `int` — первичный ключ.
- `tracker_account_id`: `int` — ссылка на `TrackerAccount`.
- `phone_number`: `str` — номер телефона, уникальный для каждой настройки.
- `session_string`: `str` — сохранённая сессия (может быть `null`).
- `max_users`: `int` — максимально допустимое число отслеживаемых пользователей.
- `current_users`: `int` — текущее число отслеживаемых пользователей.
- `created_at`, `updated_at`: даты создания/обновления.

**Фильтрация** (пример):

- `GET /tracker-settings/?phone_number=+123456789`
- `GET /tracker-settings/?tracker_account__telegram_user_id=321`

### 3. TelegramUser

**Базовый URL**:

```
/telegram-users/
```

- **GET** `/<telegram_user_id>/` — получение конкретного `TelegramUser`.
- **GET** `/` — список `TelegramUser` (можно фильтровать по `id`, `telegram_user_id`, `role`).
- **POST** `/` — создание записи о Telegram-пользователе.
- **PUT/PATCH** `/<telegram_user_id>/` — обновление данных пользователя (например, смена роли).
- **DELETE** `/<telegram_user_id>/` — удаление пользователя из системы.

**Основные поля модели** (`TelegramUser`):

- `id`: `int`
- `telegram_user_id`: `bigint` — уникальный ID в Telegram.
- `role`: `str` — роль пользователя (banned / user / vip / admin).
- `created_at`, `updated_at`: даты создания/обновления.

**Фильтрация** (пример):

- `GET /telegram-users/?role=admin`
- `GET /telegram-users/?telegram_user_id=1234567`

### 4. TrackedUser

**Базовый URL**:

```
/tracked-users/
```

- **GET** `/<tracked_user_id>/` — получение конкретного отслеживаемого пользователя.
- **GET** `/` — список отслеживаемых (фильтрация по `username`, `tracker_account__telegram_user_id`,
  `telegram_user__telegram_user_id`).
- **POST** `/` — создание новой связи «Трекер-Аккаунт → TelegramUser».
- **PUT/PATCH** `/<tracked_user_id>/` — обновление полей (например, `username`, `visible_online`).
- **DELETE** `/<tracked_user_id>/` — удаление связи (пользователь перестаёт отслеживаться).

**Основные поля модели** (`TrackedUser`):

- `id`: `int`
- `tracker_account_id`: `int` — ссылка на `TrackerAccount`.
- `telegram_user_id`: `int` — ссылка на `TelegramUser`.
- `username`: `str` — юзернейм в Telegram.
- `visible_online`: `bool` — флаг, показывать ли, что пользователь в онлайне.
- `created_at`, `updated_at`: даты создания/обновления.

**Фильтрация** (пример):

- `GET /tracked-users/?username=Ivan`
- `GET /tracked-users/?tracker_account__telegram_user_id=999999`
- `GET /tracked-users/?telegram_user__telegram_user_id=1234567`

### 5. OnlineStatus

**Базовый URL**:

```
/online-statuses/
```

- **GET** `/<online_status_id>/` — получение конкретной записи онлайн-статуса.
- **GET** `/` — список всех статусов (можно фильтровать по `tracked_user_id`, `is_online`, диапазону дат `created_at` и
  т.д.).
- **POST** `/` — создание новой записи статуса (онлайн/оффлайн).
- **PUT/PATCH** `/<online_status_id>/` — изменение статуса (хотя чаще всего статус пишется однократно).
- **DELETE** `/<online_status_id>/` — удаление статуса (допустимо, если нужно очистить историю).

**Основные поля модели** (`OnlineStatus`):

- `id`: `int`
- `tracked_user_id`: `int` — ссылка на `TrackedUser`.
- `is_online`: `bool` — онлайн (`true`) или нет (`false`).
- `created_at`: `datetime` — время фиксации статуса.

**Фильтрация** (пример):

- `GET /online-statuses/?tracked_user_id=10`
- `GET /online-statuses/?username=ivanko` (через `tracked_user__username`)
- `GET /online-statuses/?is_online=true`
- `GET /online-statuses/?created_at_before=2025-01-01&created_at_after=2024-12-01`

---

## Запуск воркеров

### Команда запуска Celery-воркера

```
make worker
```

- Выполняет команду:
  ```
  celery -A SeeOnline worker --loglevel=warning --logfile=celery_logs.log
  ```
- Поднимает основной воркер для обработки фоновых задач.

### Команда запуска Beat-воркера

```
make beat
```

- Выполняет команду:
  ```
  celery -A SeeOnline beat --loglevel=warning --logfile=beat_logs.log
  ```
- Поднимает планировщик задач (beat), отвечающий за периодический запуск заданий.

---

## Управление контейнерным запуском

### Запустить приложение

```
make run
```

- Выполняет:
  ```
  docker-compose up --build -d
  ```
- Собирает и поднимает контейнеры в фоновом режиме.

### Остановить приложение

```
make stop
```

- Выполняет:
  ```
  docker-compose stop
  ```
- Останавливает запущенные контейнеры (но не удаляет их).

### Остановить и очистить реестр контейнеров

```
make clean
```

- Выполняет:
  ```
  docker-compose down
  ```
- Удаляет **все** запущенные контейнеры и сети проекта, но не трогает образы.

### Удалить все существующие контейнеры и образы

*(если нужно всё снести начисто)*

```
make full-clean
```

- Выполняет:
  ```
  docker-compose down --volumes
  docker system prune -af
  docker volume prune -f
  ```
- Удаляет **все** образы, контейнеры, тома и сети (будьте осторожны).

### Перезапустить приложение

```
make restart
```

- Последовательно выполняет:
  ```
  make stop
  make run
  ```
- Останавливает контейнеры и заново их запускает.

### Пересобрать приложение

```
make rebuild
```

- Выполняет:
  ```
  make clean
  make run
  ```
- Удаляет контейнеры текущего проекта и заново собирает их с нуля.

---
