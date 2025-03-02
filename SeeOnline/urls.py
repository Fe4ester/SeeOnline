from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Включаем маршруты из приложения tracker
    path('', include('tracker.urls')),

    # Подключаем метрики - прометеус
    path('', include('django_prometheus.urls')),  # /metrics
    # Подключаем документацию
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
]
