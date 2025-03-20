import logging
import django_filters
from django_filters import rest_framework as filters

from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# Фильтры для TrackerAccount
# -----------------------------------------------------------
class TrackerAccountFilter(filters.FilterSet):
    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing TrackerAccountFilter with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug("Initializing TrackerSettingFilter with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug("Initializing TelegramUserFilter with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TelegramUser
        fields = {
            'id': ['exact'],
            'telegram_id': ['exact'],
            'timezone': ['exact'],
            'theme': ['exact'],
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

    def __init__(self, *args, **kwargs):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug("Initializing TrackedUserFilter with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

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
    tracked_user = django_filters.NumberFilter(field_name='tracked_user', lookup_expr='exact')
    is_online = django_filters.BooleanFilter()
    created_at = django_filters.DateTimeFromToRangeFilter()

    def __init__(self, *args, **kwargs):
        logger.debug("Initializing OnlineStatusFilter with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OnlineStatus
        fields = {
            'id': ['exact'],
            'is_online': ['exact'],
            'tracked_user': ['exact'],
        }
