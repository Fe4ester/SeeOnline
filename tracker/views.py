import logging

# Рестовские штучки
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

# Джаговые штучки
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

# drf_spectacular
from drf_spectacular.utils import extend_schema, extend_schema_view

# Тут и дурачку понятно
from .models import (
    TrackerAccount,
    TrackerSetting,
    TelegramUser,
    TrackedUser,
    OnlineStatus
)
from .serializers import (
    TrackerAccountSerializer,
    TrackerSettingSerializer,
    TelegramUserSerializer,
    TrackedUserSerializer,
    OnlineStatusSerializer
)
from .filters import (
    TrackerAccountFilter,
    TrackerSettingFilter,
    TelegramUserFilter,
    TrackedUserFilter,
    OnlineStatusFilter
)

# Сервисные функции для перераспределения/удаления
from .services.tracker_account_service import reassign_and_delete_tracker_account
from .services.tracked_user_service import delete_tracked_user, create_tracked_user

logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# ViewSet для TrackerAccount
# -----------------------------------------------------------
class TrackerAccountViewSet(viewsets.ModelViewSet):
    queryset = TrackerAccount.objects.all()
    serializer_class = TrackerAccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerAccountFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Переопределённый метод удаления:
        при удалении перераспределяем все TrackedUser на другой трекер (если есть слоты).
        """
        instance = self.get_object()
        logger.debug("Destroying TrackerAccount id=%s (telegram_id=%s)", instance.id, instance.telegram_id)
        reassign_and_delete_tracker_account(instance)
        logger.info("TrackerAccount id=%s deleted successfully", instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['patch', 'delete'], url_path='by-telegram-id/(?P<tg_id>[^/.]+)')
    def by_telegram_id(self, request, tg_id=None):
        logger.debug("TrackerAccountViewSet.by_telegram_id called with method=%s, tg_id=%s", request.method, tg_id)
        try:
            account = TrackerAccount.objects.get(telegram_id=tg_id)
            logger.debug("Found TrackerAccount: id=%s", account.id)
        except TrackerAccount.DoesNotExist:
            logger.warning("TrackerAccount with telegram_id=%s not found", tg_id)
            raise NotFound("TrackerAccount with given telegram_id not found")

        if request.method == 'DELETE':
            logger.debug("Deleting TrackerAccount by telegram_id=%s", tg_id)
            reassign_and_delete_tracker_account(account)
            logger.info("TrackerAccount with telegram_id=%s deleted", tg_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.save()
        logger.info("TrackerAccount with telegram_id=%s updated: id=%s", tg_id, updated_obj.id)
        return Response(serializer.data)


# -----------------------------------------------------------
# ViewSet для TrackerSetting
# -----------------------------------------------------------
class TrackerSettingViewSet(viewsets.ModelViewSet):
    queryset = TrackerSetting.objects.all()
    serializer_class = TrackerSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackerSettingFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['patch', 'delete'], url_path='by-phone-number/(?P<phone>[^/.]+)')
    def by_phone_number(self, request, phone=None):
        logger.debug("TrackerSettingViewSet.by_phone_number called with method=%s, phone=%s", request.method, phone)
        try:
            setting = TrackerSetting.objects.get(phone_number=phone)
            logger.debug("Found TrackerSetting: id=%s", setting.id)
        except TrackerSetting.DoesNotExist:
            logger.warning("TrackerSetting with phone_number=%s not found", phone)
            raise NotFound("TrackerSetting with given phone_number not found")

        if request.method == 'DELETE':
            setting.delete()
            logger.info("TrackerSetting with phone_number=%s deleted", phone)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.save()
        logger.info("TrackerSetting with phone_number=%s updated: id=%s", phone, updated_obj.id)
        return Response(serializer.data)

    @action(detail=False, methods=['patch', 'delete'], url_path='by-tracker-telegram-id/(?P<tg_id>[^/.]+)')
    def by_tracker_telegram_id(self, request, tg_id=None):
        logger.debug("TrackerSettingViewSet.by_tracker_telegram_id called with method=%s, tg_id=%s", request.method,
                     tg_id)
        try:
            setting = TrackerSetting.objects.get(tracker_account__telegram_id=tg_id)
            logger.debug("Found TrackerSetting: id=%s", setting.id)
        except TrackerSetting.DoesNotExist:
            logger.warning("TrackerSetting with tracker_account.telegram_id=%s not found", tg_id)
            raise NotFound("TrackerSetting with given tracker_account.telegram_id not found")

        if request.method == 'DELETE':
            setting.delete()
            logger.info("TrackerSetting with tracker_account.telegram_id=%s deleted", tg_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.save()
        logger.info("TrackerSetting with tracker_account.telegram_id=%s updated: id=%s", tg_id, updated_obj.id)
        return Response(serializer.data)


# -----------------------------------------------------------
# ViewSet для TelegramUser
# -----------------------------------------------------------
class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TelegramUserFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['patch', 'delete'], url_path='by-telegram-id/(?P<tg_id>[^/.]+)')
    def by_telegram_id(self, request, tg_id=None):
        logger.debug("TelegramUserViewSet.by_telegram_id called with method=%s, tg_id=%s", request.method, tg_id)
        try:
            user = TelegramUser.objects.get(telegram_id=tg_id)
            logger.debug("Found TelegramUser: id=%s", user.id)
        except TelegramUser.DoesNotExist:
            logger.warning("TelegramUser with telegram_id=%s not found", tg_id)
            raise NotFound("TelegramUser with given telegram_id not found")

        if request.method == 'DELETE':
            user.delete()
            logger.info("TelegramUser with telegram_id=%s deleted", tg_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.save()
        logger.info("TelegramUser with telegram_id=%s updated: id=%s", tg_id, updated_obj.id)
        return Response(serializer.data)

    @action(detail=False, methods=['patch', 'delete'], url_path='by-role/(?P<role>[^/.]+)')
    def by_role(self, request, role=None):
        """
        Массовые операции по всем пользователям с данной role.
        Осторожнее, можно снести слишком много данных.
        """
        logger.debug("TelegramUserViewSet.by_role called with method=%s, role=%s", request.method, role)
        users = TelegramUser.objects.filter(role=role)
        if not users.exists():
            logger.warning("No TelegramUser found with role=%s", role)
            raise NotFound("No TelegramUser found with this role")

        if request.method == 'DELETE':
            count = users.delete()
            logger.info("Deleted %s TelegramUser(s) with role=%s", count[0], role)
            return Response({"deleted_count": count[0]}, status=status.HTTP_200_OK)

        updated_data = request.data
        updated_count = 0
        for user in users:
            serializer = self.get_serializer(user, data=updated_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated_count += 1
        logger.info("Updated %s TelegramUser(s) with role=%s", updated_count, role)
        return Response({"detail": "Users updated"})


# -----------------------------------------------------------
# ViewSet для TrackedUser
# -----------------------------------------------------------
class TrackedUserViewSet(viewsets.ModelViewSet):
    queryset = TrackedUser.objects.all()
    serializer_class = TrackedUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrackedUserFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        """
        Переопределённый create для смены значений доступных и занятых ячеек
        (см. create_tracked_user в сервисном слое).
        """
        logger.debug("TrackedUserViewSet.create called with data=%s", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracked_user = create_tracked_user(serializer.validated_data)
        logger.info("Created new TrackedUser: id=%s, username=%s", tracked_user.id, tracked_user.username)
        return Response(self.get_serializer(tracked_user).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.debug("TrackedUserViewSet.destroy called for id=%s (username=%s)", instance.id, instance.username)
        delete_tracked_user(instance)
        logger.info("TrackedUser id=%s (username=%s) deleted", instance.id, instance.username)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['patch', 'delete'], url_path='by-username/(?P<uname>[^/.]+)')
    def by_username(self, request, uname=None):
        logger.debug("TrackedUserViewSet.by_username called with method=%s, username=%s", request.method, uname)
        try:
            tracked = TrackedUser.objects.get(username=uname)
            logger.debug("Found TrackedUser: id=%s", tracked.id)
        except TrackedUser.DoesNotExist:
            logger.warning("TrackedUser with username=%s not found", uname)
            raise NotFound("TrackedUser with given username not found")

        if request.method == 'DELETE':
            delete_tracked_user(tracked)
            logger.info("TrackedUser with username=%s (id=%s) deleted", uname, tracked.id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(tracked, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_obj = serializer.save()
        logger.info("TrackedUser with username=%s updated => id=%s", uname, updated_obj.id)
        return Response(serializer.data)


# -----------------------------------------------------------
# ViewSet для OnlineStatus
# -----------------------------------------------------------
class OnlineStatusViewSet(viewsets.ModelViewSet):
    queryset = OnlineStatus.objects.all()
    serializer_class = OnlineStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OnlineStatusFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['delete'], url_path='by-tracked-user-id/(?P<tuid>[^/.]+)')
    def by_tracked_user_id(self, request, tuid=None):
        logger.debug("OnlineStatusViewSet.by_tracked_user_id called with tuid=%s", tuid)
        statuses = OnlineStatus.objects.filter(tracked_user_id=tuid)
        if not statuses.exists():
            logger.warning("OnlineStatus for tracked_user_id=%s not found", tuid)
            raise NotFound("OnlineStatus for given tracked_user_id not found")

        deleted_count = statuses.delete()
        logger.info("Deleted %s OnlineStatus record(s) for tracked_user_id=%s", deleted_count[0], tuid)
        return Response({"deleted_count": deleted_count[0]}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='by-tracked-username/(?P<uname>[^/.]+)')
    def by_tracked_username(self, request, uname=None):
        logger.debug("OnlineStatusViewSet.by_tracked_username called with username=%s", uname)
        statuses = OnlineStatus.objects.filter(tracked_user__username=uname)
        if not statuses.exists():
            logger.warning("OnlineStatus not found for username=%s", uname)
            raise NotFound("OnlineStatus not found for this username")

        deleted_count = statuses.delete()
        logger.info("Deleted %s OnlineStatus record(s) for username=%s", deleted_count[0], uname)
        return Response({"deleted_count": deleted_count[0]}, status=status.HTTP_200_OK)
