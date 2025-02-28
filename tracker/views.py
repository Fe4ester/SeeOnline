from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

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


class TrackerAccountViewSet(viewsets.ModelViewSet):
    queryset = TrackerAccount.objects.all()
    serializer_class = TrackerAccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerAccountFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related()
            .prefetch_related('setting')
        )


class TrackerSettingViewSet(viewsets.ModelViewSet):
    queryset = TrackerSetting.objects.select_related('tracker_account')
    serializer_class = TrackerSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerSettingFilter


class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TelegramUserFilter


class TrackedUserViewSet(viewsets.ModelViewSet):
    queryset = TrackedUser.objects.select_related('tracker_account', 'telegram_user')
    serializer_class = TrackedUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackedUserFilter


class OnlineStatusViewSet(viewsets.ModelViewSet):
    queryset = OnlineStatus.objects.select_related('tracked_user', 'tracked_user__tracker_account',
                                                   'tracked_user__telegram_user')
    serializer_class = OnlineStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OnlineStatusFilter

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
