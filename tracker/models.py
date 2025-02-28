from django.db import models


# Базовые роли, для фиксированного количества
class RoleChoices(models.TextChoices):
    BANNED = "banned", "Banned"
    USER = "user", "User"
    VIP = "vip", "VIP"
    ADMIN = "admin", "Administrator"


class TrackerAccount(models.Model):
    telegram_user_id = models.BigIntegerField(
        unique=True
    )
    api_id = models.PositiveIntegerField(
        unique=True,
    )
    api_hash = models.CharField(
        max_length=32,
        unique=True,
    )
    is_active = models.BooleanField(
        default=False,
    )
    is_auth = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Трекер аккаунт"
        verbose_name_plural = "Трекер аккаунты"


class TrackerSetting(models.Model):
    tracker_account = models.OneToOneField(
        TrackerAccount,
        on_delete=models.CASCADE,
        related_name="setting",
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
    )
    session_string = models.TextField(
        max_length=512,
        unique=True,
        null=True,
        blank=True,
    )
    max_users = models.PositiveSmallIntegerField(
        default=0,
    )
    current_users = models.PositiveSmallIntegerField(
        default=0,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Настройки трекера"
        verbose_name_plural = "Настройки трекера"


class TelegramUser(models.Model):
    telegram_user_id = models.BigIntegerField(
        unique=True,
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
    )
    current_users = models.PositiveSmallIntegerField(
        default=0,
    )
    max_users = models.PositiveSmallIntegerField(
        default=0,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Telegram-пользователь"
        verbose_name_plural = "Telegram-пользователи"


class TrackedUser(models.Model):
    tracker_account = models.ForeignKey(
        TrackerAccount,
        on_delete=models.CASCADE,
        related_name="tracked_users",
    )
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="tracked_users",
    )
    username = models.CharField(
        max_length=32,
        unique=False,
    )
    visible_online = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Отслеживаемый пользователь"
        verbose_name_plural = "Отслеживаемые пользователи"


class OnlineStatus(models.Model):
    tracked_user = models.ForeignKey(
        TrackedUser,
        on_delete=models.CASCADE,
        related_name="online_statuses",
    )
    is_online = models.BooleanField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Статус онлайн"
        verbose_name_plural = "Статусы онлайн"
