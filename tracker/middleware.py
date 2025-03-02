import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLogMiddleware(MiddlewareMixin):
    """
    Middleware для логирования всех запросов и ответов
    """

    def process_request(self, request):
        # Засекаем время начала обработки запроса
        request._start_time = time.time()
        logger.debug(
            "Incoming request: method=%s, path=%s, user=%s",
            request.method,
            request.path,
            getattr(request.user, "username", "Anonymous"),
        )

    def process_response(self, request, response):
        # Посчитаем, сколько заняло обработать запрос
        duration = 0
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time

        # Логируем "ответ"
        logger.info(
            "Response: method=%s path=%s status=%s duration=%.3fs user=%s",
            request.method,
            request.path,
            response.status_code,
            duration,
            getattr(request.user, "username", "Anonymous"),
        )

        return response
