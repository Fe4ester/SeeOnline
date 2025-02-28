from django.contrib import admin
from .models import TrackerAccount, TrackerSetting, TelegramUser, TrackedUser, OnlineStatus


@admin.register(TrackerAccount)
class TrackerAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_user_id", "api_id", "is_active", "is_auth", "created_at", "updated_at")
    list_filter = ("is_active", "is_auth", "created_at")
    search_fields = ("telegram_user_id", "api_id")


@admin.register(TrackerSetting)
class TrackerSettingAdmin(admin.ModelAdmin):
    list_display = ("id", "tracker_account", "phone_number", "max_users", "current_users", "created_at", "updated_at")
    search_fields = ("phone_number", "tracker_account__telegram_user_id")


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_user_id", "role", "created_at", "updated_at", "max_users", "current_users")
    list_filter = ("role", "created_at", "max_users", "current_users")
    search_fields = ("telegram_user_id",)


@admin.register(TrackedUser)
class TrackedUserAdmin(admin.ModelAdmin):
    list_display = ("id", "tracker_account", "telegram_user", "username", "visible_online", "created_at", "updated_at")
    list_filter = ("visible_online", "created_at")
    search_fields = ("username", "telegram_user__telegram_user_id")


@admin.register(OnlineStatus)
class OnlineStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "tracked_user", "is_online", "created_at")
    list_filter = ("is_online", "created_at")
    search_fields = ("tracked_user__username", "tracked_user__telegram_user__telegram_user_id")
