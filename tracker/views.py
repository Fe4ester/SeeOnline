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

from .services.tracker_account_service import reassign_and_delete_tracker_account
from .services.tracked_user_service import delete_tracked_user, create_tracked_user


# -----------------------------------------------------------
# ViewSet для TrackerAccount.
# -----------------------------------------------------------
class TrackerAccountViewSet(viewsets.ModelViewSet):
    queryset = TrackerAccount.objects.all()
    serializer_class = TrackerAccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerAccountFilter

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Переопределенный метод удаления, для перераспределения всех Отслеживаемых аккаунтов на другой Трекер.\n
        При отсутствии трекеров с доступными слотами возвращается ошибка и удаление не происходит.\n
        Так же есть защита на уровне базы данных, так что удалить без перераспределения не получится никак.

        """
        instance = self.get_object()
        # Вызов сервисного метода
        reassign_and_delete_tracker_account(instance)
        # Если всё ок, возвращаем 204
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------
# ViewSet для TrackerSetting.
# -----------------------------------------------------------
class TrackerSettingViewSet(viewsets.ModelViewSet):
    queryset = TrackerSetting.objects.all()
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


# -----------------------------------------------------------
# ViewSet для TrackedUser
# -----------------------------------------------------------
class TrackedUserViewSet(viewsets.ModelViewSet):
    queryset = TrackedUser.objects.all()
    serializer_class = TrackedUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackedUserFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Вызываем сервисную функцию
        tracked_user = create_tracked_user(serializer.validated_data)

        # Готовим ответ
        return Response(
            self.get_serializer(tracked_user).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_tracked_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------
# ViewSet для OnlineStatus.
# -----------------------------------------------------------
class OnlineStatusViewSet(viewsets.ModelViewSet):
    queryset = OnlineStatus.objects.all()
    serializer_class = OnlineStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OnlineStatusFilter
