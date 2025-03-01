
# SeeOnline Project — Актуальная документация по API

## 1. TrackerAccount

**Базовый URL**:  
```
/tracker-accounts/
```

**Основные методы:**
1. **GET /tracker-accounts/**  
   Получение списка аккаунтов с возможной фильтрацией по:
   - `id` (точное совпадение)
   - `telegram_id` (точное совпадение)
   - `is_active` (bool)
   - `is_auth` (bool)

2. **POST /tracker-accounts/**  
   Создание нового трекер-аккаунта.

3. **GET /tracker-accounts/<id>/**  
   Получение данных одного аккаунта по его `id`.

4. **PATCH /tracker-accounts/<id>/**  
   Частичное обновление полей аккаунта по `id`.

5. **DELETE /tracker-accounts/<id>/**  
   Удаление аккаунта.  
   При удалении срабатывает логика перераспределения «отслеживаемых пользователей» на другой доступный трекер, если есть свободные слоты.

**Дополнительные эндпоинты** (обновление/удаление по `telegram_id`):
- **PATCH /tracker-accounts/by-telegram-id/<telegram_id>**  
  Обновление полей аккаунта, найденного по `telegram_id`.
- **DELETE /tracker-accounts/by-telegram-id/<telegram_id>**  
  Удаление аккаунта по `telegram_id` (также с перераспределением «отслеживаемых»).

### Поля модели `TrackerAccount`:
- `id`: int, PK
- `telegram_id`: bigint (уникальный)
- `api_id`: int (уникальный)
- `api_hash`: str (уникальный)
- `is_active`: bool
- `is_auth`: bool
- `created_at`, `updated_at`: datetime

**Пример фильтрации**:
```
GET /tracker-accounts/?is_active=true
GET /tracker-accounts/?telegram_id=123456789
```

---

## 2. TrackerSetting

**Базовый URL**:  
```
/tracker-settings/
```

**Основные методы:**
1. **GET /tracker-settings/**  
   Список всех настроек с фильтрацией по:
   - `id` (точное совпадение)
   - `phone_number` (точное совпадение)
   - `tracker_account__telegram_id` (точное совпадение)
2. **POST /tracker-settings/**  
   Создание новых настроек.
3. **GET /tracker-settings/<id>/**  
   Получение конкретных настроек по `id`.
4. **PATCH /tracker-settings/<id>/**  
   Частичное обновление настроек по `id`.
5. **DELETE /tracker-settings/<id>/**  
   Удаление настроек по `id`.

**Дополнительные эндпоинты**:
- **PATCH /tracker-settings/by-phone-number/<phone>**  
  Обновление настроек по `phone_number`.
- **DELETE /tracker-settings/by-phone-number/<phone>**  
  Удаление по `phone_number`.
- **PATCH /tracker-settings/by-tracker-telegram-id/<tg_id>**  
  Обновление настроек по `tracker_account.telegram_id`.
- **DELETE /tracker-settings/by-tracker-telegram-id/<tg_id>**  
  Удаление по `tracker_account.telegram_id`.

### Поля модели `TrackerSetting`:
- `id`: int, PK
- `tracker_account_id`: int (OneToOne к `TrackerAccount`)
- `phone_number`: str (уникальный)
- `session_string`: str / null
- `max_users`: int
- `current_users`: int
- `created_at`, `updated_at`: datetime

**Примеры фильтрации**:
```
GET /tracker-settings/?phone_number=+1234567
GET /tracker-settings/?tracker_account__telegram_id=888
```

---

## 3. TelegramUser

**Базовый URL**:
```
/telegram-users/
```

**Основные методы:**
1. **GET /telegram-users/**  
   Список всех пользователей с фильтрацией по:
   - `id`
   - `telegram_id`
   - `role` (banned / user / vip / admin)
2. **POST /telegram-users/**  
   Создание новой записи (регистрация TelegramUser).
3. **GET /telegram-users/<id>/**  
   Получение данных одного пользователя по `id` (внутренний PK).
4. **PATCH /telegram-users/<id>/**  
   Частичное обновление данных (например, смена роли).
5. **DELETE /telegram-users/<id>/**  
   Удаление пользователя.

**Дополнительные эндпоинты**:
- **PATCH /telegram-users/by-telegram-id/<tg_id>**  
  Обновить пользователя, найденного по `telegram_id`.
- **DELETE /telegram-users/by-telegram-id/<tg_id>**  
  Удалить пользователя, найденного по `telegram_id`.
- **PATCH /telegram-users/by-role/<role>**  
  Массовое обновление данных всех пользователей с указанной ролью.
- **DELETE /telegram-users/by-role/<role>**  
  Массовое удаление всех пользователей с указанной ролью (будьте осторожны).

### Поля модели `TelegramUser`:
- `id`: int, PK
- `telegram_id`: bigint (уникальный)
- `role`: str (banned / user / vip / admin)
- `current_users`, `max_users`: int
- `created_at`, `updated_at`: datetime

**Примеры фильтрации**:
```
GET /telegram-users/?role=admin
GET /telegram-users/?telegram_id=1234567
```

---

## 4. TrackedUser

**Базовый URL**:
```
/tracked-users/
```

**Основные методы:**
1. **GET /tracked-users/**  
   Список отслеживаемых пользователей с фильтрацией по:
   - `id`
   - `username`
   - `visible_online`
   - `tracker_account__telegram_id`
   - `telegram_user__telegram_id`
2. **POST /tracked-users/**  
   Создание связи «ТрекерАккаунт → TelegramUser» (указываем `tracker_account_id` и `telegram_user_id`, либо систему
   определения аккаунта).
3. **GET /tracked-users/<id>/**  
   Детальная информация об одном «отслеживаемом».
4. **PATCH /tracked-users/<id>/**  
   Частичное обновление (смена `username`, `visible_online` и т.д.).
5. **DELETE /tracked-users/<id>/**  
   Удаление отслеживания. При этом вызывается сервисная логика для корректного «освобождения слотов».

**Дополнительные эндпоинты**:
- **PATCH /tracked-users/by-username/<username>**  
  Частичное обновление по `username` (если нужно изменить поля).
- **DELETE /tracked-users/by-username/<username>**  
  Удаление записи, найденной по `username`.

### Поля модели `TrackedUser`:
- `id`: int, PK
- `tracker_account_id`: int (ForeignKey к `TrackerAccount`)
- `telegram_user_id`: int (ForeignKey к `TelegramUser`)
- `username`: str
- `visible_online`: bool
- `created_at`, `updated_at`: datetime

**Примеры фильтрации**:
```
GET /tracked-users/?username=Ivan
GET /tracked-users/?tracker_account__telegram_id=999999
GET /tracked-users/?telegram_user__telegram_id=1234567
```

---

## 5. OnlineStatus

**Базовый URL**:
```
/online-statuses/
```

**Основные методы:**
1. **GET /online-statuses/**  
   Список статусов с фильтрацией:
   - `id`
   - `tracked_user__username` (через параметр `username=...`)
   - `is_online` (bool)
   - диапазон дат `created_at` (через `created_at_after` и `created_at_before`).
2. **POST /online-statuses/**  
   Создание новой записи (фиксируем, что пользователь в сети или вышел).
3. **GET /online-statuses/<id>/**  
   Просмотр конкретной записи.
4. **PATCH /online-statuses/<id>/**  
   Частичное изменение статуса (при необходимости).
5. **DELETE /online-statuses/<id>/**  
   Удаление записи статуса.

**Дополнительные эндпоинты**:
- **DELETE /online-statuses/by-tracked-user-id/<tracked_user_id>**  
  Массовое удаление всех статусов, связанных с указанным `TrackedUser.id`.
- **DELETE /online-statuses/by-tracked-username/<username>**  
  Массовое удаление статусов по `TrackedUser.username`.

### Поля модели `OnlineStatus`:
- `id`: int, PK
- `tracked_user_id`: int (ForeignKey к `TrackedUser`)
- `is_online`: bool
- `created_at`: datetime (автоматически проставляется при записи)

**Примеры фильтрации**:
```
GET /online-statuses/?tracked_user_id=10
GET /online-statuses/?username=ivanko
GET /online-statuses/?created_at_before=2025-01-01&created_at_after=2024-12-01
GET /online-statuses/?is_online=true
```

---

# Запуск Celery

## Запустить Celery-воркер

```
make worker
```
Запускает команду:
```
celery -A SeeOnline worker --loglevel=warning --logfile=celery_logs.log
```
В результате поднимается Celery-воркер для фоновых задач.

## Запустить Celery Beat (планировщик)

```
make beat
```
Запускает команду:
```
celery -A SeeOnline beat --loglevel=warning --logfile=beat_logs.log
```
Поднимается `beat`, который отвечает за плановое (периодическое) выполнение задач.

---

# Управление Docker-контейнерами

## Запустить приложение

```
make run
```
Выполняет:
```
docker-compose up --build -d
```
Собирает и запускает все контейнеры в фоновом режиме.

## Остановить приложение

```
make stop
```
Выполняет:
```
docker-compose stop
```
Останавливает все запущенные контейнеры (не удаляя их).

## Очистить (остановить и убрать контейнеры)

```
make clean
```
Выполняет:
```
docker-compose down
```
Полностью останавливает и удаляет контейнеры (образы остаются).

## Удалить все контейнеры и образы (полная очистка)

```
make full-clean
```
Выполняет:
```
docker-compose down --volumes
docker system prune -af
docker volume prune -f
```
Удаляет все ресурсы Docker: контейнеры, образы, тома и сети — **необратимо**.

## Перезапустить приложение

```
make restart
```
Шаги:
1. `make stop` (останавливает контейнеры)
2. `make run` (заново запускает)

## Пересобрать приложение

```
make rebuild
```
Шаги:
1. `make clean` (останавливает и удаляет контейнеры)
2. `make run` (собирает и запускает всё с нуля)

---

**Все указанные эндпоинты и методы — пример «умолчаний» в `ModelViewSet`. Благодаря добавленным кастомным экшенам можно проводить PATCH/DELETE и по другим уникальным полям (см. соответствующие секции).**