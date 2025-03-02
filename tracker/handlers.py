import logging
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Кастомный exception handler для drf
    Логирует все исключения и формирует кастомный ответ
    """

    # Сначала используем стандартный DRF handler, для флрмирования базового ответа
    response = drf_exception_handler(exc, context)

    # обработка контекста, можно дописать свое
    view = context.get('view', None)
    request = context.get('request', None)

    # Логируем в любом случае
    logger.error(
        "Unhandled exception in %s. Exception: %s. Request data: %s",
        view.__class__.__name__ if view else 'unknown-view',
        exc,
        getattr(request, 'data', {}),
        exc_info=True  # в логи включаем выхлоп
    )

    # Если дрф не знает что за ошибка то формируется общий отет
    if response is None:
        from rest_framework.response import Response
        from rest_framework import status
        # Сформировать простейший ответ JSON
        response_data = {
            "detail": "Server Error. Something unexpected happened."
        }
        response = Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
