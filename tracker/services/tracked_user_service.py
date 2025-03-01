from django.db import transaction
from django.db import models

from rest_framework.exceptions import APIException
from rest_framework import status

from ..models import (
    TrackedUser,
    TrackerAccount
)


# -----------------------------------------------------------
# Кастомная ошибка, если не удалось распределить
# -----------------------------------------------------------
class CannotAssignTrackerAccount(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Не удалось найти свободный аккаунт для привязки.'
    default_code = 'tracker_account_assignment_failed'


# -----------------------------------------------------------
# Кастомная ошибка, если закончились доступные ячейки отслеживания у пользователя
# -----------------------------------------------------------
class LimitFollowedUsersReached(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Лимит отслеживаемых пользователей для данного TelegramUser исчерпан.'
    default_code = 'limit_of_followed_users_has_been_reached'


@transaction.atomic
def create_tracked_user(data: dict) -> TrackedUser:
    """
    Переопределённый метод создания TrackedUser:
     1) Проверяем, что у TelegramUser есть свободный слот (current_users < max_users).
     2) Ищем любой TrackerAccount, у которого is_active=True, is_auth=True и
        setting.current_users < setting.max_users.
     3) Если нет доступных аккаунтов или нет слота у TelegramUser — выбрасываем ошибку.
     4) Создаём TrackedUser, привязываем к найденному TrackerAccount.
     5) Увеличиваем current_users у TelegramUser и TrackerSetting на 1.
    """
    telegram_user = data['telegram_user']

    # Проверяем лимиты
    if telegram_user.current_users >= telegram_user.max_users:
        raise LimitFollowedUsersReached

    # Ищем доступный аккаунт
    free_tracker = TrackerAccount.objects.filter(
        is_auth=True,
        is_active=True,
        setting__current_users__lt=models.F('setting__max_users')
    ).select_related('setting').first()

    if not free_tracker:
        # Если не нашли
        raise CannotAssignTrackerAccount()

    # Создаём запись TrackedUser
    tracked_user = TrackedUser.objects.create(
        telegram_user=telegram_user,
        tracker_account=free_tracker,
        username=data['username'],
        # если есть ещё поля, которые клиент передаёт, тоже передадим:
        visible_online=data.get('visible_online', True),
        # и т.д.
    )

    # Обновляем счётчики
    telegram_user.current_users += 1
    telegram_user.save()

    tracker_setting = free_tracker.setting
    tracker_setting.current_users += 1
    tracker_setting.save()

    return tracked_user


@transaction.atomic
def delete_tracked_user(tracked_user: TrackedUser) -> None:
    """
    Уменьшает счётчики ячеек у telegram_user и tracker_account,
    после чего удаляет сам tracked_user.
    """
    telegram_user = tracked_user.telegram_user
    tracker_account = tracked_user.tracker_account

    # Уменьшаем счётчики
    if telegram_user.current_users > 0:
        telegram_user.current_users -= 1
        telegram_user.save()

    setting = getattr(tracker_account, 'setting', None)
    if setting and setting.current_users > 0:
        setting.current_users -= 1
        setting.save()

    # Удаляем TrackedUser
    tracked_user.delete()
