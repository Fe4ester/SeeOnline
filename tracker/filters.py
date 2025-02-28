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
# Позволяют искать по полям is_active, is_auth и т.д.
# -----------------------------------------------------------
class TrackerAccountFilter(filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    is_auth = django_filters.BooleanFilter()

    class Meta:
        model = TrackerAccount
        fields = {
            'id': ['exact'],
            'telegram_user_id': ['exact'],
            'is_active': ['exact'],
            'is_auth': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для TrackerSetting
# Пример: фильтрация по phone_number, tracker_account__telegram_user_id
# -----------------------------------------------------------
class TrackerSettingFilter(filters.FilterSet):
    tracker_account__telegram_user_id = django_filters.NumberFilter()
    phone_number = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = TrackerSetting
        fields = {
            'id': ['exact'],
            'phone_number': ['exact', 'icontains'],
        }


# -----------------------------------------------------------
# Фильтры для TelegramUser
# Позволяют искать по роли, ID и т.д.
# -----------------------------------------------------------
class TelegramUserFilter(filters.FilterSet):
    role = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = TelegramUser
        fields = {
            'id': ['exact'],
            'telegram_user_id': ['exact'],
            'role': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для TrackedUser
# Позволяют искать по username, visible_online и т.д.
# -----------------------------------------------------------
class TrackedUserFilter(filters.FilterSet):
    telegram_user__telegram_user_id = django_filters.NumberFilter()
    tracker_account__telegram_user_id = django_filters.NumberFilter()

    class Meta:
        model = TrackedUser
        fields = {
            'id': ['exact'],
            'username': ['exact', 'icontains'],
            'visible_online': ['exact'],
        }


# -----------------------------------------------------------
# Фильтры для OnlineStatus
# Позволяют искать по is_online, username через tracked_user,
# а также по диапазону дат created_at.
# -----------------------------------------------------------
class OnlineStatusFilter(filters.FilterSet):
    tracked_user_id = django_filters.NumberFilter(field_name='tracked_user__id', lookup_expr='exact')
    username = django_filters.CharFilter(field_name='tracked_user__username', lookup_expr='icontains')
    is_online = django_filters.BooleanFilter()
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OnlineStatus
        fields = {
            'id': ['exact'],
            'is_online': ['exact'],
        }
