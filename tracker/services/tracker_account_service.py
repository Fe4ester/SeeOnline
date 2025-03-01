from django.db import transaction
from rest_framework.exceptions import APIException
from rest_framework import status

from ..models import TrackerAccount, TrackedUser


# -----------------------------------------------------------
# Кастомная ошибка, если при удалении TrackerAccount
# не удалось "перевесить" всех TrackedUser.
# -----------------------------------------------------------
class CannotReassignTrackedUsers(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Невозможно перевесить всех TrackedUser на другие аккаунты.'
    default_code = 'tracker_account_reassign_failed'


@transaction.atomic
def reassign_and_delete_tracker_account(tracker_account: TrackerAccount) -> None:
    """
    1) Ищем все связанные TrackedUser, которые «висят» на данном аккаунте.
    2) Считаем суммарное «свободное место» на всех других аккаунтах.
    3) Если суммарной емкости не хватает — выбрасываем CannotReassignTrackedUsers.
    4) Иначе «равномерно» распределяем пользователей по доступным аккам.
    5) Удаляем сам tracker_account.
    """

    tracked_users = TrackedUser.objects.filter(tracker_account=tracker_account)
    total_tracked = tracked_users.count()

    if total_tracked == 0:
        # Если не привязано ни одного TrackedUser, можно сразу удалить
        tracker_account.delete()
        return

    # Ищем другие аккаунты
    candidate_accounts = TrackerAccount.objects.filter(
        is_active=True,
        is_auth=True
    ).exclude(id=tracker_account.id).select_related('setting')

    # Считаем, хватает ли суммарно слотов
    total_free_capacity = 0
    for acc in candidate_accounts:
        if hasattr(acc, 'setting'):
            total_free_capacity += (acc.setting.max_users - acc.setting.current_users)

    if total_free_capacity < total_tracked:
        raise CannotReassignTrackedUsers(
            detail='Недостаточно свободных слотов, чтобы перевесить всех TrackedUser.'
        )

    # Если слотов хватает, распределяем
    tracker_setting = getattr(tracker_account, 'setting', None)
    tracked_users_to_reassign = list(tracked_users)

    for candidate in candidate_accounts:
        if not hasattr(candidate, 'setting'):
            continue

        setting = candidate.setting
        free_slots = setting.max_users - setting.current_users

        while free_slots > 0 and tracked_users_to_reassign:
            tu = tracked_users_to_reassign.pop()
            tu.tracker_account = candidate
            tu.save()

            setting.current_users += 1
            setting.save()

            free_slots -= 1

            # Для «корректности» уменьшаем счётчик у исходного трекера
            if tracker_setting and tracker_setting.current_users > 0:
                tracker_setting.current_users -= 1
                tracker_setting.save()

            if not tracked_users_to_reassign:
                break

        if not tracked_users_to_reassign:
            break

    # Если по каким-то причинам остались непрераспределённые (не должно остаться)
    if tracked_users_to_reassign:
        raise CannotReassignTrackedUsers(
            detail='Произошла ошибка при распределении TrackedUser по другим аккаунтам.'
        )

    # Теперь можно удалить исходный трекер
    tracker_account.delete()
