import django_filters
from django_filters import rest_framework as filters

from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus
)


# -----------------------------------------------------------
# Фильтры для TrackerAccount
# -----------------------------------------------------------
class TrackerAccountFilter(filters.FilterSet):
    class Meta:
        model = TrackerAccount
        fields = {
            'id': ['exact'],
            'telegram_id': ['exact'],
            'is_active': ['exact'],
            'is_auth': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для TrackerSetting
# -----------------------------------------------------------
class TrackerSettingFilter(filters.FilterSet):
    phone_number = django_filters.CharFilter(lookup_expr='exact')
    tracker_account__telegram_id = django_filters.NumberFilter()

    class Meta:
        model = TrackerSetting
        fields = {
            'id': ['exact'],
            'phone_number': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для TelegramUser
# -----------------------------------------------------------
class TelegramUserFilter(filters.FilterSet):
    class Meta:
        model = TelegramUser
        fields = {
            'id': ['exact'],
            'telegram_id': ['exact'],
            'role': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для TrackedUser
# -----------------------------------------------------------
class TrackedUserFilter(filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='exact')
    visible_online = django_filters.BooleanFilter()
    tracker_account__telegram_id = django_filters.NumberFilter()
    telegram_user__telegram_id = django_filters.NumberFilter()

    class Meta:
        model = TrackedUser
        fields = [
            'id',
            'username',
            'visible_online',
            'tracker_account__telegram_id',
            'telegram_user__telegram_id',
        ]


# -----------------------------------------------------------
# Фильтры для OnlineStatus
# -----------------------------------------------------------
class OnlineStatusFilter(filters.FilterSet):
    username = django_filters.CharFilter(field_name='tracked_user__username', lookup_expr='icontains')
    is_online = django_filters.BooleanFilter()
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OnlineStatus
        fields = {
            'id': ['exact'],
            'is_online': ['exact'],
        }
