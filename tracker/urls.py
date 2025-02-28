from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TrackerAccountViewSet,
    TrackerSettingViewSet,
    TelegramUserViewSet,
    TrackedUserViewSet,
    OnlineStatusViewSet
)

# Создаём роутер и регистрируем ViewSet'ы
router = DefaultRouter()
router.register(r'tracker-accounts', TrackerAccountViewSet, basename='trackeraccount')
router.register(r'tracker-settings', TrackerSettingViewSet, basename='trackersetting')
router.register(r'telegram-users', TelegramUserViewSet, basename='telegramuser')
router.register(r'tracked-users', TrackedUserViewSet, basename='trackeduser')
router.register(r'online-statuses', OnlineStatusViewSet, basename='onlinestatus')

urlpatterns = [
    path('', include(router.urls)),
]
