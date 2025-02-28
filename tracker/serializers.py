from rest_framework import serializers
from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus,
)


class TrackerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackerAccount
        fields = [
            'id',
            'telegram_user_id',
            'api_id',
            'api_hash',
            'is_active',
            'is_auth',
            'created_at',
            'updated_at',
        ]


class TrackerSettingSerializer(serializers.ModelSerializer):
    # Чтобы возвращать часть данных TrackerAccount, можно подключить вложенный сериализатор, но это опционально.
    tracker_account_id = serializers.PrimaryKeyRelatedField(
        source='tracker_account',
        queryset=TrackerAccount.objects.all()
    )

    class Meta:
        model = TrackerSetting
        fields = [
            'id',
            'tracker_account_id',  # вместо 'tracker_account'
            'phone_number',
            'session_string',
            'max_users',
            'current_users',
            'created_at',
            'updated_at',
        ]


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            'id',
            'telegram_user_id',
            'role',
            'current_users',
            'max_users',
            'created_at',
            'current_users',
        ]


class TrackedUserSerializer(serializers.ModelSerializer):
    # Ссылка на ID TrackerAccount
    tracker_account_id = serializers.PrimaryKeyRelatedField(
        source='tracker_account',
        queryset=TrackerAccount.objects.all()
    )
    # Ссылка на ID TelegramUser
    telegram_user_id = serializers.PrimaryKeyRelatedField(
        source='telegram_user',
        queryset=TelegramUser.objects.all()
    )

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
    # Ссылка на ID TrackedUser
    tracked_user_id = serializers.PrimaryKeyRelatedField(
        source='tracked_user',
        queryset=TrackedUser.objects.all()
    )

    class Meta:
        model = OnlineStatus
        fields = [
            'id',
            'tracked_user_id',
            'is_online',
            'created_at',
        ]
