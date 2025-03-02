import logging

from celery import shared_task
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    TrackerAccount,
    TrackedUser,
    OnlineStatus
)
from .services.tracker_service import check_online

logger = logging.getLogger(__name__)  # __name__ = 'tracker.tasks'

file_handler = logging.FileHandler("check_online.log")
logger.warning('Test logging')

logger.setLevel(logging.WARNING)
logger.addHandler(file_handler)


@shared_task
def check_online_task(tracked_user_id, api_hash, api_id, session_string):
    try:
        logger.debug("[check_online_task] Starting with tracked_user_id=%s", tracked_user_id)

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
        logger.debug("[check_online_task] Received status=%s for user=%s", current_status, username)

        if current_status is None:
            tracked.visible_online = False
            tracked.save(update_fields=["visible_online"])
            logger.info("[check_online_task] Marked user %s offline (status=None)", username)
            return

        # ...
        last_status_record = (OnlineStatus.objects
                              .filter(tracked_user=tracked_user_id)
                              .order_by("-created_at")
                              .first())
        if not last_status_record or last_status_record.is_online != current_status:
            OnlineStatus.objects.create(
                tracked_user_id=tracked_user_id,
                is_online=current_status
            )
            logger.info("[check_online_task] Created new OnlineStatus record for %s; is_online=%s", username,
                        current_status)

    except TrackedUser.DoesNotExist:
        logger.exception("[check_online_task] TrackedUser not found", extra={"tracked_user_id": tracked_user_id})
    except Exception:
        logger.exception("[check_online_task] Unknown error", extra={"tracked_user_id": tracked_user_id})


@shared_task
def check_online_manager_task():
    logger.info("[check_online_manager_task] Start manager iteration")
    try:
        tracker_accounts = (TrackerAccount.objects
                            .filter(is_active=True, is_auth=True)
                            .select_related("setting"))

        with transaction.atomic():
            for tracker_account in tracker_accounts.iterator():
                logger.debug("[check_online_manager_task] Processing account id=%s (tg_id=%s)", tracker_account.id,
                             tracker_account.telegram_id)

                try:
                    tacker_setting = tracker_account.setting
                except ObjectDoesNotExist:
                    logger.warning("[check_online_manager_task] No setting for tracker_account=%s", tracker_account)
                    continue

                tracked_users = (TrackedUser.objects
                                 .filter(tracker_account=tracker_account, visible_online=True)
                                 .only("id", "username"))

                for tracked_user in tracked_users:
                    logger.debug("[check_online_manager_task] Scheduling check_online for tracked_user_id=%s",
                                 tracked_user.id)
                    check_online_task.delay(
                        tracked_user_id=tracked_user.id,
                        api_hash=tracker_account.api_hash,
                        api_id=tracker_account.api_id,
                        session_string=tacker_setting.session_string
                    )
    except Exception:
        logger.exception("[check_online_manager_task] Unknown error")
