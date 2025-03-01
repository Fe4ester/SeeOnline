from django.db import models


# -----------------------------------------------------------
# Выбор фиксированных ролей для TelegramUser
# -----------------------------------------------------------
class RoleChoices(models.TextChoices):
    BANNED = "banned", "Banned"
    USER = "user", "User"
    VIP = "vip", "VIP"
    ADMIN = "admin", "Administrator"


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram-пользователь"
        verbose_name_plural = "Telegram-пользователи"

    def __str__(self):
        return f"TelegramUser #{self.id} (tg_id={self.telegram_id}, role={self.role})"


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
        return f"OnlineStatus #{self.id} for TrackedUser #{self.tracked_user_id}"
