import os
from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SeeOnline.settings')

app = Celery('SeeOnline')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'manager-check': {
        'task': 'tracker.tasks.check_online_manager_task',
        'schedule': settings.MANAGER_CHECK_INTERVAL,
    },
}
