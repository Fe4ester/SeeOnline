import logging
from django.db import models

from django.utils.timezone import get_default_timezone

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# Выбор фиксированных ролей для TelegramUser
# -----------------------------------------------------------
class RoleChoices(models.TextChoices):
    BANNED = "banned", "Banned"
    USER = "user", "User"
    VIP = "vip", "VIP"
    ADMIN = "admin", "Administrator"


# -----------------------------------------------------------
# Выбор фиксированных настроек темы для TelegramUser
# -----------------------------------------------------------
class ThemeChoices(models.TextChoices):
    LIGHT = "light", "Light"
    DARK = "dark", "Dark"


# -----------------------------------------------------------
# Модель TrackerAccount
# -----------------------------------------------------------
class TrackerAccount(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    api_id = models.PositiveIntegerField(unique=True)
    api_hash = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=False)
    is_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Трекер аккаунт"
        verbose_name_plural = "Трекер аккаунты"

    def __str__(self):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug("Called __str__ on TrackerAccount: id=%s, telegram_id=%s", self.id, self.telegram_id)

        return f"TrackerAccount #{self.id} (telegram_id={self.telegram_id})"


# -----------------------------------------------------------
# Модель TrackerSetting
# -----------------------------------------------------------
class TrackerSetting(models.Model):
    tracker_account = models.OneToOneField(
        TrackerAccount,
        on_delete=models.CASCADE,
        related_name="setting",
    )
    phone_number = models.CharField(max_length=15, unique=True)
    session_string = models.TextField(max_length=512, unique=True, null=True, blank=True)
    max_users = models.PositiveSmallIntegerField(default=0)
    current_users = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки трекера"
        verbose_name_plural = "Настройки трекера"

    def __str__(self):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug(
            "Called __str__ on TrackerSetting: id=%s, tracker_account_id=%s",
            self.id, self.tracker_account_id
        )

        return f"TrackerSetting #{self.id} for TrackerAccount #{self.tracker_account_id}"


# -----------------------------------------------------------
# Модель TelegramUser
# -----------------------------------------------------------
class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
    )
    current_users = models.PositiveSmallIntegerField(default=0)
    max_users = models.PositiveSmallIntegerField(default=5)

    timezone = models.CharField(
        max_length=50,
        default=str(get_default_timezone())  # Дефолтная таймзона (можно настроить)
    )
    theme = models.CharField(
        max_length=10,
        choices=ThemeChoices.choices,
        default=ThemeChoices.LIGHT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram-пользователь"
        verbose_name_plural = "Telegram-пользователи"

    def __str__(self):
        logger.debug(
            "Called __str__ on TelegramUser: id=%s, telegram_id=%s, role=%s, timezone=%s, theme=%s",
            self.id, self.telegram_id, self.role, self.timezone, self.theme
        )
        return f"TelegramUser #{self.id} (tg_id={self.telegram_id}, role={self.role}, timezone={self.timezone}, theme={self.theme})"


# -----------------------------------------------------------
# Модель TrackedUser
# -----------------------------------------------------------
class TrackedUser(models.Model):
    tracker_account = models.ForeignKey(
        TrackerAccount,
        on_delete=models.PROTECT,
        related_name="tracked_users",
    )
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="tracked_users",
    )
    username = models.CharField(max_length=32)
    visible_online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Отслеживаемый пользователь"
        verbose_name_plural = "Отслеживаемые пользователи"

    def __str__(self):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug(
            "Called __str__ on TrackedUser: id=%s, username=%s",
            self.id, self.username
        )

        return f"TrackedUser #{self.id} (username={self.username})"


# -----------------------------------------------------------
# Модель OnlineStatus
# -----------------------------------------------------------
class OnlineStatus(models.Model):
    tracked_user = models.ForeignKey(
        TrackedUser,
        on_delete=models.CASCADE,
        related_name="online_statuses",
    )
    is_online = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Статус онлайн"
        verbose_name_plural = "Статусы онлайн"

    def __str__(self):
        # Debug - логи, полезны при отладки, для отслеживания всех действий
        logger.debug(
            "Called __str__ on OnlineStatus: id=%s, tracked_user_id=%s, is_online=%s",
            self.id, self.tracked_user_id, self.is_online
        )

        return f"OnlineStatus #{self.id} for TrackedUser #{self.tracked_user_id}"
