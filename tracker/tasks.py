import logging

from celery import shared_task
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    TrackerAccount,
    TrackerSetting,
    TrackedUser,
    OnlineStatus
)
from .services.tracker_services import check_online

# Инициализируем логгер
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("check_online.log")
logger.warning('Test logging')
logger.setLevel(logging.WARNING)
logger.addHandler(file_handler)


@shared_task
def check_online_task(tracked_user_id, api_hash, api_id, session_string):
    """
    Задача для проверки онлайна конкретного пользователя по ID.
    Параметры:
      - tracked_user_id: ID пользователя (TrackedUser)
      - api_hash, api_id, session_string: данные для API (Telegram client), подгружаются из настроек
    """

    try:
        # Выбираем только необходимые поля
        tracked = (TrackedUser.objects
                   .only("id", "username", "visible_online")
                   .get(id=tracked_user_id))
        username = tracked.username

        current_status = check_online(
            username=username,
            api_hash=api_hash,
            api_id=api_id,
            session_string=session_string
        )

        if current_status is None:
            # Если получаем None, значит статус недоступен — помечаем пользователя
            tracked.visible_online = False
            tracked.save(update_fields=["visible_online"])
            return

        # Фиксируем статус в таблице OnlineStatus, если он изменился
        try:
            with transaction.atomic():
                last_status_record = (OnlineStatus.objects
                                      .filter(tracked_user=tracked_user_id)
                                      .order_by("-created_at")
                                      .first())

                if not last_status_record or last_status_record.is_online != current_status:
                    OnlineStatus.objects.create(
                        tracked_user_id=tracked_user_id,
                        is_online=current_status
                    )
        except Exception:
            logger.exception(
                "[check_online_task] Unknown error while saving OnlineStatus",
                exc_info=True,
                extra={"tracked_user_id": tracked_user_id, "username": username}
            )

    except TrackedUser.DoesNotExist:
        logger.exception(
            "[check_online_task] TrackedUser not found",
            exc_info=True,
            extra={"tracked_user_id": tracked_user_id}
        )

    except Exception:
        logger.exception(
            "[check_online_task] Unknown error",
            exc_info=True,
            extra={"tracked_user_id": tracked_user_id}
        )


@shared_task
def check_online_manager_task():
    """
    Менеджер, который обходится по активным TrackerAccount и создает задачи
    на проверку статуса для привязанных к каждому аккаунту пользователей.
    """
    logger.info("[check_online_manager_task] Start")

    try:
        # Подгружаем TrackerSetting через select_related у TrackerAccount есть OneToOne на TrackerSetting
        tracker_accounts = (TrackerAccount.objects
                            .filter(is_active=True, is_auth=True)
                            .select_related("setting"))

        with transaction.atomic():
            for tracker_account in tracker_accounts.iterator():
                # Проверяем, есть ли связанная настройка (TrackerSetting)
                # Если нет, попадём в блок except ниже
                try:
                    tacker_setting = tracker_account.setting
                except ObjectDoesNotExist:
                    logger.exception("[check_online_manager_task] TrackerSetting not found", exc_info=True)
                    continue

                # Подгружаем только нужные поля пользователей
                tracked_users = (TrackedUser.objects
                                 .filter(tracker_account=tracker_account, visible_online=True)
                                 .only("id", "username"))

                for tracked_user in tracked_users:
                    # Ставим задачу на проверку
                    check_online_task.delay(
                        tracked_user_id=tracked_user.id,
                        api_hash=tracker_account.api_hash,
                        api_id=tracker_account.api_id,
                        session_string=tacker_setting.session_string
                    )
    except Exception:
        logger.exception("[check_online_manager_task] Unknown error", exc_info=True)
