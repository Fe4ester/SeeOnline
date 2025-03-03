# Рестовские штучки
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

# Джаговые штучки
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

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

# drf_spectacular
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Сервисные функции для перераспределения/удаления
from .services.tracker_account_service import reassign_and_delete_tracker_account
from .services.tracked_user_service import delete_tracked_user, create_tracked_user


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
        reassign_and_delete_tracker_account(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter("tg_id", type=str, description="Telegram ID трекер-аккаунта", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-telegram-id/(?P<tg_id>[^/.]+)')
    def by_telegram_id(self, request, tg_id=None):
        try:
            account = TrackerAccount.objects.get(telegram_id=tg_id)
        except TrackerAccount.DoesNotExist:
            raise NotFound("TrackerAccount with given telegram_id not found")

        if request.method == 'DELETE':
            reassign_and_delete_tracker_account(account)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    @extend_schema(
        parameters=[
            OpenApiParameter("phone", type=str, description="Phone number трекер-аккаунта", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-phone-number/(?P<phone>[^/.]+)')
    def by_phone_number(self, request, phone=None):
        try:
            setting = TrackerSetting.objects.get(phone_number=phone)
        except TrackerSetting.DoesNotExist:
            raise NotFound("TrackerSetting with given phone_number not found")

        if request.method == 'DELETE':
            setting.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter("tg_id", type=str, description="Telegram ID трекер-аккаунта", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-tracker-telegram-id/(?P<tg_id>[^/.]+)')
    def by_tracker_telegram_id(self, request, tg_id=None):
        try:
            setting = TrackerSetting.objects.get(tracker_account__telegram_id=tg_id)
        except TrackerSetting.DoesNotExist:
            raise NotFound("TrackerSetting with given tracker_account.telegram_id not found")

        if request.method == 'DELETE':
            setting.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(setting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    @extend_schema(
        parameters=[
            OpenApiParameter("tg_id", type=str, description="Telegram ID телеграм-юзера", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-telegram-id/(?P<tg_id>[^/.]+)')
    def by_telegram_id(self, request, tg_id=None):
        try:
            user = TelegramUser.objects.get(telegram_id=tg_id)
        except TelegramUser.DoesNotExist:
            raise NotFound("TelegramUser with given telegram_id not found")

        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter("role", type=str, description="Роль Телеграм-юзера", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-role/(?P<role>[^/.]+)')
    def by_role(self, request, role=None):
        """
        Массовые операции по всем пользователям с данной role.
        Осторожнее, можно снести слишком много данных.
        """
        users = TelegramUser.objects.filter(role=role)
        if not users.exists():
            raise NotFound("No TelegramUser found with this role")

        if request.method == 'DELETE':
            count = users.delete()
            return Response({"deleted_count": count[0]}, status=status.HTTP_200_OK)

        updated_data = request.data
        for user in users:
            serializer = self.get_serializer(user, data=updated_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracked_user = create_tracked_user(serializer.validated_data)
        return Response(self.get_serializer(tracked_user).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_tracked_user(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
            OpenApiParameter("uname", type=str, description="Telegram Username отслеживаемого аккаунта", location="path")
        ]
    )
    @action(detail=False, methods=['patch', 'delete'], url_path='by-username/(?P<uname>[^/.]+)')
    def by_username(self, request, uname=None):
        try:
            tracked = TrackedUser.objects.get(username=uname)
        except TrackedUser.DoesNotExist:
            raise NotFound("TrackedUser with given username not found")

        if request.method == 'DELETE':
            delete_tracked_user(tracked)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(tracked, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    @extend_schema(
        parameters=[
            OpenApiParameter("tuid", type=str, description="Telegram_user_id телеграм-юзера", location="path")
        ]
    )
    @action(detail=False, methods=['delete'], url_path='by-tracked-user-id/(?P<tuid>[^/.]+)')
    def by_tracked_user_id(self, request, tuid=None):
        statuses = OnlineStatus.objects.filter(tracked_user_id=tuid)
        if not statuses.exists():
            raise NotFound("OnlineStatus for given tracked_user_id not found")

        deleted_count = statuses.delete()
        return Response({"deleted_count": deleted_count[0]}, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter("uname", type=str, description="Юзернейм отслеживаемого аккаунта", location="path")
        ]
    )
    @action(detail=False, methods=['delete'], url_path='by-tracked-username/(?P<uname>[^/.]+)')
    def by_tracked_username(self, request, uname=None):
        statuses = OnlineStatus.objects.filter(tracked_user__username=uname)
        if not statuses.exists():
            raise NotFound("OnlineStatus not found for this username")

        deleted_count = statuses.delete()
        return Response({"deleted_count": deleted_count[0]}, status=status.HTTP_200_OK)
