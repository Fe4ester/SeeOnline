from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from django.db import models

from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus
)

from .serializers import (
    TrackerAccountSerializer,
    TrackerSettingSerializer,
    TelegramUserSerializer,
    TrackedUserSerializer,
    OnlineStatusSerializer
)

from .filters import (
    TrackerAccountFilter,
    TrackerSettingFilter,
    TelegramUserFilter,
    TrackedUserFilter,
    OnlineStatusFilter
)


# -----------------------------------------------------------
# Кастомная ошибка, если не удалось распределить
# TrackedUser или что-то пошло не так
# (Можно было бы использовать ValidationError,
#  но для примера создадим класс APIException).
# -----------------------------------------------------------
class CannotAssignTrackerAccount(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Не удалось найти свободный аккаунт для привязки.'
    default_code = 'tracker_account_assignment_failed'


# -----------------------------------------------------------
# Кастомная ошибка, если при удалении TrackerAccount
# не удалось "перевесить" всех TrackedUser.
# -----------------------------------------------------------
class CannotReassignTrackedUsers(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Невозможно перевесить всех TrackedUser на другие аккаунты.'
    default_code = 'tracker_account_reassign_failed'


# -----------------------------------------------------------
# ViewSet для TrackerAccount.
# -----------------------------------------------------------
class TrackerAccountViewSet(viewsets.ModelViewSet):
    queryset = TrackerAccount.objects.all()
    serializer_class = TrackerAccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerAccountFilter

    def get_queryset(self):
        # Подгружаем связанные данные
        return (
            super()
            .get_queryset()
            .select_related()
            .prefetch_related('setting')
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Переопределяем метод удаления TrackerAccount:
         1) Ищем все связанные TrackedUser.
         2) Пытаемся "перевесить" их на другие свободные трекеры (те, у которых
            is_active=True, is_auth=True, и current_users < max_users).
         3) Если у нас не хватает суммарного "свободного места" (по current_users)
            во всех доступных аккаунтах, то выбрасываем ошибку.
         4) Если хватает, равномерно/по порядку распределяем.
         5) Удаляем аккаунт.
        """
        # Сначала получаем сам удаляемый объект
        instance = self.get_object()
        tracker_setting = getattr(instance, 'setting', None)

        # Все TrackedUser, которые "висят" на данном аккаунте
        tracked_users = TrackedUser.objects.filter(tracker_account=instance)

        # Если на аккаунт не привязан setting, возможно, current_users = 0.
        # Но если привязан, то проверим количество:
        total_tracked = tracked_users.count()

        if total_tracked == 0:
            # Если на этом аккаунте никого не отслеживают, то удаляем спокойно.
            return super().destroy(request, *args, **kwargs)

        # Список всех остальных TrackerAccount, которые свободны:
        #  is_active=True, is_auth=True, НЕ равен удаляемому,
        #  и setting.current_users < setting.max_users
        candidate_accounts = TrackerAccount.objects.filter(
            is_active=True,
            is_auth=True
        ).exclude(id=instance.id).select_related('setting')

        # Считаем суммарное свободное место у всех кандидатов
        total_free_capacity = 0
        for acc in candidate_accounts:
            if hasattr(acc, 'setting'):
                total_free_capacity += (acc.setting.max_users - acc.setting.current_users)

        if total_free_capacity < total_tracked:
            # Если суммарно не хватает места, выбрасываем ошибку
            raise CannotReassignTrackedUsers(
                detail='Недостаточно свободных слотов, чтобы перевесить всех TrackedUser.'
            )

        # Если места хватает, начинаем «распределять»
        # (просто по порядку, пока не распределим всех).
        tracked_users_to_reassign = list(tracked_users)  # список для итерации

        for candidate in candidate_accounts:
            if not hasattr(candidate, 'setting'):
                # если у кого-то нет настроек (теоретически не должно быть, но проверим) — пропускаем
                continue

            setting = candidate.setting
            free_slots = setting.max_users - setting.current_users

            # Пока есть свободные слоты и есть кого перевешивать:
            while free_slots > 0 and tracked_users_to_reassign:
                # Берем одного TrackedUser из очереди
                tu = tracked_users_to_reassign.pop()

                # Перевешиваем его на candidate
                tu.tracker_account = candidate
                tu.save()

                # Увеличиваем current_users на 1
                setting.current_users += 1
                setting.save()

                free_slots -= 1

                # Также нужно уменьшить current_users у старого трекера
                # (но поскольку мы удаляем старый трекер, его setting
                #  и так перестанет существовать;
                #  однако, если хотим "корректно" — сделаем):
                if tracker_setting:
                    tracker_setting.current_users -= 1
                    tracker_setting.save()

                # Если закончились TrackedUser для перевешивания, выходим
                if not tracked_users_to_reassign:
                    break

            # Если уже перевесили всех, можно выходить из цикла
            if not tracked_users_to_reassign:
                break

        # Проверяем, вдруг остались "неперевешенные" (хотя не должно, т.к. места вроде хватило).
        if tracked_users_to_reassign:
            # если что-то пошло не так и остались необработанные
            raise CannotReassignTrackedUsers(
                detail='Произошла ошибка при распределении TrackedUser по другим аккаунтам.'
            )

        # Если всё успешно распределено, спокойно удаляем аккаунт
        return super().destroy(request, *args, **kwargs)


# -----------------------------------------------------------
# ViewSet для TrackerSetting.
# -----------------------------------------------------------
class TrackerSettingViewSet(viewsets.ModelViewSet):
    queryset = TrackerSetting.objects.select_related('tracker_account')
    serializer_class = TrackerSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerSettingFilter


# -----------------------------------------------------------
# ViewSet для TelegramUser.
# -----------------------------------------------------------
class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TelegramUserFilter

    def destroy(self, request, *args, **kwargs):
        telegram_id = request.query_params.get("telegram_id")

        if telegram_id:
            user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
            if user:
                user.delete()
                return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return super().destroy(request, *args, **kwargs)


# -----------------------------------------------------------
# ViewSet для TrackedUser
# Здесь переопределяем create и destroy,
# чтобы учитывать бизнес-логику распределения/освобождения.
# -----------------------------------------------------------
class TrackedUserViewSet(viewsets.ModelViewSet):
    queryset = TrackedUser.objects.select_related('tracker_account', 'telegram_user')
    serializer_class = TrackedUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackedUserFilter

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Переопределённый метод создания TrackedUser:
         1) Проверяем, что у TelegramUser есть свободный слот (current_users < max_users).
         2) Ищем любой TrackerAccount, у которого is_active=True, is_auth=True и
            setting.current_users < setting.max_users.
         3) Если нет доступных аккаунтов или нет слота у TelegramUser — выбрасываем ошибку.
         4) Создаём TrackedUser, привязываем к найденному TrackerAccount.
         5) Увеличиваем current_users у TelegramUser и TrackerSetting на 1.
        """
        # Сериализатор
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Достаём объект telegram_user из валидированных данных
        telegram_user = serializer.validated_data['telegram_user']

        # Проверяем лимиты у самого TelegramUser
        if telegram_user.current_users >= telegram_user.max_users:
            raise APIException(
                detail="Лимит отслеживаемых пользователей для данного TelegramUser исчерпан.",
                code=status.HTTP_400_BAD_REQUEST
            )

        # Ищем любой аккаунт, у которого есть настройка с current_users < max_users
        # и is_auth=True, is_active=True
        free_tracker = TrackerAccount.objects.filter(
            is_auth=True,
            is_active=True,
            setting__current_users__lt=models.F('setting__max_users')
        ).select_related('setting').first()

        if not free_tracker:
            # Если не нашли
            raise CannotAssignTrackerAccount()

        # Теперь мы знаем, на какой аккаунт будем вешать
        # Сразу прописываем в сериализатор нужный tracker_account
        # (Перезапишем, даже если клиент передал tracker_account_id)
        serializer.validated_data['tracker_account'] = free_tracker

        # Сохраняем TrackedUser
        tracked_user = serializer.save()

        # Увеличиваем current_users у TelegramUser
        telegram_user.current_users += 1
        telegram_user.save()

        # Увеличиваем current_users у привязанного TrackerSetting
        tracker_setting = free_tracker.setting
        tracker_setting.current_users += 1
        tracker_setting.save()

        # Возвращаем стандартный ответ
        headers = self.get_success_headers(serializer.data)
        return Response(
            self.get_serializer(tracked_user).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Переопределяем удаление TrackedUser:
         1) Уменьшаем current_users у TelegramUser на 1.
         2) Уменьшаем current_users у TrackerSetting связанного аккаунта на 1.
         3) Удаляем TrackedUser.
        """
        instance = self.get_object()
        telegram_user = instance.telegram_user
        tracker_account = instance.tracker_account

        # Уменьшаем счётчики
        if telegram_user.current_users > 0:
            telegram_user.current_users -= 1
            telegram_user.save()

        setting = getattr(tracker_account, 'setting', None)
        if setting and setting.current_users > 0:
            setting.current_users -= 1
            setting.save()

        return super().destroy(request, *args, **kwargs)


# -----------------------------------------------------------
# ViewSet для OnlineStatus.
# По заданию ничего особого не требуется,
# кроме базовых операций и фильтрации.
# -----------------------------------------------------------
class OnlineStatusViewSet(viewsets.ModelViewSet):
    queryset = OnlineStatus.objects.select_related('tracked_user', 'tracked_user__tracker_account',
                                                   'tracked_user__telegram_user')
    serializer_class = OnlineStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OnlineStatusFilter

    def destroy(self, request, *args, **kwargs):
        # Обычное удаление, без кастомной логики
        return super().destroy(request, *args, **kwargs)
