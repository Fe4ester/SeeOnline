from rest_framework import serializers
from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus,
)


# -----------------------------------------------------------
# Сериализатор для TrackerAccount:
# используется для отображения и валидации данных трекер-аккаунта.
# -----------------------------------------------------------
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


# -----------------------------------------------------------
# Сериализатор для TrackerSetting:
# связанный OneToOne с TrackerAccount.
# Включает полe tracker_account_id для удобства.
# -----------------------------------------------------------
class TrackerSettingSerializer(serializers.ModelSerializer):
    # Ссылка на конкретный объект TrackerAccount
    tracker_account_id = serializers.PrimaryKeyRelatedField(
        source='tracker_account',
        queryset=TrackerAccount.objects.all()
    )

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


# -----------------------------------------------------------
# Сериализатор для TelegramUser:
# хранит информацию о самом пользователе бота (не TrackedUser).
# -----------------------------------------------------------
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
            'updated_at',
        ]


# -----------------------------------------------------------
# Сериализатор для TrackedUser:
# поля для создания и чтения TrackedUser.
# tracker_account_id не будет напрямую использоваться при создании,
# т.к. по заданию выбираем его автоматически,
# но поле оставим, чтобы его видно было при чтении/изменении.
# -----------------------------------------------------------
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


# -----------------------------------------------------------
# Сериализатор для OnlineStatus:
# фиксирует, онлайн ли пользователь в данный момент,
# и время (created_at).
# -----------------------------------------------------------
class OnlineStatusSerializer(serializers.ModelSerializer):
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
