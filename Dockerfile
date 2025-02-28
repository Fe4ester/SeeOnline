FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=SeeOnline.settings
ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000 & celery -A SeeOnline worker --loglevel=info --logfile=celery_logs.log & celery -A SeeOnline beat --loglevel=info --logfile=beat_logs.log"]