import django_filters
from django_filters import rest_framework as filters

from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus
)


class TrackerAccountFilter(filters.FilterSet):
    # Пример фильтрации по булевым полям
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


class TrackerSettingFilter(filters.FilterSet):
    # Если нужно фильтровать по TrackerAccount's telegram_user_id,
    # то можно использовать метод, берущий поле через lookup:
    tracker_account__telegram_user_id = django_filters.NumberFilter()

    # Пример простой фильтрации по phone_number
    phone_number = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = TrackerSetting
        fields = {
            'id': ['exact'],
            'phone_number': ['exact', 'icontains'],
            # Можно расширять при необходимости
        }


class TelegramUserFilter(filters.FilterSet):
    # Фильтрация по роли (RoleChoices)
    role = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = TelegramUser
        fields = {
            'id': ['exact'],
            'telegram_user_id': ['exact'],
            'role': ['exact'],
        }


class TrackedUserFilter(filters.FilterSet):
    # Для фильтрации по telegram_user_id из связанной модели TelegramUser
    # можно через двойное подчеркивание: telegram_user__telegram_user_id
    telegram_user__telegram_user_id = django_filters.NumberFilter()

    # Аналогично — фильтрация по TrackerAccount.telegram_user_id (если требуется)
    tracker_account__telegram_user_id = django_filters.NumberFilter()

    class Meta:
        model = TrackedUser
        fields = {
            'id': ['exact'],
            'username': ['exact', 'icontains'],
            'visible_online': ['exact'],
            # Если надо искать точно по TelegramUser:
            # 'telegram_user__telegram_user_id': ['exact'],
        }


class OnlineStatusFilter(filters.FilterSet):
    # Фильтрация по tracked_user_id
    tracked_user_id = django_filters.NumberFilter(field_name='tracked_user__id', lookup_expr='exact')
    # Фильтрация по username через связь
    username = django_filters.CharFilter(field_name='tracked_user__username', lookup_expr='icontains')
    is_online = django_filters.BooleanFilter()

    # Фильтрация по диапазону дат (created_at)
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = OnlineStatus
        fields = {
            'id': ['exact'],
            'is_online': ['exact'],
            # created_at обрабатывается RangeFilter'ом
        }
