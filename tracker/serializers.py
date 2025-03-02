import logging
from rest_framework import serializers
from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus,
)

logger = logging.getLogger(__name__)


class TrackerAccountSerializer(serializers.ModelSerializer):
    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing TrackerAccountSerializer with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackerAccount
        fields = [
            'id',
            'telegram_id',
            'api_id',
            'api_hash',
            'is_active',
            'is_auth',
            'created_at',
            'updated_at',
        ]


class TrackerSettingSerializer(serializers.ModelSerializer):
    tracker_account_id = serializers.PrimaryKeyRelatedField(
        source='tracker_account',
        queryset=TrackerAccount.objects.all()
    )

    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing TrackerSettingSerializer with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackerSetting
        fields = [
            'id',
            'tracker_account_id',
            'phone_number',
            'session_string',
            'max_users',
            'current_users',
            'created_at',
            'updated_at',
        ]


class TelegramUserSerializer(serializers.ModelSerializer):
    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing TelegramUserSerializer with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TelegramUser
        fields = [
            'id',
            'telegram_id',
            'role',
            'current_users',
            'max_users',
            'created_at',
            'updated_at',
        ]


class TrackedUserSerializer(serializers.ModelSerializer):
    tracker_account_id = serializers.PrimaryKeyRelatedField(
        source='tracker_account',
        queryset=TrackerAccount.objects.all(),
        required=False,
    )
    telegram_user_id = serializers.PrimaryKeyRelatedField(
        source='telegram_user',
        queryset=TelegramUser.objects.all()
    )

    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing TrackedUserSerializer with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackedUser
        fields = [
            'id',
            'tracker_account_id',
            'telegram_user_id',
            'username',
            'visible_online',
            'created_at',
            'updated_at',
        ]


class OnlineStatusSerializer(serializers.ModelSerializer):
    tracked_user_id = serializers.PrimaryKeyRelatedField(
        source='tracked_user',
        queryset=TrackedUser.objects.all()
    )

    # Debug - логи, полезны при отладки, для отслеживания всех действий
    def __init__(self, *args, **kwargs):
        logger.debug("Initializing OnlineStatusSerializer with args=%s, kwargs=%s", args, kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OnlineStatus
        fields = [
            'id',
            'tracked_user_id',
            'is_online',
            'created_at',
        ]
